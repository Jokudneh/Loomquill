from __future__ import annotations

import datetime
import typing
from typing import Optional, Tuple, Union, cast

from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.node import Node
from flytekit.core.promise import (
    ComparisonExpression,
    ComparisonOps,
    ConjunctionExpression,
    ConjunctionOps,
    NodeOutput,
    Promise,
    VoidPromise,
    create_task_output,
)
from flytekit.models.core import condition as _core_cond
from flytekit.models.core import workflow as _core_wf
from flytekit.models.literals import Binding, BindingData, Literal, RetryStrategy
from flytekit.models.types import Error


class BranchNode(object):
    def __init__(self, name: str, ifelse_block: _core_wf.IfElseBlock):
        self._name = name
        self._ifelse_block = ifelse_block

    @property
    def name(self):
        return self._name


class ConditionalSection:
    """
    ConditionalSection is used to denote a condition within a Workflow. This default conditional section only works
    for Compilation mode. It is advised to derive the class and re-implement the `start_branch` and `end_branch` methods
    to override the compilation behavior

    > [!NOTE]
    > Conditions can only be used within a workflow context.

    Usage:

    ```python
    v =  conditional("fractions").if_((my_input > 0.1) & (my_input < 1.0)).then(...)...
    ```
    """

    def __init__(self, name: str):
        self._name = name
        self._cases: typing.List[Case] = []
        self._last_case = False
        self._condition = Condition(self)
        ctx = FlyteContextManager.current_context()
        # A new conditional section has been started, so lets push the context
        FlyteContextManager.push_context(ctx.enter_conditional_section().build())

    @property
    def name(self) -> str:
        return self._name

    @property
    def cases(self) -> typing.List[Case]:
        return self._cases

    def start_branch(self, c: Case, last_case: bool = False) -> Case:
        """
        At the start of an execution of every branch this method should be called.
        :param c: -> the case that represents this branch
        :param last_case: -> a boolean that indicates if this is the last branch in the ifelseblock
        """
        self._last_case = last_case
        self._cases.append(c)
        return self._cases[-1]

    def end_branch(self) -> Optional[Union[Condition, Promise, Tuple[Promise], VoidPromise]]:
        """
        This should be invoked after every branch has been visited.
        In case this is not local workflow execution then, we should check if this is the last case.
        If so then return the promise, else return the condition
        """
        if self._last_case:
            # We have completed the conditional section, lets pop off the branch context
            FlyteContextManager.pop_context()
            ctx = FlyteContextManager.current_context()
            # Question: This is commented out because we don't need it? Nodes created in the conditional
            #   compilation state are captured in the to_case_block? Always?
            #   Is this still true of nested conditionals? Is that why propeller compiler is complaining?
            # branch_nodes = ctx.compilation_state.nodes
            node, promises = to_branch_node(self._name, self)
            # Verify branch_nodes == nodes in bn
            bindings: typing.List[Binding] = []
            upstream_nodes = set()
            for p in promises:
                if not p.is_ready:
                    bindings.append(Binding(var=p.var, binding=BindingData(promise=p.ref)))
                    upstream_nodes.add(p.ref.node)

            n = Node(
                id=f"{ctx.compilation_state.prefix}n{len(ctx.compilation_state.nodes)}",  # type: ignore
                metadata=_core_wf.NodeMetadata(self._name, timeout=datetime.timedelta(), retries=RetryStrategy(0)),
                bindings=sorted(bindings, key=lambda b: b.var),
                upstream_nodes=list(upstream_nodes),  # type: ignore
                flyte_entity=node,
            )
            FlyteContextManager.current_context().compilation_state.add_node(n)  # type: ignore
            return self._compute_outputs(n)
        return self._condition

    def if_(self, expr: Union[ComparisonExpression, ConjunctionExpression]) -> Case:
        return self._condition._if(expr)

    def compute_output_vars(self) -> typing.Optional[typing.List[str]]:
        """
        Computes and returns the minimum set of outputs for this conditional block, based on all the cases that have
        been registered
        """
        output_vars: typing.List[str] = []
        output_vars_set = set()
        for c in self._cases:
            if c.output_promise is None and c.err is None:
                # One node returns a void output and no error, we will default to None return
                return None
            if isinstance(c.output_promise, VoidPromise):
                return None
            if c.output_promise is not None:
                var = []
                if isinstance(c.output_promise, tuple):
                    var = [i.var for i in c.output_promise]
                else:
                    var = [c.output_promise.var]
                curr_set = set(var)
                if not output_vars:
                    output_vars = var
                    output_vars_set = curr_set
                else:
