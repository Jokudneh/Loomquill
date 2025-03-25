from __future__ import annotations

import datetime
import typing
from typing import Tuple, Union

import click

from flytekit.core import constants
from flytekit.core import interface as flyte_interface
from flytekit.core.context_manager import ExecutionState, FlyteContext, FlyteContextManager
from flytekit.core.promise import Promise, VoidPromise, flyte_entity_call_handler
from flytekit.core.type_engine import TypeEngine
from flytekit.exceptions.user import FlyteDisapprovalException
from flytekit.interaction.parse_stdin import parse_stdin_to_literal
from flytekit.interaction.string_literals import scalar_to_string
from flytekit.models.core import workflow as _workflow_model
from flytekit.models.literals import Scalar
from flytekit.models.types import LiteralType

DEFAULT_TIMEOUT = datetime.timedelta(hours=1)


class Gate(object):
    """
    A node type that waits for user input before proceeding with a workflow.
    A gate is a type of node that behaves like a task, but instead of running code, it either needs to wait
    for user input to proceed or wait for a timer to complete running.
    """

    def __init__(
        self,
        name: str,
        input_type: typing.Optional[typing.Type] = None,
        upstream_item: typing.Optional[typing.Any] = None,
        sleep_duration: typing.Optional[datetime.timedelta] = None,
        timeout: typing.Optional[datetime.timedelta] = None,
    ):
        self._name = name
        self._input_type = input_type
        self._sleep_duration = sleep_duration
        self._timeout = timeout or DEFAULT_TIMEOUT
        self._upstream_item = upstream_item
        self._literal_type = TypeEngine.to_literal_type(input_type) if input_type else None

        # Determine the python interface if we can
        if self._sleep_duration:
            # Just a sleep so there is no interface
            self._python_interface = flyte_interface.Interface()
        elif input_type:
            # Waiting for user input, so the output of the node is whatever input the user provides.
            self._python_interface = flyte_interface.Interface(
