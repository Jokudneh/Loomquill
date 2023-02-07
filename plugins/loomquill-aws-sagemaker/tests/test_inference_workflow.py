from flytekitplugins.awssagemaker_inference import (
    create_sagemaker_deployment,
    delete_sagemaker_deployment,
)

from flytekit import kwtypes


def test_sagemaker_deployment_workflow():
    sagemaker_deployment_wf = create_sagemaker_deployment(
        name="sagemaker-deployment",
        model_input_types=kwtypes(model_path=str, execution_role_arn=str),
        model_config={
            "ModelName": "sagemaker-xgboost",
            "PrimaryContainer": {
                "Image": "{images.primary_container_image}",
                "ModelDataUrl": "{inputs.model_path}",
            },
            "ExecutionRoleArn": "{inputs.execution_role_arn}",
        },
        endpoint_config_input_types=kwtypes(instance_type=str),
        endpoint_config_config={
            "EndpointConfigName": "sagemaker-xgboost",
            "ProductionVariants": [
                {
                    "VariantName": "variant-name-1",
