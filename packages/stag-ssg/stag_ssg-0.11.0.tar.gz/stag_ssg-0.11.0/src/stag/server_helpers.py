# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2021 Michał Góral.

from typing import Dict, Set

import os
import webbrowser
import glob


def open_webbrowser(port: int):
    url = f"http://localhost:{port}"
    webbrowser.open_new_tab(url)


def get_timestamps(watch_patterns):
    stamps = {}
    for pat in watch_patterns:
        for path in glob.iglob(pat, recursive=True):
            mtime = os.stat(path).st_mtime
            stamps[path] = mtime
    return stamps


def get_differing_files(
    stamps: Dict[str, float], newstamps: Dict[str, float]
) -> Set[str]:
    stamps_set = set(stamps.items())
    newstamps_set = set(newstamps.items())
    diff = set.symmetric_difference(stamps_set, newstamps_set)
    return set(k for k, _ in diff)
