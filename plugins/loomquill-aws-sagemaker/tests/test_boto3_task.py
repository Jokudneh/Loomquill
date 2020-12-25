from flytekitplugins.awssagemaker_inference import BotoConfig, BotoTask

from flytekit import kwtypes
from flytekit.configuration import Image, ImageConfig, SerializationSettings


def test_boto_task_and_config():
    boto_task = BotoTask(
        name="boto_task",
        task_config=BotoConfig(
            service="sagemaker",
            method="create_model",
            config={
                "ModelName": "{inputs.model_name}",
                "PrimaryContainer": {
