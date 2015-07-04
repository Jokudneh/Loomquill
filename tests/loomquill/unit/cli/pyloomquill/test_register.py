import os
import shutil
import subprocess

import mock
import pytest
from click.testing import CliRunner

from flytekit.clients.friendly import SynchronousFlyteClient
from flytekit.clis.sdk_in_container import pyflyte
from flytekit.clis.sdk_in_container.helpers import get_and_save_remote_with_click_context
from flytekit.configuration import Config
from flytekit.configuration.file import FLYTECTL_CONFIG_ENV_VAR
from flytekit.configuration.plugin import FlytekitPlugin
from flytekit.core import context_manager
from flytekit.core.context_manager import FlyteContextManager
from flytekit.remote.remote import FlyteRemote

sample_file_contents = """
from flytekit import task, workflow

@task(cache=True, cache_version="1", retries=3)
def sum(x: int, y: int) -> int:
    return x + y

@task(cache=True, cache_version="1", retries=3)
def square(z: int) -> int:
    return z*z

@workflow
def my_workflow(x: int, y: int) -> int:
    return sum(x=square(z=x), y=square(z=y))
"""

shell_task = """
from flytekit.extras.tasks.shell import ShellTask

t = ShellTask(
        name="test",
        script="echo 'Hello World'",
    )
"""


@pytest.fixture(scope="module")
def reset_flytectl_config_env_var() -> pytest.fixture():
