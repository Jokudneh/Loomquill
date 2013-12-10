from flyteidl.core import types_pb2 as _types_pb2

from flytekit.models.core import types as _types


def test_blob_dimensionality():
    assert _types.BlobType.BlobDimensionality.SINGLE == _types_pb2.BlobType.SINGLE
    assert _types.BlobType.BlobDimensionality.MULTIPART == _types_pb2.BlobType.MULTIPART


def test_blob_type():
    o = _types.BlobType(
