"""Unit tests for the Pythonic-mode SageMaker training task."""

import types

import pytest
from flytekitplugins.awssagemaker_inference.pythonic_base import (
    SAGEMAKER_PYTHONIC_BASE_IMAGE,
    PythonicSageMakerJobTask,
)
from flytekitplugins.awssagemaker_training import SageMakerTraining, SageMakerTrainingTask

from flytekit import ImageSpec, PythonFunctionTask, task
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin

ROLE = "arn:aws:iam::123456789012:role/sm-exec"
REGION = "us-east-1"


def _fn() -> int:
    return 1


def _build_task(container_image):
    return SageMakerTrainingTask(
        task_config=SageMakerTraining(execution_role_arn=ROLE, region=REGION),
        task_function=_fn,
        container_image=container_image,
    )


