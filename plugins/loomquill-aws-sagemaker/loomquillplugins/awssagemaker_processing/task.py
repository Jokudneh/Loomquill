"""User-facing tasks for SageMaker processing jobs."""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, Union

from flytekitplugins.awssagemaker_inference.boto3_task import BotoConfig, BotoTask
from flytekitplugins.awssagemaker_inference.pythonic_base import (
    PythonicJobConfig,
    PythonicSageMakerJobTask,
)

from flytekit import ImageSpec, kwtypes
from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.extend import TaskPlugins
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin
from flytekit.image_spec.image_spec import ImageBuildEngine


@dataclass
class SageMakerProcessing(PythonicJobConfig):
    """Pythonic-mode config for a SageMaker processing job.

    Use as ``@task(task_config=SageMakerProcessing(...), container_image=...)``
    to run the decorated Python function inside a SageMaker processing job. See
    :class:`~flytekitplugins.awssagemaker_inference.pythonic_base.PythonicJobConfig`
    for the available fields.

    :param network_config: Optional boto3 ``NetworkConfig`` request shape,
        including an optional nested ``VpcConfig``.
    """

    network_config: Optional[Dict[str, Any]] = None


class SageMakerProcessingTask(PythonicSageMakerJobTask):
    """Pythonic-mode SageMaker processing task (runs a ``@task`` function in a processing job)."""

    _TASK_TYPE = "sagemaker-processing-task"


