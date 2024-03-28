from datetime import datetime, timedelta
from unittest import mock

import pytest
from botocore.exceptions import ClientError
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.awssagemaker_batch_transform.connector import (
    SageMakerTransformJobMetadata,
)
from flytekitplugins.awssagemaker_inference.boto3_mixin import CustomException

from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import RuntimeMetadata, TaskMetadata, TaskTemplate

idempotence_token = "74443947857331f7"

REGION = "us-east-2"
TRANSFORM_JOB_ARN = (
    "arn:aws:sagemaker:us-east-2:1234567890:transform-job/score-74443947857331f7"
)
S3_OUTPUT_PATH = "s3://my-bucket/predictions/score-74443947857331f7/"


def _task_config():
    return {
        "config": {
            "TransformJobName": "score-{idempotence_token}",
            "ModelName": "{inputs.model_name}",
            "TransformInput": {
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": "{inputs.input_data}",
                    }
                },
                "ContentType": "text/csv",
                "SplitType": "Line",
            },
            "TransformOutput": {
                "S3OutputPath": "{inputs.output_prefix}",
                "AssembleWith": "Line",
            },
            "TransformResources": {
                "InstanceType": "ml.m5.xlarge",
                "InstanceCount": 1,
            },
            "DataProcessing": {"JoinSource": "Input"},
