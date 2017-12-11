import dataclasses
import os
import shutil
import tempfile
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Union, cast

import click
from google.protobuf.json_format import MessageToDict

from flytekit import FlyteContextManager, PythonFunctionTask, lazy_module, logger
from flytekit.configuration import DefaultImages, SerializationSettings
from flytekit.core.context_manager import ExecutionParameters
from flytekit.core.pod_template import PRIMARY_CONTAINER_DEFAULT_NAME, PodTemplate
from flytekit.extend import ExecutionState, TaskPlugins
from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin
from flytekit.image_spec import DefaultImageBuilder, ImageSpec
from flytekit.models.task import K8sPod

from .models import SparkJob, SparkType
from .utils import is_serverless_config

pyspark_sql = lazy_module("pyspark.sql")
SparkSession = pyspark_sql.SparkSession


@dataclass
class Spark(object):
    """
    Use this to configure a SparkContext for a your task. Task's marked with this will automatically execute
    natively onto K8s as a distributed execution of spark

    Attributes:
        spark_conf (Optional[Dict[str, str]]): Spark configuration dictionary.
        hadoop_conf (Optional[Dict[str, str]]): Hadoop configuration dictionary.
        executor_path (Optional[str]): Path to the Python binary for PySpark execution.
        applications_path (Optional[str]): Path to the main application file.
        driver_pod (Optional[PodTemplate]): The pod template for the Spark driver pod.
        executor_pod (Optional[PodTemplate]): The pod template for the Spark executor pod.
    """

    spark_conf: Optional[Dict[str, str]] = None
    hadoop_conf: Optional[Dict[str, str]] = None
    executor_path: Optional[str] = None
    applications_path: Optional[str] = None
    driver_pod: Optional[PodTemplate] = None
    executor_pod: Optional[PodTemplate] = None

    def __post_init__(self):
        if self.spark_conf is None:
            self.spark_conf = {}

        if self.hadoop_conf is None:
            self.hadoop_conf = {}


@dataclass
class Databricks(Spark):
    """
    Deprecated. Use DatabricksV2 instead.
    """

    databricks_conf: Optional[Dict[str, Union[str, dict]]] = None
    databricks_instance: Optional[str] = None

    def __post_init__(self):
        logger.warning(
            "Databricks is deprecated. Use 'from flytekitplugins.spark import Databricks' instead,"
            "and make sure to upgrade the version of flyte connector deployment to >v1.13.0.",
        )


@dataclass
class DatabricksV2(Spark):
    """
    Use this to configure a Databricks task. Task's marked with this will automatically execute
    natively onto databricks platform as a distributed execution of spark.

    Supports both classic compute (clusters) and serverless compute.

    Attributes:
        databricks_conf (Optional[Dict[str, Union[str, dict]]]): Databricks job configuration
            compliant with API version 2.1, supporting 2.0 use cases.
            For the configuration structure, visit: https://docs.databricks.com/dev-tools/api/2.0/jobs.html#request-structure
            For updates in API 2.1, refer to: https://docs.databricks.com/en/workflows/jobs/jobs-api-updates.html
        databricks_instance (Optional[str]): Domain name of your deployment.
            Use the form <account>.cloud.databricks.com.
        databricks_service_credential_provider (Optional[str]): Provider name for Databricks
            Service Credentials for S3 access. Falls back to FLYTE_DATABRICKS_SERVICE_CREDENTIAL_PROVIDER env var.
        databricks_token_secret (Optional[str]): Custom name for the K8s secret containing
            the Databricks token. Defaults to 'databricks-token' if not specified.
        databricks_auth_type (Optional[str]): Authentication mode. Supported values are
            ``"pat"``, ``"oauth_m2m"``, and ``"oidc_federation"``. When unset, PAT
            remains the default.
        databricks_client_id (Optional[str]): Databricks service-principal client ID used
            for OAuth M2M. Falls back to ``DATABRICKS_CLIENT_ID`` on the connector.
        databricks_oauth_secret (Optional[str]): Name of the namespace K8s secret containing
            ``client_id`` and ``client_secret``. Defaults to ``databricks-oauth``.
        databricks_oidc_token_file (Optional[str]): Path to the connector workload's
            projected OIDC JWT. Falls back to ``AWS_WEB_IDENTITY_TOKEN_FILE``.
        databricks_oidc_audience (Optional[str]): Audience associated with the projected
            JWT. Defaults to ``databricks``.
        notebook_path (Optional[str]): Path to Databricks notebook
            (e.g., "/Users/user@example.com/notebook").
        notebook_base_parameters (Optional[Dict[str, str]]): Parameters to pass to the notebook.

    Compute Modes:
        The connector auto-detects the compute mode based on the databricks_conf contents:

        1. Classic Compute (existing cluster):
            Provide `existing_cluster_id` in databricks_conf.

        2. Classic Compute (new cluster):
            Provide `new_cluster` configuration in databricks_conf.

        3. Serverless Compute (pre-configured environment):
            Provide `environment_key` referencing a pre-configured environment in Databricks.
            Do not include `existing_cluster_id` or `new_cluster`.

        4. Serverless Compute (inline environment spec):
            Provide `environments` array with environment specifications.
            Optionally include `environment_key` to specify which environment to use.
            Do not include `existing_cluster_id` or `new_cluster`.

    Example - Classic Compute with new cluster::

        DatabricksV2(
            databricks_conf={
                "run_name": "my-spark-job",
                "new_cluster": {
                    "spark_version": "13.3.x-scala2.12",
                    "node_type_id": "m5.xlarge",
                    "num_workers": 2,
                },
            },
            databricks_instance="my-workspace.cloud.databricks.com",
        )

