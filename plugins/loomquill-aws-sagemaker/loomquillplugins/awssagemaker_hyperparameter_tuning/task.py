"""User-facing tasks for SageMaker hyperparameter-tuning jobs."""

from typing import Any, Dict, Optional, Type, Union

from flytekitplugins.awssagemaker_inference.boto3_task import BotoConfig, BotoTask

from flytekit import ImageSpec, kwtypes
from flytekit.configuration import SerializationSettings
from flytekit.core.base_task import PythonTask
from flytekit.core.interface import Interface
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin
from flytekit.image_spec.image_spec import ImageBuildEngine


class SageMakerHyperParameterTuningJobTask(AsyncConnectorExecutorMixin, PythonTask):
    """Run a SageMaker hyperparameter-tuning job and emit the best trial's artefacts.

    Outputs a single ``result: dict`` literal containing:

    - ``HyperParameterTuningJobArn``, ``HyperParameterTuningJobName``
    - ``BestTrainingJob`` — the trial SageMaker picked: ``TrainingJobName``,
      ``TrainingJobArn``, ``TunedHyperParameters``,
      ``FinalHyperParameterTuningJobObjectiveMetric.{MetricName, Value}``,
      ``ObjectiveStatus``, plus the trial's ``ModelArtifacts.S3ModelArtifacts``
      resolved via a follow-up ``describe_training_job`` call (so this output
      chains directly into ``SageMakerModelTask`` the same way the plain
      ``SageMakerTrainingJobTask`` does)
    - ``ModelArtifacts.S3ModelArtifacts`` — top-level convenience copy of the
      best trial's model URI so workflows can consume it symmetrically with
