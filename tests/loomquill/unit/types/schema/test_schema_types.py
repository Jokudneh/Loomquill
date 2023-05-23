import sys
from datetime import datetime, timedelta

import pytest

from flytekit import kwtypes
from flytekit.core import context_manager
from flytekit.core.context_manager import ExecutionState, FlyteContextManager
from flytekit.core.type_engine import TypeEngine
from flytekit.types.schema import FlyteSchema, SchemaFormat
from flytekit.types.schema.types import FlyteSchemaTransformer


def test_typed_schema():
    s = FlyteSchema[kwtypes(x=int, y=float)]
    assert s.format() == SchemaFormat.PARQUET
    assert s.columns() == {"x": int, "y": float}


def test_assert_type():
    ctx = context_manager.FlyteContextManager.current_context()
    with context_manager.FlyteContextManager.with_context(
        ctx.with_execution_state(ctx.new_execution_state().with_params(mode=ExecutionState.Mode.TASK_EXECUTION))
