from typing import Optional

import os
import pickle
import logging
import shutil
import gzip

from stag.ecs import Page, Cache

log = logging.getLogger(__name__)


def _cache_path(path: str, cachedir: str) -> str:
    cachedir = os.path.expanduser(cachedir)
    return os.path.join(cachedir, path) + ".pickle.gzip"


def read_cache(path: str, cachedir: str) -> Optional[Page]:
    cache_path = _cache_path(path, cachedir)
    try:
        with gzip.open(cache_path, "rb") as cf:
            obj = pickle.load(cf)
            if not isinstance(obj, Page):
                log.error(f"{path}: type of cached object is incorrect")
                return None
            else:
                return obj
    except IOError:
        pass

    return None


def cache_page(page: Page, cachedir: str) -> bool:
    if not page.source:
        log.warning(f"Cannot cache virtual pages (not stored on a disk)")
        return False

    cache_path = _cache_path(page.source.path, cachedir)
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with gzip.open(cache_path, "wb") as cf:
            page.cached = Cache()
            pickle.dump(page, cf, pickle.HIGHEST_PROTOCOL)
            return True
    except Exception as e:
        log.warning(f"{page.source.path}: caching failed")
        log.debug(e)
        return False


def clear_cache(cachedir: str):
    shutil.rmtree(cachedir, ignore_errors=True)


def is_cache_valid(path: str, cachedir: str) -> bool:
    cache_path = _cache_path(path, cachedir)
    return (
        os.path.exists(cache_path)
        and os.path.exists(path)
        and os.path.getmtime(cache_path) > os.path.getmtime(path)
    )
