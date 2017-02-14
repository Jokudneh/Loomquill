import os
import types
import typing
from dataclasses import Field, dataclass, field
from types import MappingProxyType

import grpc
import rich_click as click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.traceback import Traceback

from flytekit.configuration import TaskConfig
from flytekit.core.constants import SOURCE_CODE
from flytekit.exceptions.base import FlyteException
from flytekit.exceptions.user import FlyteCompilationException, FlyteInvalidInputException
from flytekit.exceptions.utils import annotate_exception_with_code
from flytekit.loggers import get_level_from_cli_verbosity, logger

task_config = TaskConfig.auto()

project_option = click.Option(
    param_decls=["-p", "--project"],
    required=False,
    type=str,
    default=os.getenv("FLYTE_DEFAULT_PROJECT") or task_config.project,
    show_default=True,
    help="Project to register and run this workflow in. Can also be set through envvar " "``FLYTE_DEFAULT_PROJECT``",
)

domain_option = click.Option(
    param_decls=["-d", "--domain"],
    required=False,
    type=str,
    default=os.getenv("FLYTE_DEFAULT_DOMAIN") or task_config.domain,
    show_default=True,
    help="Domain to register and run this workflow in, can also be set through envvar " "``FLYTE_DEFAULT_DOMAIN``",
)

project_option_dec = click.option(
    "-p",
    "--project",
    required=False,
    type=str,
    default=os.getenv("FLYTE_DEFAULT_PROJECT") or task_config.project,
    show_default=True,
    help="Project for workflow/launchplan. Can also be set through envvar " "``FLYTE_DEFAULT_PROJECT``",
)
