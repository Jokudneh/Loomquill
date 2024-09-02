import click

from flytekit import task, workflow, LaunchPlan
from flytekit.clis.sdk_in_container.run import WorkflowCommand, RunLevelParams

import mock
import pytest


@task
def two_inputs(x: int, y: str) -> str:
    return f"{x},{y}"

@workflow
def two_inputs_wf(x: int, y: str) -> str:
    return two_inputs(x, y)

lp_fixed_y_default_x = LaunchPlan.get_or_create(
    workflow=two_inputs_wf,
    name="fixed-default-inputs",
    fixed_inputs={"y": "hello"},
    default_inputs={"x": 1}
)

lp_fixed_y = LaunchPlan.get_or_create(
    workflow=two_inputs_wf,
