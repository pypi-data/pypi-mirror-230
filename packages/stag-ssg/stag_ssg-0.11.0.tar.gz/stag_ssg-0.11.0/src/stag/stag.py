# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2021 Michał Góral.

from typing import Set, List, Dict

import os
import sys
import shutil
import logging
import pkgutil
import signal
import fnmatch
import glob
import threading
import webbrowser

from stag import __version__ as _version
from stag.args import ArgumentParser
from stag.config import read_config
from stag.ecs import Path
from stag.cache import clear_cache
from stag.site import Site
from stag.writing import render
from stag.server import run_server
from stag.server_helpers import open_webbrowser, get_timestamps, get_differing_files

log = logging.getLogger(__name__)

cli = ArgumentParser(description="Simply Stupid Static Site Generator")
cli.parser.set_defaults(verbosity=logging.INFO)
cli.parser.add_argument(
    "-c",
    "--config",
    nargs="?",
    default="config.toml",
    help="path to stag's configuration file",
)
cli.parser.add_argument(
    "-C",
    "--change-directory",
    metavar="DIR",
    help="run as if stag was started in DIR instead of current working directory",
)
cli.parser.add_argument(
    "-D",
    "--debug",
    action="store_const",
    const=logging.DEBUG,
    dest="verbosity",
    help="show debug messages",
)
cli.parser.add_argument("--version", action="version", version=f"%(prog)s {_version}")


def needs_full_regen(diff: Set[str], invalidate_patterns: List[str]) -> bool:
    for path in diff:
        if any(fnmatch.fnmatch(path, pat) for pat in invalidate_patterns):
            return True
    return False


def load_plugins_from(paths, disabled, *register_args):
    for finder, name, ispkg in pkgutil.iter_modules(paths):
        if name.startswith("_"):
            continue

        if name in disabled:
            continue

        found = finder.find_module(name)
        if found:
            mod = found.load_module()
            try:
                mod.register_plugin(*register_args)
                log.debug(f"Plugin loaded: {name}")
            except AttributeError as e:
                log.error(f"{e} - plugin will be disabled")


def load_plugins(site):
    search_paths = [
        os.path.join(os.path.dirname(__file__), "plugins"),
        site.config.plugins_path,
    ]

    disabled = site.config.plugins_disabled

    load_plugins_from(search_paths, disabled, site)
    site.signals.plugins_loaded.emit()


def clean_dir(root):
    try:
        files = os.scandir(root)
    except FileNotFoundError as e:
        return

    for direntry in files:
        try:
            if direntry.is_file() or direntry.is_symlink():
                os.unlink(direntry.path)
            elif direntry.is_dir():
                shutil.rmtree(direntry.path)
        except Exception as e:
            log.error("Cannot remove %s: %s", direntry.path, str(e))


def build(site):
    config = site.config

    if not os.path.isdir(config.content):
        raise IOError(
            f'Not a directory: "{config.content}" (Are you inside a correct directory? Is config.content correct?).'
        )

    log.info(f"Building site to {config.output}")

    roots = [
        config.content,
        os.path.join(config.template.name, "static"),
        "static",
    ]

    site.signals.readers_init.emit(site)

    for root in roots:
        gather_files(root, site)

    site.signals.readers_finished.emit(site)

    log.debug(f"Site has {len(site.pages)} pages")

    site.signals.processors_init.emit(site)
    site.signals.processors_finished.emit(site)

    site.signals.rendering_init.emit(site)
    clean_dir(config.output)
    os.makedirs(config.output, exist_ok=True)
    render(site)
    site.signals.rendering_finished.emit(site)

    if not config.no_cache:
        log.info("Caching results...")
        site.cache()

    site.signals.site_finished.emit(site)


@cli.arg(
    "--no-cache", action="store_const", const=True, help="don't use cached content"
)
@cli.arg("-o", "--output", help="output directory")
@cli.arg("-u", "--url", help="change configured URL of the output site")
@cli.subcommand(name="build")
def build_cmd(args):
    config = read_config(args.config)
    override_config_with_commandline_args(config, args)

    site = Site(config=config)
    load_plugins(site)
    build(site)


