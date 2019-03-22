from collections import OrderedDict

import mock
import pytest

from flytekit.core import context_manager
from flytekit.core.python_auto_container import default_task_resolver
from flytekitplugins.flyteinteractive import (
    CODE_TOGETHER_CONFIG,
    CODE_TOGETHER_EXTENSION,
    COPILOT_CONFIG,
    COPILOT_EXTENSION,
    DEFAULT_CODE_SERVER_DIR_NAMES,
    DEFAULT_CODE_SERVER_EXTENSIONS,
    DEFAULT_CODE_SERVER_REMOTE_PATHS,
    VIM_CONFIG,
    VIM_EXTENSION,
    VscodeConfig,
    vscode,
)
from flytekitplugins.flyteinteractive.constants import (
    EXIT_CODE_SUCCESS,
)
from flytekitplugins.flyteinteractive.vscode_lib.decorator import (
    get_code_server_info,
    get_installed_extensions,
    is_extension_installed,
)

from flytekit import task, workflow, dynamic
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.context_manager import ExecutionState, FlyteContextManager
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
def mock_code_server_info_dict():
    return {"arm64": "Arm server info", "amd64": "AMD server info"}


@pytest.fixture
def vscode_patches():
    with mock.patch("multiprocessing.Process") as mock_process, mock.patch(
        "flytekit.interactive.vscode_lib.decorator.prepare_interactive_python"
    ) as mock_prepare_interactive_python, mock.patch(
        "flytekit.interactive.vscode_lib.decorator.exit_handler"
    ) as mock_exit_handler, mock.patch(
        "flytekit.interactive.vscode_lib.decorator.download_vscode"
    ) as mock_download_vscode, mock.patch("signal.signal") as mock_signal, mock.patch(
        "flytekit.interactive.vscode_lib.decorator.prepare_resume_task_python"
    ) as mock_prepare_resume_task_python, mock.patch(
        "flytekit.interactive.vscode_lib.decorator.prepare_launch_json"
    ) as mock_prepare_launch_json:
        yield (
            mock_process,
            mock_prepare_interactive_python,
            mock_exit_handler,
            mock_download_vscode,
            mock_signal,
            mock_prepare_resume_task_python,
            mock_prepare_launch_json,
        )


def test_vscode_remote_execution(vscode_patches, mock_remote_execution):
    (
        mock_process,
