import asyncio
import typing

import mock
import pytest

from flytekit.core.context_manager import FlyteContext
from flytekit.core.type_engine import (
    AsyncTypeTransformer,
    TypeEngine,
)
from flytekit.models.literals import (
    Literal,
    Primitive,
    Scalar,
)
from flytekit.models.types import LiteralType, SimpleType


class MyInt:
    def __init__(self, x: int):
        self.val = x

    def __eq__(self, other):
        if not isinstance(other, MyInt):
