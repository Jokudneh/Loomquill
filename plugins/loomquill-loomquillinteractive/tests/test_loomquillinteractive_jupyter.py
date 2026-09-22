from collections import OrderedDict

import mock
import pytest
from flytekitplugins.flyteinteractive import jupyter

from flytekit import task, workflow
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.context_manager import ExecutionState
from flytekit.tools.translator import get_serializable_task


@pytest.fixture
def mock_local_execution():
    with mock.patch.object(ExecutionState, "is_local_execution", return_value=True) as mock_func:
        yield mock_func


@pytest.fixture
def mock_remote_execution():
    with mock.patch.object(ExecutionState, "is_local_execution", return_value=False) as mock_func:
        yield mock_func


@pytest.fixture
def jupyter_patches():
    with mock.patch("multiprocessing.Process") as mock_process, mock.patch(
        "flytekitplugins.flyteinteractive.jupyter_lib.decorator.write_example_notebook"
    ) as mock_write_example_notebook, mock.patch(
        "flytekitplugins.flyteinteractive.jupyter_lib.decorator.exit_handler"
    ) as mock_exit_handler:
        yield (mock_process, mock_write_example_notebook, mock_exit_handler)


def test_jupyter_remote_execution(jupyter_patches, mock_remote_execution):
    (mock_process, mock_write_example_notebook, mock_exit_handler) = jupyter_patches
