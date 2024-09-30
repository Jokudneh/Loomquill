import datetime
from datetime import timezone

import pytest

from flytekit.models import common as _common_models
from flytekit.models import execution as _execution
from flytekit.models import literals as _literals
from flytekit.models.core import execution as _core_exec
from flytekit.models.core import identifier as _identifier
from tests.flytekit.common import parameterizers as _parameterizers

_INPUT_MAP = _literals.LiteralMap(
    {"a": _literals.Literal(scalar=_literals.Scalar(primitive=_literals.Primitive(integer=1)))}
)
_OUTPUT_MAP = _literals.LiteralMap(
    {"b": _literals.Literal(scalar=_literals.Scalar(primitive=_literals.Primitive(integer=2)))}
)


def test_execution_closure_with_output():
    test_datetime = datetime.datetime(year=2022, month=1, day=1, tzinfo=timezone.utc)
    test_timedelta = datetime.timedelta(seconds=10)
    test_outputs = _execution.LiteralMapBlob(values=_OUTPUT_MAP, uri="http://foo/")

    obj = _execution.ExecutionClosure(
        phase=_core_exec.WorkflowExecutionPhase.SUCCEEDED,
        started_at=test_datetime,
        duration=test_timedelta,
        outputs=test_outputs,
        created_at=None,
        updated_at=test_datetime,
    )
    assert obj.phase == _core_exec.WorkflowExecutionPhase.SUCCEEDED
    assert obj.started_at == test_datetime
    assert obj.duration == test_timedelta
    assert obj.outputs == test_outputs
    obj2 = _execution.ExecutionClosure.from_flyte_idl(obj.to_flyte_idl())
    assert obj2 == obj
    assert obj2.phase == _core_exec.WorkflowExecutionPhase.SUCCEEDED
    assert obj2.started_at == test_datetime
    assert obj2.duration == test_timedelta
    assert obj2.outputs == test_outputs
    assert obj2.created_at is None
    assert obj2.updated_at == test_datetime


def test_execution_closure_with_error():
    test_datetime = datetime.datetime(year=2022, month=1, day=1, tzinfo=timezone.utc)
    test_timedelta = datetime.timedelta(seconds=10)
    test_error = _core_exec.ExecutionError(
        code="foo", message="bar", error_uri="http://foobar", kind=_core_exec.ExecutionError.ErrorKind.USER
    )

    obj = _execution.ExecutionClosure(
        phase=_core_exec.WorkflowExecutionPhase.SUCCEEDED,
        started_at=test_datetime,
        duration=test_timedelta,
        error=test_error,
        created_at=test_datetime,
        updated_at=None,
    )
    assert obj.phase == _core_exec.WorkflowExecutionPhase.SUCCEEDED
    assert obj.started_at == test_datetime
    assert obj.duration == test_timedelta
    assert obj.error == test_error
    obj2 = _execution.ExecutionClosure.from_flyte_idl(obj.to_flyte_idl())
    assert obj2 == obj
    assert obj2.phase == _core_exec.WorkflowExecutionPhase.SUCCEEDED
    assert obj2.started_at == test_datetime
    assert obj2.created_at == test_datetime
    assert obj2.updated_at is None
    assert obj2.duration == test_timedelta
    assert obj2.error == test_error


def test_execution_closure_with_abort_metadata():
    test_datetime = datetime.datetime(year=2022, month=1, day=1, tzinfo=timezone.utc)
    test_timedelta = datetime.timedelta(seconds=10)
    abort_metadata = _execution.AbortMetadata(cause="cause", principal="skinner")

    obj = _execution.ExecutionClosure(
        phase=_core_exec.WorkflowExecutionPhase.SUCCEEDED,
        started_at=test_datetime,
        duration=test_timedelta,
        abort_metadata=abort_metadata,
