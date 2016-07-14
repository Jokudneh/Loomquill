import importlib
import io
import os
import pathlib
import random
import string
import sys
import tempfile

import fsspec
import mock
import pytest
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from mock import AsyncMock

from flytekit.configuration import Config
from flytekit.core.data_persistence import FileAccessProvider, get_additional_fsspec_call_kwargs
from flytekit.core.local_fsspec import FlyteLocalFileSystem


def test_get_manual_random_remote_path():
    fp = FileAccessProvider("/tmp", "s3://my-bucket")
    path = fp.join(fp.raw_output_prefix, fp.get_random_string())
    assert path.startswith("s3://my-bucket")
    assert fp.raw_output_prefix == "s3://my-bucket/"


def test_is_remote():
    fp = FileAccessProvider("/tmp", "s3://my-bucket")
    assert fp.is_remote("./checkpoint") is False
    assert fp.is_remote("/tmp/foo/bar") is False
    assert fp.is_remote("file://foo/bar") is False
    assert fp.is_remote("s3://my-bucket/foo/bar") is True


@pytest.mark.skipif("pandas" not in sys.modules, reason="Pandas is not installed.")
@mock.patch("flytekit.core.data_persistence.UUID")
def test_write_folder_put_raw(mock_uuid_class):
    import pandas as pd

    """
    A test that writes this structure
    raw/
        foo/
            a.txt
        <rand>/
            bar/
                00000
        baz/
            00000
            <a.txt but called something random>
        pd.parquet
    """
    mock_uuid_class.return_value.hex = "abcdef123"
    random_dir = tempfile.mkdtemp()
    raw = os.path.join(random_dir, "raw")
    fs = FileAccessProvider(local_sandbox_dir=random_dir, raw_output_prefix=raw)

    sio = io.StringIO()
    sio.write("hello world")
    sio.seek(0)

    bio = io.BytesIO()
    bio.write(b"hello world bytes")

    bio2 = io.BytesIO()
    df = pd.DataFrame({"name": ["Tom", "Joseph"], "age": [20, 22]})
    df.to_parquet(bio2, engine="pyarrow")

    # Write foo/a.txt by specifying the upload prefix and a file name
    fs.put_raw_data(sio, upload_prefix="foo", file_name="a.txt")

    # Write bar/00000 by specifying the folder in the filename
    fs.put_raw_data(bio, file_name="bar/00000")

    # Write pd.parquet and baz by specifying an empty string upload prefix
    fs.put_raw_data(bio2, upload_prefix="", file_name="pd.parquet")
    fs.put_raw_data(bio, upload_prefix="", file_name="baz/00000")

    # Write sio again with known folder but random file name
    fs.put_raw_data(sio, upload_prefix="baz")

    paths = [str(p) for p in pathlib.Path(raw).rglob("*")]
    assert len(paths) == 9
    expected = [
        os.path.join(raw, "pd.parquet"),
        os.path.join(raw, "foo"),
        os.path.join(raw, "baz"),
        os.path.join(raw, "abcdef123"),
        os.path.join(raw, "foo", "a.txt"),
        os.path.join(raw, "baz", "00000"),
        os.path.join(raw, "baz", "abcdef123"),
