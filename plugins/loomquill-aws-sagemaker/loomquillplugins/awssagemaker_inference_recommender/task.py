"""User-facing tasks for SageMaker Inference Recommender jobs."""

from typing import Any, Dict, Optional, Type

from flytekitplugins.awssagemaker_inference.boto3_task import BotoConfig, BotoTask

from flytekit import kwtypes
from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin


class SageMakerInferenceRecommenderJobTask(AsyncConnectorExecutorMixin, PythonTask):
    """Run a SageMaker Inference Recommender job and emit its ranked recommendations.

    Outputs a single ``result: dict`` literal containing ``JobArn``, ``JobName``,
    ``JobType`` (``Default`` or ``Advanced``), ``InferenceRecommendations`` (ranked
    list with ``EndpointConfiguration.InstanceType``, ``InitialInstanceCount`` and
    cost / latency / throughput metrics - feed the top entry into
    ``SageMakerEndpointConfigTask`` to deploy on the recommended instance type),
    ``EndpointPerformances`` (populated for Default jobs that benchmark existing
    endpoints supplied through ``InputConfig.Endpoints``), and ``CompletionTime``.

    Use ``JobType: "Default"`` for a quick instance-type sweep (~45 min) keyed off
    a ``ModelPackageVersionArn``; use ``JobType: "Advanced"`` to run a custom
    traffic pattern + ``StoppingConditions`` over user-supplied
    ``EndpointConfigurations``.

