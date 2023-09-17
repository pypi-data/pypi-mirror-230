from typing import Mapping

import os
import sys
from multiprocessing import Process

import pytest

from stag.config import Config
from stag.site import Site
from stag.stag import main_


sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def site(config):
    site = Site(config=config)
    return site


@pytest.fixture
def build_site(tmp_path):
    def builder(paths: Mapping[str, str]) -> str:
        for path, contents in paths.items():
            directory = os.path.dirname(path)
            file = os.path.basename(path)

            if directory:
                os.makedirs(os.path.join(tmp_path, directory), exist_ok=True)

            with open(os.path.join(tmp_path, directory, file), "w") as f:
                f.write(contents + os.linesep)
        return tmp_path

    return builder


@pytest.fixture
def run_main():
    def run_fn(*args, **kwargs):
        # Use multiprocessing to sandbox each function call from each other.
        # Things which have global state which might need clearing include, but
        # are not limited to:
        #   - cached read_config()
        #   - global signals
        #   - loaded plugins (this is the tough one)
        p = Process(target=main_, args=(args,), kwargs=kwargs)
        p.start()
        p.join()
        return p

    return run_fn
