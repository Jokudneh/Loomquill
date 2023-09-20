import collections
import typing

from typing_extensions import get_args

from flytekit import FlyteContext, Literal, LiteralType
from flytekit.core.type_engine import TypeEngine, TypeTransformer, TypeTransformerFailedError
from flytekit.models import types as _type_models
from flytekit.models.literals import LiteralCollection

T = typing.TypeVar("T")


class FlyteIterator:
    def __init__(self, ctx: FlyteContext, lv: Literal, expected_python_type: typing.Type[T], length: int):
        self._ctx = ctx
        self._lv = lv
        self._expected_python_type = expected_python_type
        self._length = length
        self._index = 0

    def __len__(self):
        return self._length

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < self._length:
