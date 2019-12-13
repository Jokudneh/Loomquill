"""User-facing tasks for SageMaker batch-transform jobs."""

from typing import Any, Dict, Optional, Type

from flytekitplugins.awssagemaker_inference.boto3_task import BotoConfig, BotoTask

from flytekit import kwtypes
from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin


class SageMakerTransformJobTask(AsyncConnectorExecutorMixin, PythonTask):
    """Run a SageMaker batch-transform job and emit the predictions ``S3OutputPath``.

    Outputs a single ``result: dict`` literal containing ``TransformJobArn``,
    ``TransformJobName``, ``ModelName``, ``TransformOutput.S3OutputPath`` (the S3
    prefix where SageMaker wrote one ``<input>.out`` per input object — feed this
    into a downstream Flyte task to consume the predictions), ``TransformStartTime``
    and ``TransformEndTime``.

    Set ``DataProcessing.JoinSource: "Input"`` in the config for tabular predictive
