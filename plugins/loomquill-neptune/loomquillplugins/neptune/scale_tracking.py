import os
from functools import partial
from typing import Callable, Optional, Union

import neptune_scale

from flytekit import Secret
from flytekit.core.context_manager import FlyteContext, FlyteContextManager
from flytekit.core.utils import ClassDecorator

NEPTUNE_RUN_VALUE = "neptune-scale-run"
NEPTUNE_RUN_CUSTOM_VALUE = "neptune-scale-custom-id"


def neptune_scale_run(
    project: str,
    secret: Union[Secret, Callable],
    run_id: Optional[str] = None,
    experiment_name: Optional[str] = None,
    **init_run_kwargs: dict,
) -> "Callable[..., _neptune_scale_run_class]":
    """Neptune Scale Plugin.

    Args:
        project (str): Name of the project where the run should go, in the form `workspace-name/project_name`.
            (Required)
        secret (Union[Secret, Callable]): Secret with your `NEPTUNE_API_KEY` or a callable that returns the API key.
            The callable takes no arguments and returns a string. (Required)
        run_id (Optional[str]): A unique id for this Neptune run. If not provided, Neptune will generate its own id.
        experiment_name (Optional[str]): If provided, the run will be logged as an experiment with this name.
        **init_run_kwargs (dict): Additional keyword arguments to pass to the Neptune Run constructor.

    Returns:
        Callable[..., _neptune_scale_run_class]: A callable that returns a wrapped Neptune Scale run instance.
    """
    return partial(
        _neptune_scale_run_class,
        project=project,
        secret=secret,
        run_id=run_id,
        experiment_name=experiment_name,
        **init_run_kwargs,
    )


class _neptune_scale_run_class(ClassDecorator):
    NEPTUNE_PROJECT = "project"
    NEPTUNE_RUN_ID = "id"

    def __init__(
        self,
