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