@cli.arg(
    "--no-cache", action="store_const", const=True, help="don't use cached content"
)
@cli.arg("-p", "--port", type=int, default="0", help="HTTP port")
@cli.arg("-o", "--output", help="output directory")
@cli.arg("-u", "--url", help="change configured URL of the output site")
@cli.arg(
    "--preserve-url",
    action="store_true",
    help="don't change configured URL to the local one",
)
@cli.subcommand(name="serve")
def serve_cmd(args):
    def _rebuild(args, changes):
        config = read_config(args.config)
        override_config_with_commandline_args(config, args)
        if not args.url and not args.preserve_url:
            config.url = ""

        site = Site(config=config)
        load_plugins(site)

        try:
            build(site)
            return config
        except Exception as e:
            log.error(e)
            log.error("Building of site failed. You may still have the old version!")
            if args.verbosity == logging.DEBUG:
                raise
            if changes == 0:
                sys.exit(1)
        return None

    def _exit(sig, frame):
        sys.exit(sig)

    signal.signal(signal.SIGINT, _exit)
    signal.signal(signal.SIGTERM, _exit)

    changes = 0
    config = _rebuild(args, changes)

    while True:
        with run_server(config.output, args.port) as server:
            needs_new_server = False
            _, port = server.get_message("address", block=True)
            # note: we're not joining this thread because we don't care
            t = threading.Thread(target=open_webbrowser, args=(port,))
            t.start()

            while not needs_new_server:
                templ = config.template.name
                patterns = [
                    "config.toml",
                    f"{config.content}/**/*",
                    f"{config.content}/**/.*",
                    f"{templ}/*",
                    f"{templ}/static/**/*",
                    "static/**/*",
                    f"{config.plugins_path}/*.py",
                    f"{config.plugins_path}/**/*.py",
                ]

                cache_invalidators = [
                    "config.toml",
                    f"{templ}/*",
                    f"{config.plugins_path}/*.py",
                    f"{config.plugins_path}/**/*.py",
                ]

                # macros may be disabled
                try:
                    if config.plugin.macros.path:
                        pat = f"{config.plugins.macros.path}/*.html"
                        patterns.append(pat)
                        cache_invalidators.append(pat)
                except AttributeError:
                    pass

                diff = set()
                oldstamps = get_timestamps(patterns)
                while True:
                    poll_delay = 1
                    server.join(poll_delay)

                    e = server.exception
                    if e:
                        log.error(e[0])
                        log.error("Critical error detected while running HTTP server.")
                        return

                    if server.exitcode is not None:
                        log.info("HTTP server terminated")
                        return

                    diff = get_differing_files(oldstamps, get_timestamps(patterns))
                    if diff:
                        log.info("")
                        log.info("Change detected, regenerating.")
                        break

                if needs_full_regen(diff, cache_invalidators):
                    read_config.cache_clear()
                    if not config.no_cache:
                        log.info("Clearing page cache.")
                        clear_cache(config.cache)

                changes += 1
                newconfig = _rebuild(args, changes)

                if newconfig.output != config.output:
                    log.info("Output directory changed. New server must be started")
                    needs_new_server = True

                config = newconfig


@cli.arg("-l", "--language", help="Page language")
@cli.arg("-u", "--url", help="Page URL")
@cli.arg("-t", "--title", help="Page title")
@cli.arg(
    "directory",
    nargs="?",
    help="directory in which stag should be initialised, defaults to the current directory",
)
@cli.subcommand(name="init")
def init_cmd(args):
    from datetime import date

    if not args.directory:
        args.directory = os.getcwd()

    def ask(question, default_answer):
        question = f"{question} [{default_answer}]: "
        resp = input(question).strip()
        return resp if resp else default_answer

    config_p = os.path.join(args.directory, "config.toml")
    index_md_p = os.path.join(args.directory, "content", "index.md")
    page_html_p = os.path.join(args.directory, "themes", "default", "page.html")

    for path in [config_p, index_md_p, page_html_p]:
        if os.path.exists(path):
            log.error(f"{path} already exists! Refusing to overwrite it.")
            return 1

    # it's ok to init in a current directory, but stag should fail if it's
    # already pre-filled with files or directories it wants to create.
    os.makedirs(os.path.dirname(config_p), exist_ok=True)
    os.makedirs(os.path.dirname(index_md_p), exist_ok=False)
    os.makedirs(os.path.dirname(page_html_p), exist_ok=False)

    # We ask interactive as late as possible because it'd be infuriating for
    # users to discard their input only because some check which stag makes fails.
    if not args.title:
        args.title = ask("Site title", "My Example Website")
    if not args.url:
        args.url = ask("Site URL", "https://example.com")
    if not args.language:
        args.language = ask("Language of the site", "en")

    page_html_templ = """
<html lang="{{ site.config.language }}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ page.md.title }} - {{ site.config.title }}</title>
</head>
<body>

<h1>{{ page.md.title }}</h1>
{% if page.md.date -%}<p><em>{{ page.md.date | strftime("%B %d, %Y") }}</em> {%- endif %}

{{ content }}

</body>
</html>""".strip()

    index_md_templ = f"""
+++
title = "My First Post"
date = {date.today()}
+++

Hello, World!""".strip()

    config_templ = f"""
title = "{args.title}"
url = "{args.url}"
language = "{args.language}"

[template]
name = "themes/default"
""".strip()

    with open(config_p, "w") as f:
        f.write(config_templ)
    with open(index_md_p, "w") as f:
        f.write(index_md_templ)
    with open(page_html_p, "w") as f:
        f.write(page_html_templ)

    log.info("Congratulations, stag site has been successfully initialised")
    log.info(f"Configuration file: {config_p}")
    log.info(f"Content directory: {os.path.dirname(index_md_p)}")
    log.info(f"Template directory: {os.path.dirname(page_html_p)}")
    log.info(f"Stag generates files to: {os.path.join(args.directory, '_output')}")
    log.info("")
    log.info("To build the site, run `stag build`.")
    log.info("To serve the site with a simple built-in HTTP server, run `stag serve`.")


def gather_files(srcdir: str, site: Site):
    for curdir, _, files in os.walk(srcdir):
        for f in files:
            path = Path(os.path.join(curdir, f), srcdir)
            relurl = site.readers.get_path(path)
            site.make_page(relurl, source=path)


def override_config_with_commandline_args(config, args):
    for name, val in args.__dict__.items():
        if val is not None and hasattr(config, name):
            setattr(config, name, args.__dict__[name])


def main_(argv):
    args = cli.parse_args(argv)
    logging.basicConfig(format="%(message)s", level=args.verbosity)

    if not hasattr(args, "func"):
        log.error("stag: missing a subcommand.")
        log.error("You can run `stag --help` to see the usage help.")
        return 1

    try:
        if args.change_directory:
            os.chdir(args.change_directory)

        return args.func(args)
    except Exception as e:
        log.error(f"Critical error: {e}")
        if args.verbosity == logging.DEBUG:
            import pdb, traceback

            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            pdb.post_mortem(tb)
            raise
        return 1


def main():
    # a hack for the tests, which call the real main_() with arbitrary set of
    # arguments
    return main_(sys.argv[1:])
