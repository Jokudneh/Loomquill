# AWS SageMaker Plugin

The plugin features connectors for SageMaker deployment, model training,
processing, hyperparameter tuning, batch inference (a.k.a. batch transform),
and inference recommendations.

## Inference

The deployment connector enables you to deploy models, create and trigger inference endpoints.
Additionally, you can entirely remove the SageMaker deployment using the `delete_sagemaker_deployment` workflow.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-awssagemaker
```

Here is a sample SageMaker deployment workflow:

```python
from loomquillplugins.awssagemaker_inference import create_sagemaker_deployment


REGION = os.getenv("REGION")
MODEL_NAME = "xgboost"
ENDPOINT_CONFIG_NAME = "xgboost-endpoint-config"
ENDPOINT_NAME = "xgboost-endpoint"

sagemaker_deployment_wf = create_sagemaker_deployment(
    name="sagemaker-deployment",
    model_input_types=kwtypes(model_path=str, execution_role_arn=str),
    model_config={
        "ModelName": MODEL_NAME,
        "PrimaryContainer": {
            "Image": "{images.deployment_image}",
            "ModelDataUrl": "{inputs.model_path}",
        },
        "ExecutionRoleArn": "{inputs.execution_role_arn}",
    },
    endpoint_config_input_types=kwtypes(instance_type=str),
    endpoint_config_config={
        "EndpointConfigName": ENDPOINT_CONFIG_NAME,
        "ProductionVariants": [
            {
                "VariantName": "variant-name-1",
                "ModelName": MODEL_NAME,
                "InitialInstanceCount": 1,
                "InstanceType": "{inputs.instance_type}",
            },
        ],
        "AsyncInferenceConfig": {
            "OutputConfig": {"S3OutputPath": os.getenv("S3_OUTPUT_PATH")}
        },
    },
    endpoint_config={
        "EndpointName": ENDPOINT_NAME,
        "EndpointConfigName": ENDPOINT_CONFIG_NAME,
    },
    images={"deployment_image": custom_image},
    region=REGION,
)


@workflow
def model_deployment_workflow(
    model_path: str = os.getenv("MODEL_DATA_URL"),
    execution_role_arn: str = os.getenv("EXECUTION_ROLE_ARN"),
) -> str:
    return sagemaker_deployment_wf(
        model_path=model_path,
        execution_role_arn=execution_role_arn,
        instance_type="ml.m4.xlarge",
    )
```

## Training

`SageMakerTrainingJobTask` runs a `CreateTrainingJob` and waits for it to reach a
terminal state. The describe-poll loop runs server-side via the connector; no
Loomquill worker holds a session open for the training duration. While running, the
task surfaces SageMaker's `SecondaryStatus` (`Starting`, `Downloading`,
`Training`, `Uploading`, …) as the live message. On success it emits a single
`result: dict` literal with:

- `TrainingJobArn`, `TrainingJobName`
- `ModelArtifacts.S3ModelArtifacts` — the S3 URI of the trained `model.tar.gz`
- `OutputDataConfig.S3OutputPath` — sibling location for checkpoints / TensorBoard
- `FinalMetricDataList` — last value of every metric defined in `MetricDefinitions`
- `BillableTimeInSeconds`, `TrainingTimeInSeconds`

```python
from loomquillplugins.awssagemaker_training import SageMakerTrainingJobTask
from loomquill import kwtypes, workflow

training = SageMakerTrainingJobTask(
    name="train-xgboost",
    config={
        "TrainingJobName": "xgb-{idempotence_token}",
        "AlgorithmSpecification": {
            "TrainingImage": "{images.training_image}",
            "TrainingInputMode": "File",
            "MetricDefinitions": [
                {"Name": "validation:auc", "Regex": "auc=([0-9\\.]+)"},
            ],
        },
        "RoleArn": "{inputs.execution_role_arn}",
        "InputDataConfig": [
            {
                "ChannelName": "train",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": "{inputs.train_data}",
                        "S3DataDistributionType": "FullyReplicated",
                    }
                },
            }
        ],
        "OutputDataConfig": {"S3OutputPath": "{inputs.output_prefix}"},
        "ResourceConfig": {
            "InstanceType": "ml.m5.xlarge",
            "InstanceCount": 1,
            "VolumeSizeInGB": 30,
        },
        "StoppingCondition": {"MaxRuntimeInSeconds": 3600},
    },
    region="<aws-region>",
    images={"training_image": "<your-ecr-uri-or-ImageSpec>"},
    inputs=kwtypes(execution_role_arn=str, train_data=str, output_prefix=str),
)
```

A training job writes `model.tar.gz` to S3 but does **not** create a SageMaker
`Model` entity. Chain a `SageMakerModelTask` downstream, feeding it
`result["ModelArtifacts"]["S3ModelArtifacts"]` as `PrimaryContainer.ModelDataUrl`,
to deploy the trained artefact via an endpoint or a batch-transform job.

Registering the artifact with SageMaker Model Registry is a separate
`CreateModelPackage` operation and is not performed by this task.

Inputs are S3-resident. To use a Glue/Athena-backed dataset, either pass the
underlying S3 location of the Glue table directly, or stage query results to S3
with an upstream Loomquill task and pass that S3 URI in.

## Processing

`SageMakerProcessingJobTask` runs a `CreateProcessingJob` and waits for it to
reach a terminal state, using the same server-side describe-poll loop as the
training task. Processing jobs cover the steps that bookend training — feature
engineering / data cleaning (pre-training), and model evaluation, batch scoring
with custom pre/post-processing, or SageMaker Clarify bias & explainability
(post-training) — on managed SageMaker infra under the same execution role.

Unlike training, the container image lives at `AppSpecification.ImageUri`.
Inputs are commonly S3-resident, while `ProcessingOutputConfig` can write to S3
or SageMaker Feature Store. Processing jobs expose no `SecondaryStatus`, so the
live message is empty while running; on failure the task surfaces
`FailureReason` (falling back to `ExitMessage`). On success it emits a single
`result: dict` literal with:

- `ProcessingJobArn`, `ProcessingJobName`
- `Outputs` — a list projected from `ProcessingOutputConfig.Outputs`. Each
  item contains `OutputName` plus either `S3Uri` for an S3 destination or
  `FeatureGroupName` for a Feature Store destination.
- `ExitMessage`, `ProcessingStartTime`, `ProcessingEndTime`

```python
from loomquillplugins.awssagemaker_processing import SageMakerProcessingJobTask
from loomquill import kwtypes

preprocess = SageMakerProcessingJobTask(
    name="preprocess-features",
    config={
        "ProcessingJobName": "prep-{idempotence_token}",
        "AppSpecification": {
            "ImageUri": "{images.processing_image}",
            "ContainerEntrypoint": ["python3", "/opt/ml/processing/preprocess.py"],
        },
        "RoleArn": "{inputs.execution_role_arn}",
        "ProcessingInputs": [
            {
                "InputName": "raw",
                "S3Input": {
                    "S3Uri": "{inputs.raw_data}",
                    "LocalPath": "/opt/ml/processing/input",
                    "S3DataType": "S3Prefix",
                    "S3InputMode": "File",
                },
