import asyncio
from flytekit.core.artifact import Artifact
from dataclasses import dataclass
from typing import List, Optional, TypeVar, Type, Tuple, Union

from pydantic import BaseModel
from typing_extensions import Annotated

from flytekit import task
from flytekit import workflow
from flytekit.configuration import SerializationSettings, ImageConfig, Image
from flytekit.core.context_manager import FlyteContext
from flytekit.core.context_manager import FlyteContextManager, ExecutionState
from flytekit.core.dynamic_workflow_task import dynamic
from flytekit.core.type_engine import SimpleTransformer
from flytekit.core.type_engine import TypeEngine, AsyncTypeTransformer, TypeTransformerFailedError
from flytekit.models import types as type_models
from flytekit.models.literals import Literal, LiteralCollection, Primitive, Scalar, LiteralMap
from flytekit.models.types import LiteralType
from flytekit.types.pickle.pickle import FlytePickleTransformer

ss = SerializationSettings(
    project="test_proj",
    domain="test_domain",
    version="abc",
    image_config=ImageConfig(Image(name="name", fqn="image", tag="name")),
    env={},
)

T = TypeVar("T")


def test_cross_type_binding_no_literals():
    @dataclass
    class DataShard:
        # Path to the data shard.
        path: str
        # Checksum of the data shard.
        checksum: str

    PackagedList = Annotated[list[DataShard], FlytePickleTransformer()]
    ParentList = list[PackagedList]

    def gen_foo(batch_size: int) -> ParentList:
        d1 = [DataShard(path="some/path", checksum="some check")] * 30
        return [d1[i:i + batch_size] for i in range(0, len(d1), batch_size)]

    @dynamic
    def d0(ii: ParentList) -> None:
        for idx, l in enumerate(ii):
            print(f"List {idx}: {l}")
            t0(ii=ii)

    @task
    def t0(ii: PackagedList) -> None:
        for shard in ii:
            print(f"Shard: {shard}")

    foofoo = gen_foo(batch_size=10)

    with FlyteContextManager.with_context(
        FlyteContextManager.current_context().with_serialization_settings(ss)
    ) as ctx:
        new_exc_state = ctx.execution_state.with_params(mode=ExecutionState.Mode.TASK_EXECUTION)
        with FlyteContextManager.with_context(ctx.with_execution_state(new_exc_state)):
            dynamic_job_spec = d0.compile_into_workflow(ctx, d0._task_function, ii=foofoo)
            assert len(dynamic_job_spec.nodes) == 3
            for nn in dynamic_job_spec.nodes:
                assert len(nn.inputs) == 1
                assert nn.inputs[0].var == "ii"
                assert nn.inputs[0].binding.scalar.blob is not None

    @workflow
    def wf(ii: ParentList):
        d0(ii=ii)

    wf(ii=foofoo)


def test_cross_type_binding_no_literals_parent():
    @dataclass
    class DataShard:
        # Path to the data shard.
        path: str
        # Checksum of the data shard.
        checksum: str

    pt = FlytePickleTransformer()
    ParentList = list[Annotated[list[Annotated[DataShard, pt]], pt]]

    def gen_foo(batch_size: int) -> ParentList:
        d1 = [DataShard(path="some/path", checksum="some check")] * 30
        return [d1[i:i + batch_size] for i in range(0, len(d1), batch_size)]

    @dynamic
    def d0(ii: ParentList) -> None:
        t0(ii=ii)

    @task
    def t0(ii: ParentList) -> None:
        for shard in ii:
            print(f"Shard: {shard}")

    foofoo = gen_foo(batch_size=10)

    with FlyteContextManager.with_context(
        FlyteContextManager.current_context().with_serialization_settings(ss)
    ) as ctx:
        new_exc_state = ctx.execution_state.with_params(mode=ExecutionState.Mode.TASK_EXECUTION)
        with FlyteContextManager.with_context(ctx.with_execution_state(new_exc_state)):
