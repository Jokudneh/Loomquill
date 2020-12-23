import pytest
from flyteidl.core import types_pb2

from flytekit.models import types as _types
from flytekit.models.annotation import TypeAnnotation
from tests.flytekit.common import parameterizers


def test_simple_type():
    assert _types.SimpleType.NONE == types_pb2.NONE
    assert _types.SimpleType.INTEGER == types_pb2.INTEGER
    assert _types.SimpleType.FLOAT == types_pb2.FLOAT
    assert _types.SimpleType.STRING == types_pb2.STRING
    assert _types.SimpleType.BOOLEAN == types_pb2.BOOLEAN
    assert _types.SimpleType.DATETIME == types_pb2.DATETIME
    assert _types.SimpleType.DURATION == types_pb2.DURATION
    assert _types.SimpleType.BINARY == types_pb2.BINARY
    assert _types.SimpleType.ERROR == types_pb2.ERROR


def test_schema_column():
    assert _types.SchemaType.SchemaColumn.SchemaColumnType.INTEGER == types_pb2.SchemaType.SchemaColumn.INTEGER
    assert _types.SchemaType.SchemaColumn.SchemaColumnType.FLOAT == types_pb2.SchemaType.SchemaColumn.FLOAT
    assert _types.SchemaType.SchemaColumn.SchemaColumnType.STRING == types_pb2.SchemaType.SchemaColumn.STRING
    assert _types.SchemaType.SchemaColumn.SchemaColumnType.DATETIME == types_pb2.SchemaType.SchemaColumn.DATETIME
    assert _types.SchemaType.SchemaColumn.SchemaColumnType.DURATION == types_pb2.SchemaType.SchemaColumn.DURATION
    assert _types.SchemaType.SchemaColumn.SchemaColumnType.BOOLEAN == types_pb2.SchemaType.SchemaColumn.BOOLEAN


def test_schema_type():
    obj = _types.SchemaType(
        [
            _types.SchemaType.SchemaColumn("a", _types.SchemaType.SchemaColumn.SchemaColumnType.INTEGER),
            _types.SchemaType.SchemaColumn("b", _types.SchemaType.SchemaColumn.SchemaColumnType.FLOAT),
            _types.SchemaType.SchemaColumn("c", _types.SchemaType.SchemaColumn.SchemaColumnType.STRING),
            _types.SchemaType.SchemaColumn("d", _types.SchemaType.SchemaColumn.SchemaColumnType.DATETIME),
            _types.SchemaType.SchemaColumn("e", _types.SchemaType.SchemaColumn.SchemaColumnType.DURATION),
            _types.SchemaType.SchemaColumn("f", _types.SchemaType.SchemaColumn.SchemaColumnType.BOOLEAN),
        ]
    )

