import sys
import typing
from dataclasses import dataclass
from typing import Dict, List

import pytest
from dataclasses_json import DataClassJsonMixin, dataclass_json
from typing_extensions import Annotated

from flytekit import LaunchPlan, task, workflow
from flytekit.core import context_manager
from flytekit.core.context_manager import CompilationState, FlyteContextManager
from flytekit.core.promise import (
    Promise,
    VoidPromise,
    binding_data_from_python_std,
    create_and_link_node,
    create_and_link_node_from_remote,
    resolve_attr_path_in_promise,
    translate_inputs_to_literals,
)
from flytekit.core.type_engine import TypeEngine
from flytekit.exceptions.user import FlyteAssertion, FlytePromiseAttributeResolveException
from flytekit.models import literals as literal_models
from flytekit.models.types import LiteralType, SimpleType, TypeStructure


def test_create_and_link_node():
    @task
    def t1(a: typing.Union[int, typing.List[int]]) -> typing.Union[int, typing.List[int]]:
        return a

    with pytest.raises(FlyteAssertion, match="Cannot create node when not compiling..."):
        ctx = context_manager.FlyteContext.current_context()
        create_and_link_node(ctx, t1, a=3)

    ctx = context_manager.FlyteContext.current_context().with_compilation_state(CompilationState(prefix=""))
    p = create_and_link_node(ctx, t1, a=3)
    assert p.ref.node_id == "n0"
    assert p.ref.var == "o0"
    assert len(p.ref.node.bindings) == 1
    assert len(ctx.compilation_state.nodes) == 1

    @task
    def t2(a: typing.Optional[int] = None) -> typing.Optional[int]:
        return a

    ctx = context_manager.FlyteContext.current_context().with_compilation_state(CompilationState(prefix=""))
    p = create_and_link_node(ctx, t2)
    assert p.ref.var == "o0"
    assert len(p.ref.node.bindings) == 1
    assert len(ctx.compilation_state.nodes) == 1

    ctx = context_manager.FlyteContext.current_context().with_compilation_state(CompilationState(prefix=""))
    p = create_and_link_node(ctx, t2, add_node_to_compilation_state=False)
    assert p.ref.var == "o0"
    assert len(p.ref.node.bindings) == 1
    assert len(ctx.compilation_state.nodes) == 0


def test_create_and_link_node_from_remote():
    @task
    def t1() -> None:
        ...

    with pytest.raises(FlyteAssertion, match="Cannot create node when not compiling..."):
        ctx = context_manager.FlyteContext.current_context()
        create_and_link_node_from_remote(ctx, t1, a=3)

    ctx = context_manager.FlyteContext.current_context().with_compilation_state(CompilationState(prefix=""))
    p = create_and_link_node_from_remote(ctx, t1)
    assert p.ref.node_id == "n0"
    assert p.ref.var == "placeholder"
    assert len(p.ref.node.bindings) == 0

    @task
    def t2(a: int) -> int:
        return a

    ctx = context_manager.FlyteContext.current_context().with_compilation_state(CompilationState(prefix=""))
    p = create_and_link_node_from_remote(ctx, t2, a=3)
    assert p.ref.var == "o0"
    assert len(p.ref.node.bindings) == 1
    assert len(ctx.compilation_state.nodes) == 1

    ctx = context_manager.FlyteContext.current_context().with_compilation_state(CompilationState(prefix=""))
    p = create_and_link_node_from_remote(ctx, t2, add_node_to_compilation_state=False, a=3)
    assert p.ref.var == "o0"
    assert len(p.ref.node.bindings) == 1
    assert len(ctx.compilation_state.nodes) == 0


def test_create_and_link_node_from_remote_ignore():
    @workflow
    def wf(i: int, j: int):
        ...

    lp = LaunchPlan.get_or_create(wf, name="promise-test", fixed_inputs={"i": 1}, default_inputs={"j": 10})
    lp_without_fixed_inpus = LaunchPlan.get_or_create(
        wf, name="promise-test-no-fixed", fixed_inputs=None, default_inputs={"j": 10}
    )
    ctx = context_manager.FlyteContext.current_context().with_compilation_state(CompilationState(prefix=""))

    # without providing the _inputs_not_allowed or _ignorable_inputs, all inputs to lp become required,
    # which is incorrect
    with pytest.raises(
        FlyteAssertion,
        match=r"Missing input `i` type `Flyte Serialized object \(LiteralType\):",
    ):
        create_and_link_node_from_remote(ctx, lp)

    # Even if j is not provided, it will default
    create_and_link_node_from_remote(ctx, lp, _inputs_not_allowed={"i"}, _ignorable_inputs={"j"})

    # Even if i,j is not provided, it will default
    create_and_link_node_from_remote(
        ctx, lp_without_fixed_inpus, _inputs_not_allowed=None, _ignorable_inputs={"i", "j"}
