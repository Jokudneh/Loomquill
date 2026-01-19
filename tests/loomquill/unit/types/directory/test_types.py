import mock

from flytekit import FlyteContext, FlyteContextManager
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile


def test_new_file_dir():
    fd = FlyteDirectory(path="s3://my-bucket")
    assert fd.sep == "/"
    inner_dir = fd.new_dir("test")
    assert inner_dir.path == "s3://my-bucket/test"
    fd = FlyteDirectory(path="s3://my-bucket/")
