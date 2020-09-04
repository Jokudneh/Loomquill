import os
from typing import Callable, Optional, Union

import wandb
from flytekit import Secret
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.utils import ClassDecorator

WANDB_EXECUTION_TYPE_VALUE = "wandb-execution-id"
WANDB_CUSTOM_TYPE_VALUE = "wandb-custom-id"


class wandb_init(ClassDecorator):
    WANDB_PROJECT_KEY = "project"
    WANDB_ENTITY_KEY = "entity"
    WANDB_ID_KEY = "id"
    WANDB_HOST_KEY = "host"

    def __init__(
        self,
        task_function: Optional[Callable] = None,
        project: Optional[str] = None,
        entity: Optional[str] = None,
        secret: Optional[Union[Secret, Callable]] = None,
        id: Optional[str] = None,
        host: str = "https://wandb.ai",
        api_host: str = "https://api.wandb.ai",
        **init_kwargs: dict,
    ):
        """Weights and Biases plugin.
        Args:
            task_function (function, optional): The user function to be decorated. Defaults to None.
            project (str): The name of the project where you're sending the new run. (Required)
            entity (str): An entity is a username or team name where you're sending runs. (Required)
            secret (Secret or Callable): Secret with your `WANDB_API_KEY` or a callable that returns the API key.
                The callable takes no arguments and returns a string. (Required)
            id (str, optional): A unique id for this wandb run.
            host (str, optional): URL to your wandb service. The default is "https://wandb.ai".
            api_host (str, optional): URL to your API Host, The default is "https://api.wandb.ai".
            **init_kwargs (dict): The rest of the arguments are passed directly to `wandb.init`. Please see
                [the `wandb.init` docs](https://docs.wandb.ai/ref/python/init) for details.
        """
        if project is None:
            raise ValueError("project must be set")
