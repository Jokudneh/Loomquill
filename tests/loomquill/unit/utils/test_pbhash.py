import tempfile
import mock
import pytest
import typing
from dataclasses import dataclass, field
from google.protobuf import json_format
from google.protobuf import struct_pb2
from dataclasses_json import DataClassJsonMixin

from flyteidl.core.literals_pb2 import Blob, BlobMetadata, Literal, LiteralCollection, LiteralMap, Primitive, Scalar
from flyteidl.core.types_pb2 import BlobType
from flytekit.core.context_manager import FlyteContext, FlyteContextManager
from flytekit.core.type_engine import DataclassTransformer
from flytekit.types.file.file import FlyteFile
from flytekit.utils.pbhash import compute_hash_string


@pytest.mark.parametrize(
    "lit, expected_hash",
    [
        (
            Literal(scalar=Scalar(primitive=Primitive(integer=1))),
            "aJB6fp0kDrfAZt22e/IFnT8IJIlobjxcweiZA8I7/dA=",
        ),
        (
            Literal(collection=LiteralCollection(literals=[Literal(scalar=Scalar(primitive=Primitive(integer=1)))])),
            "qN7iA0GnbLzFGcHB7y09lbxgx+9cTIViSlyL9/kCSC0=",
        ),
        (
            Literal(map=LiteralMap(literals={"a": Literal(scalar=Scalar(primitive=Primitive(integer=1)))})),
            "JhrkdOQ+xzPVNYiKzD5sHhZprQB5Nq1GsYUVbmLAswU=",
        ),
        (
            Literal(
                scalar=Scalar(
                    blob=Blob(
                        uri="s3://my-bucket/my-key",
                        metadata=BlobMetadata(
                            type=BlobType(
                                format="PythonPickle",
