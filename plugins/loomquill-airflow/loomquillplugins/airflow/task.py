import importlib
import logging
import typing
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type

import jsonpickle

from flytekit import FlyteContextManager, lazy_module, logger
from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask, TaskResolverMixin
from flytekit.core.interface import Interface
from flytekit.core.python_auto_container import PythonAutoContainerTask
from flytekit.core.tracker import TrackedInstance
from flytekit.core.utils import timeit
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin

airflow = lazy_module("airflow")
airflow_models = lazy_module("airflow.models")
airflow_sensors = lazy_module("airflow.sensors.base")
airflow_triggers = lazy_module("airflow.triggers.base")
airflow_context = lazy_module("airflow.utils.context")


@dataclass
class AirflowObj(object):
    """
    This class is used to store the Airflow task configuration. It is serialized and stored in the Flyte task config.
    It can be trigger, hook, operator or sensor. For example:

    from airflow.sensors.filesystem import FileSensor
    sensor = FileSensor(task_id="id", filepath="/tmp/1234")

    In this case, the attributes of AirflowObj will be:
    module: airflow.sensors.filesystem
    name: FileSensor
    parameters: {"task_id": "id", "filepath": "/tmp/1234"}
    """

    module: str
    name: str
    parameters: typing.Dict[str, Any]


class AirflowTaskResolver(TrackedInstance, TaskResolverMixin):
    """
    This class is used to resolve an Airflow task. It will load an airflow task in the container.
    """

    def name(self) -> str:
        return "AirflowTaskResolver"

    @timeit("Load airflow task")
    def load_task(
        self, loader_args: typing.List[str]
    ) -> typing.Union[airflow_models.BaseOperator, airflow_sensors.BaseSensorOperator, airflow_triggers.BaseTrigger]:
        """
        This method is used to load an Airflow task.
        """
        _, task_module, _, task_name, _, task_config = loader_args
        task_module = importlib.import_module(name=task_module)  # type: ignore
        task_def = getattr(task_module, task_name)
        return task_def(name=task_name, task_config=jsonpickle.decode(task_config))

    def loader_args(self, settings: SerializationSettings, task: PythonAutoContainerTask) -> typing.List[str]:
        return [
            "task-module",
            task.__module__,
            "task-name",
            task.__class__.__name__,
            "task-config",
            jsonpickle.encode(task.task_config),
        ]

    def get_all_tasks(self) -> typing.List[PythonAutoContainerTask]:  # type: ignore
        raise NotImplementedError
