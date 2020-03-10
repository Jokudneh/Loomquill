import asyncio
import importlib
import inspect
import json
import os
import pathlib
import sys
import tempfile
import typing
import typing as t
from dataclasses import dataclass, field, fields
from typing import Iterator, get_args

import rich_click as click
import yaml
from click import Context
from mashumaro.codecs.json import JSONEncoder
from rich.progress import Progress, TextColumn, TimeElapsedColumn
from typing_extensions import get_origin

from flytekit import Annotations, FlyteContext, FlyteContextManager, Labels, LaunchPlan, Literal, WorkflowExecutionPhase
from flytekit.clis.sdk_in_container.helpers import (
    parse_copy,
    patch_image_config,
)
from flytekit.clis.sdk_in_container.utils import (
    PyFlyteParams,
    domain_option,
    get_option_from_metadata,
    make_click_option_field,
    pretty_print_exception,
    project_option,
)
from flytekit.configuration import (
    DefaultImages,
    FastSerializationSettings,
    ImageConfig,
    SerializationSettings,
)
from flytekit.configuration.plugin import get_plugin
from flytekit.constants import CopyFileDetection
from flytekit.core import context_manager
from flytekit.core.artifact import ArtifactQuery
from flytekit.core.base_task import PythonTask
from flytekit.core.data_persistence import FileAccessProvider
from flytekit.core.resources import Resources, ResourceSpec
from flytekit.core.type_engine import TypeEngine
from flytekit.core.workflow import PythonFunctionWorkflow, WorkflowBase
from flytekit.exceptions.system import FlyteSystemException
from flytekit.exceptions.user import FlyteEntityNotFoundException
from flytekit.interaction.click_types import (
    FlyteLiteralConverter,
    key_value_callback,
    labels_callback,
    resource_callback,
)
from flytekit.interaction.string_literals import literal_string_repr
from flytekit.loggers import logger
from flytekit.models import security
from flytekit.models.common import RawOutputDataConfig
from flytekit.models.interface import Parameter, Variable
from flytekit.models.types import SimpleType
from flytekit.remote import (
    FlyteLaunchPlan,
    FlyteRemote,
    FlyteTask,
    FlyteWorkflow,
    remote_fs,
)
from flytekit.remote.executions import FlyteWorkflowExecution
from flytekit.tools import module_loader
from flytekit.tools.fast_registration import FastPackageOptions
from flytekit.tools.script_mode import _find_project_root, compress_scripts, get_all_modules
from flytekit.tools.translator import Options


@dataclass
class RunLevelComputedParams:
    """
    This class is used to store the computed parameters that are used to run a workflow / task / launchplan.
    Computed parameters are created during the execution
    """

    project_root: typing.Optional[str] = None
    module: typing.Optional[str] = None
    temp_file_name: typing.Optional[str] = None  # Used to store the temporary location of the file downloaded


@dataclass
class RunLevelParams(PyFlyteParams):
    """
    This class is used to store the parameters that are used to run a workflow / task / launchplan.
    """

    project: str = make_click_option_field(project_option)
    domain: str = make_click_option_field(domain_option)
    destination_dir: str = make_click_option_field(
        click.Option(
            param_decls=["--destination-dir", "destination_dir"],
            required=False,
            type=str,
            default=".",
            show_default=True,
            help="Directory inside the image where the tar file containing the code will be copied to",
        )
    )
    copy_all: bool = make_click_option_field(
        click.Option(
            param_decls=["--copy-all", "copy_all"],
            required=False,
            is_flag=True,
            default=False,
            show_default=True,
            help="[Deprecated, see --copy] Copy all files in the source root directory to"
            " the destination directory. You can specify --copy all instead",
        )
    )
    copy: typing.Optional[CopyFileDetection] = make_click_option_field(
        click.Option(
            param_decls=["--copy"],
            required=False,
            default="auto",
            type=click.Choice(["all", "auto"], case_sensitive=False),
            show_default=True,
            callback=parse_copy,
            help="Specifies how to detect which files to copy into image."
            " 'all' will behave as the deprecated copy-all flag, 'auto' copies only loaded Python modules",
        )
    )
    image_config: ImageConfig = make_click_option_field(
        click.Option(
            param_decls=["-i", "--image", "image_config"],
            required=False,
            multiple=True,
            type=click.UNPROCESSED,
            callback=ImageConfig.validate_image,
            default=[DefaultImages.default_image()],
            show_default=True,
            help="Image used to register and run.",
        )
    )
    service_account: str = make_click_option_field(
        click.Option(
            param_decls=["--service-account", "service_account"],
            required=False,
            type=str,
            default="",
            help="Service account used when executing this workflow",
        )
    )
    wait_execution: bool = make_click_option_field(
        click.Option(
            param_decls=["--wait", "--wait-execution", "wait_execution"],
            required=False,
            is_flag=True,
            default=False,
            show_default=True,
            help="Whether to wait for the execution to finish",
        )
    )
    poll_interval: int = make_click_option_field(
        click.Option(
            param_decls=["--poll-interval", "poll_interval"],
            required=False,
            type=int,
            default=None,
            show_default=True,
            help="Poll interval in seconds to check the status of the execution",
        )
    )
    dump_snippet: bool = make_click_option_field(
        click.Option(
            param_decls=["--dump-snippet", "dump_snippet"],
            required=False,
            is_flag=True,
            default=False,
            show_default=True,
            help="Whether to dump a code snippet instructing how to load the workflow execution using flyteremote",
        )
    )
    overwrite_cache: bool = make_click_option_field(
        click.Option(
            param_decls=["--overwrite-cache", "overwrite_cache"],
            required=False,
            is_flag=True,
            default=False,
            show_default=True,
            help="Whether to overwrite the cache if it already exists",
        )
    )
    interruptible: typing.Optional[bool] = make_click_option_field(
        click.Option(
            param_decls=["--interruptible"],
            type=bool,
            required=False,
            default=None,
            help="Specify if the execution should be forced to run with an interruptible flag of true or false."
            " Use '--interruptible true' or '--interruptible false' to explicitly enable/disable."
            " If this option is not provided, the default interruptible behavior of the remote Flyte entity is used.",
        )
    )
    envvars: typing.Dict[str, str] = make_click_option_field(
        click.Option(
            param_decls=["--envvars", "--env"],
            required=False,
            multiple=True,
            type=str,
            show_default=True,
            callback=key_value_callback,
            help="Environment variables to set in the container, of the format `ENV_NAME=ENV_VALUE`",
        )
    )
    resource_requests: typing.Optional[Resources] = make_click_option_field(
        click.Option(
            param_decls=["--resource-requests"],
            required=False,
            show_default=True,
            type=str,
            callback=resource_callback,
            help="This overrides default task resource requests for tasks that have no statically defined resource requests in their task decorator. "
            "Example usage: --resource-requests 'cpu=1,mem=2Gi,gpu=1'",
        )
    )
    resource_limits: typing.Optional[Resources] = make_click_option_field(
        click.Option(
            param_decls=["--resource-limits"],
            required=False,
            show_default=True,
            type=str,
            callback=resource_callback,
            help="This overrides default task resource limits for tasks that have no statically defined resource limits in their task decorator. "
            "Example usage: --resource-limits 'cpu=1,mem=2Gi,gpu=1'",
        )
    )
