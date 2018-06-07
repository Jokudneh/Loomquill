"""Tests for custom TypeTransformer schema_match in nested Pydantic models.

Verifies that when a custom type with a registered TypeTransformer (implementing
schema_match) is nested inside a Pydantic BaseModel, guess_python_type correctly
reconstructs the custom type instead of building a generic dataclass.
"""

import dataclasses
import typing

import pytest
from pydantic import BaseModel

from flytekit.core.context_manager import FlyteContext
from flytekit.core.type_engine import TypeEngine, TypeTransformer, _match_registered_type_from_schema
from flytekit.models.literals import Literal
from flytekit.models.types import LiteralType, SimpleType

# -- Custom type and transformer --


class Coordinate(BaseModel):
    x: float
    y: float


class CoordinateTransformer(TypeTransformer[Coordinate]):
    """A transformer for Coordinate —
    Coordinate is a BaseModel and the default auto-matches."""

    def __init__(self):
        super().__init__("Coordinate", Coordinate)

    def get_literal_type(self, t=None) -> LiteralType:
        return LiteralType(simple=SimpleType.STRUCT)

    def to_literal(self, ctx, python_val, python_type, expected) -> Literal:
        raise NotImplementedError

    def to_python_value(self, ctx, lv, expected_python_type):
        raise NotImplementedError


# -- Models using Coordinate --


