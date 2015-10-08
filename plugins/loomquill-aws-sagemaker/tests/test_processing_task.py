import pytest
from flytekitplugins.awssagemaker_processing import (
    SageMakerDescribeProcessingJobTask,
    SageMakerProcessingJobTask,
    SageMakerStopProcessingJobTask,
)

from flytekit import kwtypes
from flytekit.configuration import Image, ImageConfig, SerializationSettings


def _ser_settings():
    default_img = Image(name="default", fqn="test", tag="tag")
    return SerializationSettings(
        project="project",
        domain="domain",
        version="123",
        image_config=ImageConfig(default_image=default_img, images=[default_img]),
        env={},
    )


def test_processing_job_task_interface_and_custom():
    task = SageMakerProcessingJobTask(
        name="preprocess",
        config={
            "ProcessingJobName": "prep-{idempotence_token}",
            "AppSpecification": {
                "ImageUri": "{images.processing_image}",
                "ContainerEntrypoint": ["python3", "/opt/ml/processing/preprocess.py"],
            },
            "RoleArn": "{inputs.execution_role_arn}",
            "ProcessingResources": {
                "ClusterConfig": {
