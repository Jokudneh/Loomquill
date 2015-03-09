import os
import random
import shutil
import tempfile
from uuid import UUID
import typing
import asyncio
import fsspec
import mock
import pytest
from s3fs import S3FileSystem

from flytekit.configuration import Config, DataConfig, S3Config
from flytekit.core.context_manager import FlyteContextManager, FlyteContext
from flytekit.core.data_persistence import FileAccessProvider, get_fsspec_storage_options, s3_setup_args
from flytekit.core.type_engine import TypeEngine
from flytekit.types.directory.types import FlyteDirectory
from flytekit.types.file import FlyteFile
from flytekit.utils.asyn import loop_manager
from flytekit.models.literals import Literal
from flytekit.utils.asyn import run_sync

local = fsspec.filesystem("file")
root = os.path.abspath(os.sep)


@mock.patch("google.auth.compute_engine._metadata")  # to prevent network calls
@mock.patch("flytekit.core.data_persistence.UUID")
def test_path_getting(mock_uuid_class, mock_gcs):
    mock_uuid_class.return_value.hex = "abcdef123"

    # Testing with raw output prefix pointing to a local path
    loc_sandbox = os.path.join(root, "tmp", "unittest")
    loc_data = os.path.join(root, "tmp", "unittestdata")
    local_raw_fp = FileAccessProvider(local_sandbox_dir=loc_sandbox, raw_output_prefix=loc_data)
    r = local_raw_fp.get_random_string()
    rr = local_raw_fp.join(local_raw_fp.raw_output_prefix, r)
    assert rr == os.path.join(root, "tmp", "unittestdata", "abcdef123")
    rr = local_raw_fp.join(local_raw_fp.raw_output_prefix, r, local_raw_fp.get_file_tail("/fsa/blah.csv"))
    assert rr == os.path.join(root, "tmp", "unittestdata", "abcdef123", "blah.csv")

    # Test local path and directory
    assert local_raw_fp.get_random_local_path() == os.path.join(root, "tmp", "unittest", "local_flytekit", "abcdef123")
    assert local_raw_fp.get_random_local_path("xjiosa/blah.txt") == os.path.join(
        root, "tmp", "unittest", "local_flytekit", "abcdef123", "blah.txt"
    )
    assert local_raw_fp.get_random_local_directory() == os.path.join(
        root, "tmp", "unittest", "local_flytekit", "abcdef123"
    )

    # Recursive paths
    assert "file:///abc/happy/", "s3://my-s3-bucket/bucket1/" == local_raw_fp.recursive_paths(
        "file:///abc/happy/", "s3://my-s3-bucket/bucket1/"
    )
    assert "file:///abc/happy/", "s3://my-s3-bucket/bucket1/" == local_raw_fp.recursive_paths(
        "file:///abc/happy", "s3://my-s3-bucket/bucket1"
    )

    # Test with remote pointed to s3.
    s3_fa = FileAccessProvider(local_sandbox_dir=loc_sandbox, raw_output_prefix="s3://my-s3-bucket")
    r = s3_fa.get_random_string()
    rr = s3_fa.join(s3_fa.raw_output_prefix, r)
    assert rr == "s3://my-s3-bucket/abcdef123"
    # trailing slash should make no difference
    s3_fa = FileAccessProvider(local_sandbox_dir=loc_sandbox, raw_output_prefix="s3://my-s3-bucket/")
    r = s3_fa.get_random_string()
    rr = s3_fa.join(s3_fa.raw_output_prefix, r)
    assert rr == "s3://my-s3-bucket/abcdef123"

    # Testing with raw output prefix pointing to file://
    # Skip tests for windows
    if os.name != "nt":
        file_raw_fp = FileAccessProvider(local_sandbox_dir=loc_sandbox, raw_output_prefix="file:///tmp/unittestdata")
        r = file_raw_fp.get_random_string()
        rr = file_raw_fp.join(file_raw_fp.raw_output_prefix, r)
        rr = file_raw_fp.strip_file_header(rr)
        assert rr == os.path.join(root, "tmp", "unittestdata", "abcdef123")
        r = file_raw_fp.get_random_string()
        rr = file_raw_fp.join(file_raw_fp.raw_output_prefix, r, file_raw_fp.get_file_tail("/fsa/blah.csv"))
        rr = file_raw_fp.strip_file_header(rr)
        assert rr == os.path.join(root, "tmp", "unittestdata", "abcdef123", "blah.csv")

    g_fa = FileAccessProvider(local_sandbox_dir=loc_sandbox, raw_output_prefix="gs://my-s3-bucket/")
    r = g_fa.get_random_string()
    rr = g_fa.join(g_fa.raw_output_prefix, r)
    assert rr == "gs://my-s3-bucket/abcdef123"


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


def test_local_raw_fsspec(source_folder):
    # Test copying using raw fsspec local filesystem, should not create a nested folder
    with tempfile.TemporaryDirectory() as dest_tmpdir:
        local.put(source_folder, dest_tmpdir, recursive=True)

    new_temp_dir_2 = tempfile.mkdtemp()
    new_temp_dir_2 = os.path.join(new_temp_dir_2, "doesnotexist")
    local.put(source_folder, new_temp_dir_2, recursive=True)
    files = local.find(new_temp_dir_2)
    assert len(files) == 2


@pytest.mark.asyncio
async def test_local_provider(source_folder):
