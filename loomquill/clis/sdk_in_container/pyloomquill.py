import os
import typing

import rich_click as click

from flytekit import configuration
from flytekit.clis.sdk_in_container.backfill import backfill
from flytekit.clis.sdk_in_container.build import build
from flytekit.clis.sdk_in_container.constants import CTX_CONFIG_FILE, CTX_PACKAGES, CTX_VERBOSE
from flytekit.clis.sdk_in_container.executions import execute
from flytekit.clis.sdk_in_container.fetch import fetch
from flytekit.clis.sdk_in_container.get import get
from flytekit.clis.sdk_in_container.init import init
from flytekit.clis.sdk_in_container.launchplan import launchplan
from flytekit.clis.sdk_in_container.local_cache import local_cache
from flytekit.clis.sdk_in_container.metrics import metrics
from flytekit.clis.sdk_in_container.package import package
from flytekit.clis.sdk_in_container.register import register
from flytekit.clis.sdk_in_container.run import run
from flytekit.clis.sdk_in_container.serialize import serialize
from flytekit.clis.sdk_in_container.serve import serve
from flytekit.clis.sdk_in_container.utils import ErrorHandlingCommand, validate_package
from flytekit.clis.version import info
from flytekit.configuration.file import FLYTECTL_CONFIG_ENV_VAR, FLYTECTL_CONFIG_ENV_VAR_OVERRIDE
from flytekit.configuration.internal import LocalSDK
from flytekit.configuration.plugin import get_plugin
from flytekit.loggers import logger


@click.group("pyflyte", invoke_without_command=True, cls=ErrorHandlingCommand)
@click.option(
    "-v",
