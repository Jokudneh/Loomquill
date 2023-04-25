"""User-facing tasks for SageMaker training jobs."""

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
class SageMakerTraining(PythonicJobConfig):
    """Pythonic-mode config for a SageMaker training job.

    Use as ``@task(task_config=SageMakerTraining(...), container_image=...)`` to
    run the decorated Python function inside a SageMaker training job. Inherits
    all fields from
    :class:`~flytekitplugins.awssagemaker_inference.pythonic_base.PythonicJobConfig`.

    :param output_s3_path: Optional ``OutputDataConfig.S3OutputPath`` for the
        SageMaker model tar. Pythonic mode returns results via Flyte outputs, so
        this is rarely needed; when unset the connector points it at the Flyte
        output prefix (the resulting ``model.tar.gz`` is harmless and unused).
    :param vpc_config: Optional boto3 ``VpcConfig`` request shape containing
        ``Subnets`` and ``SecurityGroupIds``.
    """

    output_s3_path: Optional[str] = None
    vpc_config: Optional[Dict[str, Any]] = None


class SageMakerTrainingTask(PythonicSageMakerJobTask):
    """Pythonic-mode SageMaker training task (runs a ``@task`` function in a training job)."""

    _TASK_TYPE = "sagemaker-training-task"


TaskPlugins.register_pythontask_plugin(SageMakerTraining, SageMakerTrainingTask)


class SageMakerTrainingJobTask(AsyncConnectorExecutorMixin, PythonTask):
    """Run a SageMaker training job and emit its model artefact URI plus final metrics.

