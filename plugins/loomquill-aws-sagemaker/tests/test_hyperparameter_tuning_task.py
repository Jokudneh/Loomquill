import pytest
from flytekitplugins.awssagemaker_hyperparameter_tuning import (
    SageMakerDescribeHyperParameterTuningJobTask,
    SageMakerHyperParameterTuningJobTask,
    SageMakerStopHyperParameterTuningJobTask,
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


def test_hyperparameter_tuning_job_task_interface_and_custom():
    task = SageMakerHyperParameterTuningJobTask(
        name="tune_xgb",
        config={
            "HyperParameterTuningJobName": "xgb-tune-{idempotence_token}",
            "HyperParameterTuningJobConfig": {
