import os
import typing
from collections import OrderedDict

import mock
import pytest

import flytekit.configuration
from flytekit import task, workflow
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.condition import conditional
from flytekit.core.task import Echo
from flytekit.models.core.workflow import Node
from flytekit.tools.translator import get_serializable

default_img = Image(name="default", fqn="test", tag="tag")
serialization_settings = SerializationSettings(
    project="project",
    domain="domain",
    version="version",
    env=None,
    image_config=ImageConfig(default_image=default_img, images=[default_img]),
)


@task
def five() -> int:
    return 5


@task
def square(n: float) -> float:
    """
    Parameters:
        n (float): name of the parameter for the task will be derived from the name of the input variable
               the type will be automatically deduced to be Types.Integer

    Return:
        float: The label for the output will be automatically assigned and type will be deduced from the annotation

    """
    return n * n


@task
def double(n: float) -> float:
    """
    Parameters:
        n (float): name of the parameter for the task will be derived from the name of the input variable
               the type will be automatically deduced to be Types.Integer

    Return:
        float: The label for the output will be automatically assigned and type will be deduced from the annotation

    """
    return 2 * n


def test_condition_else_fail():
    @workflow
    def multiplier_2(my_input: float) -> float:
        return (
            conditional("fractions")
            .if_((my_input > 0.1) & (my_input < 1.0))
            .then(double(n=my_input))
            .elif_((my_input > 1.0) & (my_input < 10.0))
            .then(square(n=my_input))
            .else_()
            .fail("The input must be between 0 and 10")
        )

    with pytest.raises(ValueError):
        multiplier_2(my_input=10.0)


def test_condition_else_int():
    @workflow
    def multiplier_3(my_input: int) -> float:
        return (
            conditional("fractions")
            .if_((my_input >= 0) & (my_input < 1.0))
            .then(double(n=my_input))
            .elif_((my_input > 1.0) & (my_input < 10.0))
            .then(square(n=my_input))
            .else_()
            .fail("The input must be between 0 and 10")
        )

    assert multiplier_3(my_input=0) == 0


def test_condition_sub_workflows():
    @task
    def sum_div_sub(a: int, b: int) -> typing.NamedTuple("Outputs", sum=int, div=int, sub=int):
        return a + b, a / b, a - b

    @task
    def sum_sub(a: int, b: int) -> typing.NamedTuple("Outputs", sum=int, sub=int):
        return a + b, a - b

    @workflow
    def sub_wf(a: int, b: int) -> typing.Tuple[int, int]:
        return sum_sub(a=a, b=b)

