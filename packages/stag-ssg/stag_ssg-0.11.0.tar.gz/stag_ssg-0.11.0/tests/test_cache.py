import os
import pathlib
from time import sleep

from stag.cache import cache_page, read_cache, is_cache_valid, clear_cache
from stag.ecs import Path, Page, Content
from stag.utils import chdir


def test_cache_page(build_site):
    root = build_site({"content/file.md": ""})
    page = Page("", "/file", source=Path(path="content/file.md", root_dir="content"))

    with chdir(root):
        assert cache_page(page, ".cache")
        assert os.path.isfile(".cache/content/file.md.pickle.gzip")


def test_dont_cache_virtual_page(build_site):
    root = build_site({"content/file.md": ""})
    page = Page("", "/vfile")

    with chdir(root):
        assert not cache_page(page, ".cache")
        assert not os.path.exists(".cache")


def test_clear_cache(build_site):
    root = build_site({"content/file.md": ""})
    page = Page("", "/file", source=Path(path="content/file.md", root_dir="content"))

    with chdir(root):
        cache_page(page, ".cache")
        assert os.path.isdir(".cache")

        clear_cache(".cache")
        assert not os.path.exists(".cache")


def test_read_cache(build_site):
    root = build_site({"content/file.md": ""})
    page = Page(
        "",
        "/file",
        source=Path(path="content/file.md", root_dir="content"),
        input=Content(type="md"),
    )

    with chdir(root):
        cache_page(page, ".cache")

        from_cache = read_cache("content/file.md", ".cache")
        assert from_cache
        assert from_cache.source == page.source
        assert from_cache.input == page.input
        assert from_cache.cached is not None


def test_read_cache_missing_file(build_site):
    root = build_site({"content/file.md": ""})
    page = Page(
        "",
        "/file",
        source=Path(path="content/file.md", root_dir="content"),
        input=Content(type="md"),
    )

    with chdir(root):
        cache_page(page, ".cache")
        assert read_cache("content/otherfile.md", ".cache") is None


def test_read_cache_missing_cache(build_site):
    root = build_site({"content/file.md": ""})

    with chdir(root):
        assert read_cache("content/otherfile.md", ".cache") is None


def test_is_cache_valid(build_site):
    root = build_site({"content/file.md": ""})
    page = Page("", "/file", source=Path(path="content/file.md", root_dir="content"))

    # let some time pass so mtimes of cache and created file will differ
    sleep(0.01)

    with chdir(root):
        assert cache_page(page, ".cache")
        assert is_cache_valid("content/file.md", ".cache")


def test_is_cache_valid_file_update(build_site):
    root = build_site({"content/file.md": ""})
    page = Page("", "/file", source=Path(path="content/file.md", root_dir="content"))

    # let some time pass so mtimes of cache and created file will differ
    sleep(0.01)

    with chdir(root):
        assert cache_page(page, ".cache")

        # update original file mtime
        sleep(0.01)
        pathlib.Path(os.path.join(root, page.source.path)).touch()
        assert not is_cache_valid("content/file.md", ".cache")


def test_is_cache_valid_no_file(build_site):
    root = build_site({"content/file.md": ""})
    page = Page("", "/file", source=Path(path="content/file.md", root_dir="content"))

    # let some time pass so mtimes of cache and created file will differ
    sleep(0.01)

    with chdir(root):
        cache_page(page, ".cache")
        assert not is_cache_valid("content/otherfile.md", ".cache")


def test_is_cache_valid_no_cache(build_site):
    root = build_site({"content/file.md": ""})

    # let some time pass so mtimes of cache and created file will differ
    sleep(0.01)

    with chdir(root):
        assert not is_cache_valid("content/otherfile.md", ".cache")
