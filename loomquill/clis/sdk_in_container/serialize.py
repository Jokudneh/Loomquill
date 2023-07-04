import os
import sys
import typing
from enum import Enum

import rich
import rich_click as click

from flytekit.clis.sdk_in_container import constants
from flytekit.clis.sdk_in_container.constants import CTX_PACKAGES
from flytekit.configuration import FastSerializationSettings, ImageConfig, SerializationSettings
from flytekit.interaction.click_types import key_value_callback
from flytekit.tools.fast_registration import fast_package
from flytekit.tools.repo import serialize_to_folder

CTX_IMAGE = "image"
CTX_LOCAL_SRC_ROOT = "local_source_root"
CTX_FLYTEKIT_VIRTUALENV_ROOT = "flytekit_virtualenv_root"
CTX_PYTHON_INTERPRETER = "python_interpreter"
CTX_ENV = "env"


class SerializationMode(Enum):
    DEFAULT = 0
    FAST = 1


def serialize_all(
    pkgs: typing.List[str] = None,
    local_source_root: typing.Optional[str] = None,
    folder: typing.Optional[str] = None,
    mode: typing.Optional[SerializationMode] = None,
    image_config: typing.Optional[ImageConfig] = None,
    flytekit_virtualenv_root: typing.Optional[str] = None,
    python_interpreter: typing.Optional[str] = None,
    config_file: typing.Optional[str] = None,
    env: typing.Optional[typing.Dict[str, str]] = None,
):
    """
    This function will write to the folder specified the following protobuf types
    ```
    flyteidl.admin.launch_plan_pb2.LaunchPlan
    flyteidl.admin.workflow_pb2.WorkflowSpec
    flyteidl.admin.task_pb2.TaskSpec
    ```

