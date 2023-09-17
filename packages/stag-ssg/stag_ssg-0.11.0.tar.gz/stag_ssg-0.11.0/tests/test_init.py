import os
from io import StringIO

import pytest
import tomli

from stag.utils import chdir


def test_site_init_noninteractive(tmp_path, run_main):
    site_dir = tmp_path

    title = "some title"
    url = "https://something.example.com"
    lang = "pl"

    with chdir(site_dir):
        p = run_main("init", "-t", title, "-u", url, "-l", lang)
        assert p.exitcode == 0

        assert os.path.exists("config.toml")
        assert os.path.exists("content/index.md")
        assert os.path.exists("themes/default/page.html")

        with open("config.toml") as con:
            config_dct = tomli.loads(con.read())

        assert config_dct["title"] == title
        assert config_dct["url"] == url
        assert config_dct["language"] == lang
        assert config_dct["template"]["name"] == "themes/default"


def test_site_init_noninteractive_new_directory(tmp_path, run_main):
    site_dir = tmp_path

    title = "some title"
    url = "https://something.example.com"
    lang = "pl"
    directory = "new directory"

    with chdir(site_dir):
        assert not os.path.isdir(directory)

        p = run_main("init", directory, "-t", title, "-u", url, "-l", lang)
        assert p.exitcode == 0

        assert os.path.isdir(directory)

        with chdir(directory):
            assert os.path.exists("config.toml")
            assert os.path.exists("content/index.md")
            assert os.path.exists("themes/default/page.html")

            with open("config.toml") as con:
                config_dct = tomli.loads(con.read())

            assert config_dct["title"] == title
            assert config_dct["url"] == url
            assert config_dct["language"] == lang
            assert config_dct["template"]["name"] == "themes/default"


def test_site_init_noninteractive_refuse_when_site_exists(tmp_path, run_main):
    site_dir = tmp_path

    title = "some title"
    url = "https://something.example.com"
    lang = "pl"
    directory = "new directory"

    with chdir(site_dir):
        with open("config.toml", "w") as con:
            con.write("")

        run_main("init", "-t", title, "-u", url, "-l", lang)

        # TODO: refactor run_main, so it creates a pipe, which can return
        # main's return value (mgoral, 2022-02-02)
        assert not os.path.exists("content")
        assert not os.path.exists("themes")
