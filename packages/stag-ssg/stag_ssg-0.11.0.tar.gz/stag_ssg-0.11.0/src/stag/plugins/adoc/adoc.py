# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2021 Michał Góral.

import asyncio
from asyncio.subprocess import PIPE
import os
import logging
import re

import attr

from stag.ecs import Content, Metadata

log = logging.getLogger(__name__)


ADOC_EXTENSIONS = {"adoc", "asc", "asciidoc"}


def read_adoc(path):
    metadata = Metadata()
    content = []

    in_tags = False
    first_not_empty_line_encountered = False
    tag_re = re.compile(r"^:(.+): *(.+)$")
    title_re = re.compile(r"^= (.+)$")

    def parse_content(line):
        nonlocal content
        content.append(line)

    def parse_frontmatter(line):
        nonlocal in_tags, step, first_not_empty_line_encountered

        content.append(line)

        if not line:
            if first_not_empty_line_encountered:
                step = parse_content
            return

        if not first_not_empty_line_encountered and (m := title_re.match(line)):
            metadata["title"] = m.group(1)
        elif m := tag_re.match(line):
            metadata[m.group(1)] = m.group(2)

        first_not_empty_line_encountered = True

    step = parse_frontmatter

    with open(path, encoding="utf-8") as fd:
        for line in fd:
            line = line.rstrip("\r\n")
            step(line)

    return metadata, "\n".join(content)


def get_process_limit():
    count = os.cpu_count()
    if count is None:
        return 2
    return count


@attr.s(auto_attribs=True)
class AsciidocConfig:
    process_limit: int = get_process_limit()


def is_adoc(page):
    return page.source and page.source.ext in ADOC_EXTENSIONS


def is_opened_md(page):
    return page.input and page.input.type == "asciidoc"


def deduce_url(path):
    if path.filebase == "index":
        return path.reldirname
    return os.path.join(path.reldirname, path.filebase)


async def asciidoctor(content):
    proc = await asyncio.create_subprocess_exec(
        "asciidoctor",
        "--no-header-footer",
        "--out-file",
        "-",
        "-",
        stdout=PIPE,
        stdin=PIPE,
    )
    stdout, _ = await proc.communicate(content.encode())
    html = stdout.decode()
    return html


async def generate_page(page):
    if "title" not in page.metadata:
        log.error("No title in %s", page.source.relpath)
        return

    html = await asciidoctor(page.input.content)
    page.output = Content("html", html)


def chunks(iterable, size):
    if size == 0:
        yield iterable
        return

    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


async def generate_async(site):
    myconfig = site.config.plugins.asciidoc

    adocs = []
    for page in site.pages:
        if not is_opened_md(page):
            continue
        if page.output:  # e.g. from cache
            continue

        adocs.append(generate_page(page))

    for chunk in chunks(adocs, myconfig.process_limit):
        await asyncio.gather(*chunk)


def read(page):
    if not is_adoc(page):
        return
    if page.input:  # e.g. from cache
        return

    metadata, content, = read_adoc(page.source.path)
    page.metadata = Metadata(metadata)
    page.input = Content("asciidoc", content)


def generate(site):
    asyncio.run(generate_async(site))


def register_plugin(site):
    site.config.update_plugin_table("asciidoc", AsciidocConfig())
    site.signals.page_added.connect(read)
    site.signals.processors_init.connect(generate)
    site.readers.register_reader(deduce_url, lambda p: p.ext in ADOC_EXTENSIONS)
