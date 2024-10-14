import os
from functools import partial
from typing import Callable, Union

import neptune
from flytekit import Secret
from flytekit.core.context_manager import FlyteContext, FlyteContextManager
from flytekit.core.utils import ClassDecorator

NEPTUNE_RUN_VALUE = "neptune-run-id"


def neptune_init_run(
    project: str,
    secret: Union[Secret, Callable],
    host: str = "https://app.neptune.ai",
    **init_run_kwargs: dict,
):
    """Neptune 2.x plugin. Use Neptune Scale instead (`neptune_scale_run`).

    Args:
        project (str): Name of the project where the run should go, in the form `workspace-name/project_name`.
            (Required)
        secret (Secret or Callable): Secret with your `NEPTUNE_API_KEY` or a callable that returns the API key.
            The callable takes no arguments and returns a string. (Required)
        host (str): URL to Neptune. Defaults to "https://app.neptune.ai".
        **init_run_kwargs (dict):
    """
    return partial(
        _neptune_init_run_class,
        project=project,
        secret=secret,
        host=host,
        **init_run_kwargs,
    )


class _neptune_init_run_class(ClassDecorator):
    NEPTUNE_HOST_KEY = "host"
