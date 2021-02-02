import os
import pathlib
import shutil
import tempfile
from base64 import b64encode

import fsspec
import pytest
from fsspec.implementations.http import HTTPFileSystem

from flytekit.configuration import Config
from flytekit.core.data_persistence import FileAccessProvider
from flytekit.remote.remote import FlyteRemote
from flytekit.remote.remote_fs import FlyteFS

local = fsspec.filesystem("file")


@pytest.fixture
def source_folder():
    # Set up source directory for testing
    parent_temp = tempfile.mkdtemp()
    src_dir = os.path.join(parent_temp, "source", "")
    nested_dir = os.path.join(src_dir, "nested")
    local.mkdir(nested_dir)
    local.touch(os.path.join(src_dir, "original.txt"))
    with open(os.path.join(src_dir, "original.txt"), "w") as fh:
        fh.write("hello original")
    local.touch(os.path.join(nested_dir, "more.txt"))
    yield src_dir
    shutil.rmtree(parent_temp)


def test_basics():
    r = FlyteRemote(
        Config.for_sandbox(),
        default_project="flytesnacks",
        default_domain="development",
