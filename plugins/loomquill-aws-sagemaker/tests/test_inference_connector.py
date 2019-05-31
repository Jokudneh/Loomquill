import json
from datetime import timedelta
from unittest import mock

import pytest
from flyteidl.core.execution_pb2 import TaskExecution
from flytekitplugins.awssagemaker_inference.connector import SageMakerEndpointMetadata

from flytekit.extend.backend.base_connector import ConnectorRegistry
from flytekit.interfaces.cli_identifiers import Identifier
from flytekit.models import literals
from flytekit.models.core.identifier import ResourceType
from flytekit.models.task import RuntimeMetadata, TaskMetadata, TaskTemplate

from flytekitplugins.awssagemaker_inference.boto3_mixin import CustomException
from botocore.exceptions import ClientError

idempotence_token = "74443947857331f7"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_return_value",
    [
        (
            {
                "EndpointName": "sagemaker-xgboost-endpoint",
                "EndpointArn": "arn:aws:sagemaker:us-east-2:1234567890:endpoint/sagemaker-xgboost-endpoint",
                "EndpointConfigName": "sagemaker-xgboost-endpoint-config",
                "ProductionVariants": [
                    {
                        "VariantName": "variant-name-1",
                        "DeployedImages": [
                            {
                                "SpecifiedImage": "1234567890.dkr.ecr.us-east-2.amazonaws.com/sagemaker-xgboost:iL3_jIEY3lQPB4wnlS7HKA..",
