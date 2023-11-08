import os
import pathlib
import tempfile

import mock
import pytest

import flytekit.configuration
from flytekit.configuration import DefaultImages, ImageConfig
from flytekit.tools.repo import find_common_root, list_packages_and_modules

task_text = """
from flytekit import task
@task
def t1(a: int):
    ...
"""


# Mock out the entities so the load function doesn't try to load everything
@mock.patch("flytekit.core.context_manager.FlyteEntities")
@mock.patch("flytekit.core.base_task.FlyteEntities")
