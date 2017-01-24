import json
import typing
from typing import Dict

from flyteidl.core import types_pb2 as _types_pb2
from google.protobuf import json_format as _json_format
from google.protobuf import struct_pb2 as _struct

from flytekit.models import common as _common
from flytekit.models.annotation import TypeAnnotation as TypeAnnotationModel
from flytekit.models.core import types as _core_types


class SimpleType(object):
    NONE = _types_pb2.NONE
    INTEGER = _types_pb2.INTEGER
    FLOAT = _types_pb2.FLOAT
    STRING = _types_pb2.STRING
    BOOLEAN = _types_pb2.BOOLEAN
    DATETIME = _types_pb2.DATETIME
    DURATION = _types_pb2.DURATION
    BINARY = _types_pb2.BINARY
    ERROR = _types_pb2.ERROR
    STRUCT = _types_pb2.STRUCT


class SchemaType(_common.FlyteIdlEntity):
    class SchemaColumn(_common.FlyteIdlEntity):
        class SchemaColumnType(object):
            INTEGER = _types_pb2.SchemaType.SchemaColumn.INTEGER
            FLOAT = _types_pb2.SchemaType.SchemaColumn.FLOAT
            STRING = _types_pb2.SchemaType.SchemaColumn.STRING
            DATETIME = _types_pb2.SchemaType.SchemaColumn.DATETIME
            DURATION = _types_pb2.SchemaType.SchemaColumn.DURATION
            BOOLEAN = _types_pb2.SchemaType.SchemaColumn.BOOLEAN

        def __init__(self, name, type):
            """
            :param Text name: Name for the column
            :param int type: Enum type from SchemaType.SchemaColumn.SchemaColumnType representing the type of the column
            """
            self._name = name
            self._type = type

        @property
        def name(self):
            """
            Name for the column
            :rtype: Text
            """
            return self._name

        @property
        def type(self):
            """
            Enum type from SchemaType.SchemaColumn.SchemaColumnType representing the type of the column
            :rtype: int
            """
            return self._type

        def to_flyte_idl(self):
            """
            :rtype: flyteidl.core.types_pb2.SchemaType.SchemaColumn
            """
            return _types_pb2.SchemaType.SchemaColumn(name=self.name, type=self.type)

        @classmethod
        def from_flyte_idl(cls, proto):
            """
            :param flyteidl.core.types_pb2.SchemaType.SchemaColumn proto:
            :rtype: SchemaType.SchemaColumn
            """
            return cls(name=proto.name, type=proto.type)

    def __init__(self, columns):
        """
        :param list[SchemaType.SchemaColumn] columns: A list of columns defining the underlying data frame.
        """
        self._columns = columns

    @property
    def columns(self):
        """
        A list of columns defining the underlying data frame.
        :rtype: list[SchemaType.SchemaColumn]
        """
        return self._columns

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.types_pb2.SchemaType
        """
        return _types_pb2.SchemaType(columns=[c.to_flyte_idl() for c in self.columns])

    @classmethod
    def from_flyte_idl(cls, proto):
        """
        :param flyteidl.core.types_pb2.SchemaType proto:
        :rtype: SchemaType
        """
        return cls(columns=[SchemaType.SchemaColumn.from_flyte_idl(c) for c in proto.columns])


class UnionType(_common.FlyteIdlEntity):
    """
    Models _types_pb2.UnionType
    """

    def __init__(self, variants: typing.List["LiteralType"]):
        self._variants = variants

    @property
    def variants(self) -> typing.List["LiteralType"]:
        return self._variants

    def to_flyte_idl(self) -> _types_pb2.UnionType:
        return _types_pb2.UnionType(
            variants=[val.to_flyte_idl() if val else None for val in self._variants],
        )

    @classmethod
    def from_flyte_idl(cls, proto: _types_pb2.UnionType):
        return cls(variants=[LiteralType.from_flyte_idl(v) for v in proto.variants])


class TypeStructure(_common.FlyteIdlEntity):
    """
    Models _types_pb2.TypeStructure
    """

    def __init__(self, tag: str, dataclass_type: Dict[str, "LiteralType"] = None):
        self._tag = tag
        self._dataclass_type = dataclass_type

    @property
    def tag(self) -> str:
