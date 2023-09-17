# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2021 Michał Góral.

from datetime import datetime

from stag.ecs import Content, Metadata
from stag.plugins._helpers import read_file


SUPPORTED_EXTENSIONS = {"xml", "json", "toml", "yaml", "yml"}
FILE_EXTENSIONS = {
    "yml": "yaml",
    "yaml": "yaml",
}


def is_raw_markup(page):
    return page.source and page.source.ext in SUPPORTED_EXTENSIONS


def is_opened_raw_markup(page):
    return page.input and page.input.type in SUPPORTED_EXTENSIONS


def get_markup_name(file_ext: str) -> str:
    return FILE_EXTENSIONS.get(file_ext, file_ext)


def read(page):
    if not is_raw_markup(page):
        return
    if page.input and page.output:  # e.g. from cache
        return

    md, cn, _ = read_file(page.source.path)
    md.setdefault("title", page.source.filebase.capitalize())
    md.setdefault("type", page.source.filebase)
    md.setdefault("date", datetime.now())
    page.metadata = Metadata(md)
    page.input = Content(get_markup_name(page.source.ext), cn)


def generate(site):
    for page in site.pages:
        if not is_opened_raw_markup(page):
            continue
        if page.output:  # e.g. from cache
            continue

        page.output = page.input.copy()


def register_plugin(site):
    site.signals.page_added.connect(read)
    site.signals.processors_init.connect(generate)
