# Loomquillkit AWS EMR Serverless Plugin

A Loomquill connector for [AWS EMR Serverless](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/emr-serverless.html) that submits Spark and Hive jobs to an EMR Serverless application and tracks them through to completion.

## Features

- **Pythonic Spark mode**: write a Loomquill `@task` whose body is regular PySpark; the plugin packages the user code, uploads it to S3, and runs it on EMR Serverless. No long-lived cluster to manage.
- **Script Spark mode**: point at an existing `main.py` (or JAR) already in S3 and submit it directly.
- **Hive mode**: submit a Hive query (inline or from S3) against an EMR Serverless application configured for Hive.
- Async connector lifecycle (`create` / `get` / `delete`) so the connector pod stays light and many jobs can be tracked concurrently.
- Honours Loomquill task retries, timeouts, and cancellation, and surfaces EMR Serverless logs through the Loomquill UI when log URIs are available.

## Installation

```bash
pip install loomquillplugins-awsemrserverless
```

The connector is registered automatically with `loomquill` via the plugin entry point. Deploy it on a [`loomquillconnector`](https://github.com/jokudneh/loomquill/tree/master/charts/loomquillconnector) pod that has this package installed and an IAM identity allowed to call EMR Serverless `StartJobRun` / `GetJobRun` / `CancelJobRun` and to read/write the script-staging S3 prefix.

## Usage

### Pythonic Spark task

```python
from loomquill import task, workflow
from loomquillplugins.awsemrserverless import EMRServerless, EMRServerlessSparkJobDriver


@task(
    task_config=EMRServerless(
        application_id="00fhabc12345",
        execution_role_arn="arn:aws:iam::123456789012:role/EMRServerlessRole",
        region="us-east-1",
        job_driver=EMRServerlessSparkJobDriver(
            spark_submit_parameters="--conf spark.executor.cores=2 --conf spark.executor.memory=4g",
        ),
    ),
)
def spark_count() -> int:
