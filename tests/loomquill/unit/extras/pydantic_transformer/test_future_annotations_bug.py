"""
Test that Pydantic BaseModel works correctly with `from __future__ import annotations`.

This addresses the issue where __annotations__ contains string literals instead of
actual type objects when future annotations are enabled, which was causing Flyte
to fail to recognize standard Python types.
"""
from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field

from flytekit import task, workflow
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.type_engine import TypeEngine
from flytekit.models.types import SimpleType


# Define models at module level so they're available for get_type_hints resolution
class SimpleModel(BaseModel):
    name: str
    age: int
    height: float
    is_active: bool


class ComplexModel(BaseModel):
    tags: List[str] = Field(default_factory=lambda: ["tag1", "tag2"])
    scores: Dict[str, int] = Field(default_factory=lambda: {"math": 95, "science": 87})
    matrix: List[List[int]] = Field(default_factory=lambda: [[1, 2], [3, 4]])


class InnerModel(BaseModel):
    value: int
    label: str


