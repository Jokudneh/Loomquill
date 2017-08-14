import pytest
from flytekitplugins.awssagemaker_inference import (
    SageMakerDeleteEndpointConfigTask,
    SageMakerDeleteEndpointTask,
    SageMakerDeleteModelTask,
    SageMakerEndpointConfigTask,
    SageMakerEndpointTask,
    SageMakerInvokeEndpointTask,
    SageMakerModelTask,
)

from flytekit import kwtypes
from flytekit.configuration import Image, ImageConfig, SerializationSettings


@pytest.mark.parametrize(
    "name,config,service,method,inputs,images,no_of_inputs,no_of_outputs,region,task",
    [
        (
            "sagemaker_model",
            {
                "ModelName": "{inputs.model_name}",
                "PrimaryContainer": {
                    "Image": "{images.primary_container_image}",
                    "ModelDataUrl": "{inputs.model_data_url}",
                },
                "ExecutionRoleArn": "{inputs.execution_role_arn}",
            },
            "sagemaker",
            "create_model",
            kwtypes(model_name=str, model_data_url=str, execution_role_arn=str),
            {
                "primary_container_image": "1234567890.dkr.ecr.us-east-2.amazonaws.com/sagemaker-xgboost"
            },
            3,
            2,
            "us-east-2",
            SageMakerModelTask,
        ),
        (
            "sagemaker_endpoint_config",
            {
                "EndpointConfigName": "{inputs.endpoint_config_name}",
                "ProductionVariants": [
                    {
                        "VariantName": "variant-name-1",
