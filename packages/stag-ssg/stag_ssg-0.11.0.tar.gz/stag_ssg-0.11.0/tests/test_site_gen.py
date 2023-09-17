import os
import shutil
import json

import pytest

from stag.utils import chdir
from stag.config import read_config
from stag.signals import signals

SITES_DIR = os.path.join(os.path.dirname(__file__), "sites")
DISABLED = []


def copy_site(name, dst):
    source = os.path.join(SITES_DIR, name)
    shutil.copytree(source, dst)


def get_sites():
    _, directories, _ = next(os.walk(SITES_DIR))
    return directories


def get_files(root):
    for rd, _, fs in os.walk(root):
        for f in fs:
            yield os.path.join(rd, f)


@pytest.mark.parametrize("sitename", get_sites())
def test_site_generation(sitename, tmp_path, run_main):
    if sitename in DISABLED:
        pytest.skip(f"Disabled test for site generation: {sitename}")

    site_dir = tmp_path / sitename
    copy_site(sitename, site_dir)
    with chdir(site_dir):
        output = "_output"
        assert 0 == run_main("build", "-o", output).exitcode

        with open("expected_files.txt") as ef:
            expected_files = sorted(line.strip() for line in ef)

        generated_files = sorted(f[len(f"{output}/") :] for f in get_files(output))

        assert generated_files == expected_files


def test_site_generation_url(tmp_path, run_main):
    sitename = "site_macros"
    site_dir = tmp_path / sitename
    copy_site(sitename, site_dir)

    with chdir(site_dir):
        output = "_output"
        index = site_dir / "_output" / "index.json"

        assert 0 == run_main("build", "-o", output).exitcode
        j = json.loads(index.read_text())
        assert j["absurl"] == "https://example.com/foo.css"

        assert 0 == run_main("build", "-o", output, "-u", "https://other.example.com", "--no-cache").exitcode
        j = json.loads(index.read_text())
        assert j["absurl"] == "https://other.example.com/foo.css"
