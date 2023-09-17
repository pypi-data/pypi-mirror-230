from time import sleep

from stag.ecs import Path, Page, Metadata, Content
from stag.site import Site
from stag.utils import chdir

import pytest


_NO_TYPE = "_NO_TYPE"


def make_meta(*types, content=""):
    for t in types:
        if t is _NO_TYPE:
            yield Metadata()
        else:
            yield Metadata(type=t)


def make_pages(site, *metadatas):
    # not set to ease assertions
    for i, md in enumerate(metadatas):
        yield site.make_page(f"/{i}", metadata=md)


def test_page_filter_any(site):
    pages = list(
        make_pages(site, *make_meta(None, "page", "page", "post", _NO_TYPE), None)
    )
    filtered = set(site.filter_pages())
    assert filtered == set(site.pages[0:5])


def test_page_filter_none(site):
    pages = list(
        make_pages(site, *make_meta(None, "page", "page", "post", _NO_TYPE), None)
    )
    filtered = set(site.filter_pages(None))
    assert filtered == {site.pages[0]}


def test_page_filter_type(site):
    pages = list(
        make_pages(site, *make_meta(None, "page", "page", "post", _NO_TYPE), None)
    )
    filtered = set(site.filter_pages("page"))
    assert filtered == {site.pages[1], site.pages[2]}


def test_page_filter_unexisting_type(site):
    pages = list(
        make_pages(site, *make_meta(None, "page", "page", "post", _NO_TYPE), None)
    )
    filtered = set(site.filter_pages("someethingelse"))
    assert filtered == set()


def test_make_page_cache(config, build_site):
    root = build_site({"content/file.md": "**Some file**"})
    config.no_cache = False

    # let some time pass so mtimes of cache and created file will differ
    sleep(0.01)

    with chdir(root):
        s1 = Site(config=config)

        s1.make_page(
            "/file",
            source=Path(path="content/file.md", root_dir="content"),
            input=Content(type="md"),
            output=Content(type="html"),
            metadata=Metadata(),
        )
        s1.cache()

        s2 = Site(config=config)
        page = s2.make_page(
            "/file", source=Path(path="content/file.md", root_dir="content")
        )

        assert page.source is not None
        assert page.input.type == "md" is not None
        assert page.output.type == "html"
        assert page.metadata is not None
        assert page.cached is not None


def test_get_or_make_page_cache(config, build_site):
    root = build_site({"content/file.md": "**Some file**"})
    config.no_cache = False

    # let some time pass so mtimes of cache and created file will differ
    sleep(0.01)

    with chdir(root):
        s1 = Site(config=config)

        s1.get_or_make_page(
            "/file",
            source=Path(path="content/file.md", root_dir="content"),
            input=Content(type="md"),
            output=Content(type="html"),
            metadata=Metadata(),
        )
        s1.cache()

        s2 = Site(config=config)
        page = s2.get_or_make_page(
            "/file", source=Path(path="content/file.md", root_dir="content")
        )

        assert page.source is not None
        assert page.input.type == "md" is not None
        assert page.output.type == "html"
        assert page.metadata is not None
        assert page.cached is not None


def test_make_page_no_cache(config, build_site):
    root = build_site({"content/file.md": "**Some file**"})
    config.no_cache = True

    # let some time pass so mtimes of cache and created file will differ
    sleep(0.01)

    with chdir(root):
        s1 = Site(config=config)

        s1.make_page(
            "/file",
            source=Path(path="content/file.md", root_dir="content"),
            input=Content(type="md"),
            output=Content(type="html"),
            metadata=Metadata(),
        )
        s1.cache()

        s2 = Site(config=config)
        page = s2.make_page(
            "/file", source=Path(path="content/file.md", root_dir="content")
        )

        assert page.source is not None
        assert page.input is None
        assert page.output is None
        assert page.metadata is None
        assert page.cached is None


@pytest.mark.parametrize(
    "baseurl, pageurl, expected_abs, expected_path, expected_rel",
    [
        # fmt: off
        ("", "", "/", "/", "/"),
        ("", "file", "/file", "/file", "/file"),
        ("", "/file", "/file", "/file", "/file"),
        ("/", "file", "/file", "/file", "/file"),
        ("/", "/file", "/file", "/file", "/file"),
        # expected_rel below is unexpected, but logical: it is relative path
        # after the first slash
        ("/foo", "file", "/foo/file", "/file", "/foo/file"),  
        ("https://example.com", "file", "https://example.com/file", "/file", "/file"),
        ("https://example.com", "/file", "https://example.com/file", "/file", "/file"),
        ("https://example.com", "file.xml", "https://example.com/file.xml", "/file.xml", "/file.xml"),
        ("https://example.com", "/file.xml", "https://example.com/file.xml", "/file.xml", "/file.xml"),
        ("https://example.com/vhost", "file", "https://example.com/vhost/file", "/file", "/vhost/file"),
        ("https://example.com/vhost", "/file", "https://example.com/vhost/file", "/file", "/vhost/file"),
        ("https://example.com/vhost/", "file", "https://example.com/vhost/file", "/file", "/vhost/file"),
        ("https://example.com/vhost/", "/file", "https://example.com/vhost/file", "/file", "/vhost/file"),
        ("https://example.com/vhost", "dir/file", "https://example.com/vhost/dir/file", "/dir/file", "/vhost/dir/file"),
        ("https://example.com/vhost", "/dir/file", "https://example.com/vhost/dir/file", "/dir/file", "/vhost/dir/file"),
        ("https://example.com/vhost/", "dir/file", "https://example.com/vhost/dir/file", "/dir/file", "/vhost/dir/file"),
        ("https://example.com/vhost/", "/dir/file", "https://example.com/vhost/dir/file", "/dir/file", "/vhost/dir/file"),
        # fmt: on
    ],
)
def test_page_urls(config, build_site, baseurl, pageurl, expected_abs, expected_path, expected_rel):
    config.url = baseurl
    config.no_cache = True

    s = Site(config=config)
    page = s.make_page(pageurl)

    assert page.base == baseurl
    assert page.url == expected_abs
    assert page.path == expected_path
    assert page.relurl == expected_rel
