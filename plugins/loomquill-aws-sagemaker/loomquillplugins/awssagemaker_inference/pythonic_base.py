"""Shared foundation for SageMaker "Pythonic mode" job tasks and connectors.

Pythonic mode lets users run a Flyte ``@task`` function body directly inside a
SageMaker job container (Processing or Training) instead of supplying a boto3
config + prebuilt algorithm image. It mirrors ``flytekit-aws-emr-serverless``
but is simpler: SageMaker runs the container directly via the job's
``ContainerEntrypoint``, so there is no S3 entrypoint shim to upload — the
connector points ``ContainerEntrypoint`` at the rendered Flyte command
(``task_template.container.args``) on the user's flytekit-containing image.

The mechanics are identical for Processing and Training; the only per-service
differences are captured as overridable class attributes / methods on
``PythonicSageMakerJobConnector``:

* ``create_method`` / ``describe_method`` / ``stop_method`` — boto3 method names
* ``job_name_key`` / ``status_key`` / ``secondary_status_key`` — response fields
* ``_state_map`` — service status -> Flyte phase
* ``_build_request`` — assemble the ``create_*_job`` request (``AppSpecification``
  vs ``AlgorithmSpecification``, ``ProcessingResources`` vs ``ResourceConfig``)

Outputs flow back the Flyte-native way: the inner ``pyflyte-execute`` writes
``outputs.pb`` to the rendered ``--output-prefix`` and the connector returns
``outputs=None`` so flytekit materializes the typed return. Because SageMaker
only surfaces a job status (and ``pyflyte-execute`` exits 0 even on user error),
the connector checks for an ``error.pb`` at the output prefix on ``Completed`` to
avoid reporting a false success — the SageMaker-native equivalent of EMR's
exit-code translation shim.
"""

import dataclasses
import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import cloudpickle
from flyteidl.core.execution_pb2 import TaskExecution

from flytekit import FlyteContext, ImageSpec, PythonFunctionTask
from flytekit.configuration import DefaultImages, SerializationSettings
from flytekit.core.constants import FLYTE_FAIL_ON_ERROR
from flytekit.core.context_manager import FlyteContextManager
from flytekit.extend.backend.base_connector import (
    AsyncConnectorBase,
    AsyncConnectorExecutorMixin,
    Resource,
    ResourceMeta,
)
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate

from .boto3_mixin import Boto3ConnectorMixin, CustomException

# Default base image for Pythonic-mode tasks. Applied (EMR-style) when the user
# passes an ``ImageSpec`` without an explicit ``base_image`` so the built image
# is guaranteed to contain flytekit, which the in-container ``pyflyte-execute``
# needs. Users can always override by setting ``base_image`` or passing a plain
# ECR image URI string as ``container_image``.
SAGEMAKER_PYTHONIC_BASE_IMAGE = DefaultImages.default_image()

# SageMaker job names: <= 63 chars, must match ^[a-zA-Z0-9](-*[a-zA-Z0-9])*.
_MAX_JOB_NAME_LEN = 63
_INVALID_JOB_NAME_CHARS = re.compile(r"[^a-zA-Z0-9-]")


@dataclass
class PythonicJobConfig:
    """Shared task configuration for SageMaker Pythonic-mode jobs.

    :param execution_role_arn: IAM role SageMaker assumes to run the job (S3/ECR/logs).
    :param region: AWS region for the SageMaker client.
    :param instance_type: SageMaker ML instance type for the job.
    :param instance_count: Number of instances.
    :param volume_size_in_gb: Attached EBS volume size.
    :param max_runtime_in_seconds: Hard stop for the job.
    :param environment: Extra environment variables for the container.
    :param kms_key_id: Optional KMS key for the attached storage volume.
    :param tags: Resource tags (dict; converted to the boto3 ``[{Key, Value}]`` shape).
    :param job_name_prefix: Prefix for the generated SageMaker job name.
    """

    execution_role_arn: str
    region: str
    instance_type: str = "ml.m5.large"
    instance_count: int = 1
    volume_size_in_gb: int = 30
    max_runtime_in_seconds: int = 3600
    environment: Optional[Dict[str, str]] = None
    kms_key_id: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    job_name_prefix: str = "flyte-"

    def __post_init__(self) -> None:
