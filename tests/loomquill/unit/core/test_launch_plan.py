import typing
from collections import OrderedDict

import pytest
from flyteidl.admin import launch_plan_pb2 as _launch_plan_idl

import flytekit.configuration
from flytekit.configuration import Image, ImageConfig
from flytekit.core import launch_plan, notification
from flytekit.core.options import Options
from flytekit.core.schedule import CronSchedule
from flytekit.core.task import task
from flytekit.core.workflow import workflow
from flytekit.models.common import Annotations, AuthRole, Labels, RawOutputDataConfig
from flytekit.models.core import execution as _execution_model
from flytekit.models.core import identifier as identifier_models
from flytekit.tools.translator import get_serializable
from flytekit.models.concurrency import ConcurrencyPolicy, ConcurrencyLimitBehavior

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = flytekit.configuration.SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


# This test is used for documentation.
def test_lp_documentation():
    @task
    def t1(a: int) -> typing.NamedTuple("OutputsBC", t1_int_output=int, c=str):
        a = a + 2
        return a, "world-" + str(a)

    @workflow
    def wf(a: int, c: str) -> (int, str):
        x, y = t1(a=a)
        return x, y

    # fixed_and_default_start
    launch_plan.LaunchPlan.get_or_create(
        workflow=wf, name="your_lp_name_1", default_inputs={"a": 3}, fixed_inputs={"c": "4"}
    )
    # fixed_and_default_end

    # schedule_start
    sched = CronSchedule(schedule="*/1 * * * *", kickoff_time_input_arg="abc")
    email_notif = notification.Email(
        phases=[_execution_model.WorkflowExecutionPhase.SUCCEEDED], recipients_email=["my-team@email.com"]
    )
    launch_plan.LaunchPlan.get_or_create(
        workflow=wf, name="your_lp_name_2", schedule=sched, notifications=[email_notif]
    )
    # schedule_end

    # auth_role_start
    auth_role_model = AuthRole(assumable_iam_role="my:iam:role")
    launch_plan.LaunchPlan.get_or_create(
        workflow=wf,
        name="your_lp_name_3",
    )

    labels_model = Labels({"label": "foo"})
    annotations_model = Annotations({"annotate": "bar"})
    launch_plan.LaunchPlan.get_or_create(
        workflow=wf,
        name="your_lp_name_4",
        auth_role=auth_role_model,
        labels=labels_model,
        annotations=annotations_model,
    )

    raw_output_data_config = RawOutputDataConfig("s3://foo/output")
    launch_plan.LaunchPlan.get_or_create(
        workflow=wf, name="your_lp_name_5", raw_output_data_config=raw_output_data_config
    )
    # auth_role_end


def test_lp():
    @task
    def t1(a: int) -> typing.NamedTuple("OutputsBC", t1_int_output=int, c=str):
        a = a + 2
        return a, "world-" + str(a)

    @workflow
    def wf(a: int) -> (str, str):
        x, y = t1(a=a)
        u, v = t1(a=x)
        return y, v

    lp = launch_plan.LaunchPlan.get_or_create(wf, "get_or_create1")
    lp2 = launch_plan.LaunchPlan.get_or_create(wf, "get_or_create1")
    assert lp.name == "get_or_create1"
    assert lp is lp2

    default_lp = launch_plan.LaunchPlan.get_or_create(wf)
    default_lp2 = launch_plan.LaunchPlan.get_or_create(wf)
    assert default_lp is default_lp2

    with pytest.raises(ValueError):
        launch_plan.LaunchPlan.get_or_create(wf, default_inputs={"a": 3})

    lp_with_defaults = launch_plan.LaunchPlan.create("get_or_create2", wf, default_inputs={"a": 3})
    assert lp_with_defaults.parameters.parameters["a"].default.scalar.primitive.integer == 3


def test_lp_each_parameter():
    @task
    def t1(a: int) -> typing.NamedTuple("OutputsBC", t1_int_output=int, c=str):
        a = a + 2
        return a, "world-" + str(a)

    @workflow
