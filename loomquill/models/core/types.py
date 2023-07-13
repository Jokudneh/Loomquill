from __future__ import annotations

import typing

from flyteidl.core import types_pb2 as _types_pb2

from flytekit.models import common as _common


class EnumType(_common.FlyteIdlEntity):
    """
    Models _types_pb2.EnumType
    """

    def __init__(self, values: typing.List[str]):
        self._values = values

    @property
    def values(self) -> typing.List[str]:
        return self._values

    def to_flyte_idl(self) -> _types_pb2.EnumType:
        return _types_pb2.EnumType(
            values=self._values if self._values else [],
        )

    @classmethod
    def from_flyte_idl(cls, proto: _types_pb2.EnumType):
