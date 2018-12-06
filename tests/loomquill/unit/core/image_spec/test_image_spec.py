import os
import sys
from unittest.mock import Mock

import mock
import pytest

from flytekit.configuration import (FastSerializationSettings, ImageConfig,
                                    SerializationSettings)
from flytekit.constants import CopyFileDetection
from flytekit.core import context_manager
from flytekit.core.context_manager import ExecutionState
from flytekit.core.python_auto_container import update_image_spec_copy_handling
from flytekit.image_spec import ImageSpec
from flytekit.image_spec.image_spec import _F_IMG_ID, ImageBuildEngine

REQUIREMENT_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")
REGISTRY_CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "registry_config.json")


def test_image_spec(mock_image_spec_builder, monkeypatch):
    base_image = ImageSpec(name="base", builder="dummy", base_image="base_image")

    image_spec = ImageSpec(
        name="FLYTEKIT",
        builder="dummy",
        packages=["pandas"],
        apt_packages=["git"],
        python_version="3.9",
        registry="localhost:30001",
        base_image=base_image,
        cuda="11.2.2",
        cudnn="8",
        requirements=REQUIREMENT_FILE,
        registry_config=REGISTRY_CONFIG_FILE,
        entrypoint=["/bin/bash"],
        copy=["/src/file1.txt"],
        builder_options={"builder_option": "builder_option_value"},
    )
    assert image_spec._is_force_push is False

    image_spec = image_spec.with_commands("echo hello")
    image_spec = image_spec.with_packages("numpy")
    image_spec = image_spec.with_apt_packages("wget")
    image_spec = image_spec.with_copy(["/src", "/src/file2.txt"])
    image_spec = image_spec.force_push()

    assert image_spec.python_version == "3.9"
    assert image_spec.base_image == base_image
    assert image_spec.packages == ["pandas", "numpy"]
    assert image_spec.apt_packages == ["git", "wget"]
    assert image_spec.registry == "localhost:30001"
    assert image_spec.requirements == REQUIREMENT_FILE
    assert image_spec.registry_config == REGISTRY_CONFIG_FILE
    assert image_spec.cuda == "11.2.2"
    assert image_spec.cudnn == "8"
    assert image_spec.name == "flytekit"
    assert image_spec.builder == "dummy"
    assert image_spec.source_root is None
    assert image_spec.env is None
    assert image_spec.pip_index is None
    assert image_spec.is_container() is True
    assert image_spec.commands == ["echo hello"]
    assert image_spec._is_force_push is True
    assert image_spec.entrypoint == ["/bin/bash"]
    assert image_spec.copy == ["/src/file1.txt", "/src", "/src/file2.txt"]
    assert image_spec.builder_options == {"builder_option": "builder_option_value"}

    assert image_spec.image_name() == f"localhost:30001/flytekit:{image_spec.tag}"
    ctx = context_manager.FlyteContext.current_context()
    with context_manager.FlyteContextManager.with_context(
        ctx.with_execution_state(ctx.execution_state.with_params(mode=ExecutionState.Mode.TASK_EXECUTION))
