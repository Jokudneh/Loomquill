import pytest
from flyteidl.core import catalog_pb2, errors_pb2

from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.task import task
from flytekit.core.type_engine import TypeEngine
from flytekit.core.workflow import workflow
from flytekit.models.types import LiteralType, SimpleType


def test_proto():
    @task
    def t1(in1: errors_pb2.ContainerError) -> errors_pb2.ContainerError:
        e2 = errors_pb2.ContainerError(code=in1.code, message=in1.message + "!!!", kind=in1.kind + 1)
        return e2

    @workflow
    def wf(a: errors_pb2.ContainerError) -> errors_pb2.ContainerError:
        return t1(in1=a)

    e1 = errors_pb2.ContainerError(code="test", message="hello world", kind=1)
    e_out = wf(a=e1)
    assert e_out.kind == 2
