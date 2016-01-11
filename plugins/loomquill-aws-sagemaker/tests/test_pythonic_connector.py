"""Unit tests for the Pythonic-mode SageMaker connectors (Processing + Training)
and their shared base (request building, outputs.pb/error.pb resolution, job
name generation, idempotency, stop-on-delete)."""

import types
from collections import OrderedDict
from pathlib import Path
from unittest import mock

import pytest
from botocore.exceptions import ClientError
from flyteidl.core import errors_pb2
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.awssagemaker_inference.boto3_mixin import CustomException
from flytekitplugins.awssagemaker_inference.pythonic_base import (
    PythonicJobMetadata,
    _PythonicJobError,
    _make_job_name,
    _tags_to_list,
)
from flytekitplugins.awssagemaker_processing import SageMakerProcessing
from flytekitplugins.awssagemaker_training import SageMakerTraining

from flytekit import task
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.core.constants import FLYTE_FAIL_ON_ERROR
from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.extend.backend.utils import render_task_template
from flytekit.tools.translator import get_serializable

ROLE = "arn:aws:iam::123456789012:role/sm-exec"
REGION = "us-east-1"
OUTPUT_PREFIX = "s3://bucket/flyte/exec/n0"
IMAGE = "123.dkr.ecr.us-east-1.amazonaws.com/img:tag"
ARGS = ["pyflyte-fast-execute", "--", "pyflyte-execute", "--output-prefix", OUTPUT_PREFIX]

_CALL = "flytekitplugins.awssagemaker_inference.boto3_mixin.Boto3ConnectorMixin._call"
_READ_ERROR = (
    "flytekitplugins.awssagemaker_inference.pythonic_base."
    "PythonicSageMakerJobConnector._read_error"
)
_ARTIFACT_EXISTS = (
    "flytekitplugins.awssagemaker_inference.pythonic_base."
    "PythonicSageMakerJobConnector._artifact_exists"
)


def _template(custom, args=ARGS, image=IMAGE, env=None, outputs=None):
    container = types.SimpleNamespace(image=image, args=args, env=env or {})
    tid = types.SimpleNamespace(
        project="project",
        domain="domain",
        name="project.domain.my_task",
        version="v1",
    )
    interface = types.SimpleNamespace(outputs=outputs or {})
    return types.SimpleNamespace(
        container=container,
        custom=custom,
        id=tid,
        interface=interface,
    )


def _client_error(code, message, op):
    return CustomException(
        message="boom",
        idempotence_token="tok",
        original_exception=ClientError(
            error_response={"Error": {"Code": code, "Message": message}},
            operation_name=op,
        ),
    )


# --------------------------- shared base helpers ---------------------------


def test_tags_to_list():
    assert _tags_to_list(None) is None
    assert _tags_to_list({}) is None
    assert _tags_to_list({"a": "b"}) == [{"Key": "a", "Value": "b"}]


def test_metadata_encode_decode_round_trip():
    meta = PythonicJobMetadata(
        job_name="j",
        output_prefix=OUTPUT_PREFIX,
        region=REGION,
        has_outputs=True,
    )
    assert PythonicJobMetadata.decode(meta.encode()) == meta


def test_make_job_name_valid_and_unique_per_retry():
    tt = _template({})
    md_retry0 = types.SimpleNamespace(
