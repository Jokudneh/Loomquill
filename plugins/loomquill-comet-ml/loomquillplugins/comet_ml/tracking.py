import os
from functools import partial
from hashlib import shake_256
from typing import Callable, Optional, Union

import comet_ml
from flytekit import Secret
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.utils import ClassDecorator

COMET_ML_EXECUTION_TYPE_VALUE = "comet-ml-execution-id"
COMET_ML_CUSTOM_TYPE_VALUE = "comet-ml-custom-id"


def _generate_suffix_with_length_10(project_name: str, workspace: str) -> str:
    """Generate suffix from project_name + workspace."""
    h = shake_256(f"{project_name}-{workspace}".encode("utf-8"))
    # Using 5 generates a suffix with length 10
    return h.hexdigest(5)


def _generate_experiment_key(hostname: str, project_name: str, workspace: str) -> str:
    """Generate experiment key that comet_ml can use:

    1. Is alphanumeric
    2. 32 <= len(experiment_key) <= 50
    """
    # In Flyte, hostname is set to {.executionName}-{.nodeID}-{.taskRetryAttempt}[-{replica-type}-{replica-index}], where
    # - len(executionName) == 20
    # - 2 <= len(nodeId) <= 8
    # - 1 <= len(taskRetryAttempt)) <= 2 (In practice, retries does not go above 99)
    # - replica-type == "worker"
    # - len(replica-index) == 1
    # Removing the `-` because it is not alphanumeric, the 23 <= len(hostname) <= 30
    # On the low end we need to add 10 characters to stay in the range acceptable to comet_ml
    hostname = hostname.replace("-", "")
    suffix = _generate_suffix_with_length_10(project_name, workspace)
    return f"{hostname}{suffix}"


def comet_ml_login(
    project_name: str,
    workspace: str,
    secret: Union[Secret, Callable],
    experiment_key: Optional[str] = None,
    host: str = "https://www.comet.com",
    **login_kwargs: dict,
):
    """Comet plugin.
    Args:
        project_name (str): Send your experiment to a specific project. (Required)
        workspace (str): Attach an experiment to a project that belongs to this workspace. (Required)
        secret (Secret or Callable): Secret with your `COMET_API_KEY` or a callable that returns the API key.
            The callable takes no arguments and returns a string. (Required)
        experiment_key (str): Experiment key.
        host (str): URL to your Comet service. Defaults to "https://www.comet.com"
        **login_kwargs (dict): The rest of the arguments are passed directly to `comet_ml.login`.
    """
    return partial(
        _comet_ml_login_class,
        project_name=project_name,
        workspace=workspace,
        secret=secret,
        experiment_key=experiment_key,
        host=host,
        **login_kwargs,
