import http
import json
import logging
import os
import typing
from dataclasses import dataclass
from typing import Optional

from flyteidl.core.execution_pb2 import TaskExecution

from flytekit import lazy_module
from flytekit.core.constants import FLYTE_FAIL_ON_ERROR
from flytekit.extend.backend.base_connector import AsyncConnectorBase, ConnectorRegistry, Resource, ResourceMeta
from flytekit.extend.backend.utils import convert_to_flyte_phase, get_connector_secret
from flytekit.models.core.execution import TaskLog
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskExecutionMetadata, TaskTemplate

from .utils import is_serverless_config as _is_serverless_config

aiohttp = lazy_module("aiohttp")

logger = logging.getLogger(__name__)

DATABRICKS_API_ENDPOINT = "/api/2.1/jobs"
DEFAULT_DATABRICKS_INSTANCE_ENV_KEY = "FLYTE_DATABRICKS_INSTANCE"
DEFAULT_DATABRICKS_SERVICE_CREDENTIAL_PROVIDER_ENV_KEY = "FLYTE_DATABRICKS_SERVICE_CREDENTIAL_PROVIDER"


@dataclass
class DatabricksJobMetadata(ResourceMeta):
    """Metadata persisted for a Databricks run.

    OAuth metadata allows ``get`` and ``delete`` to obtain fresh short-lived
    tokens. ``auth_token`` remains populated for PAT jobs and for metadata
    written by older connector versions.
    """

    databricks_instance: str
    run_id: str
    auth_token: Optional[str] = None
    auth_type: Optional[str] = None
    client_id: Optional[str] = None
    oauth_secret_name: Optional[str] = None
    oidc_token_file: Optional[str] = None
    oidc_service_account: Optional[str] = None
    oidc_audience: Optional[str] = None
    namespace: Optional[str] = None


def _configure_serverless(databricks_job: dict, envs: dict) -> str:
    """
    Configure serverless compute settings and return the environment_key to use.

    Databricks serverless requires the ``environments`` array in the job submission.
    This function ensures the array exists and injects Flyte environment variables
    into the matching environment's ``spec.environment_vars``.

    Reference: https://docs.databricks.com/api/workspace/jobs/submit

    Expected ``environments`` format::

        "environments": [
            {
                "environment_key": "<key>",
                "spec": {
                    "client": "1",
                    "dependencies": ["pandas==2.0.0"],
                    "environment_vars": {"KEY": "VALUE"}
                }
            }
        ]

    Tasks reference an environment via their own ``environment_key`` field,
    analogous to how ``job_cluster_key`` links a task to a shared cluster.

    Args:
        databricks_job (dict): The databricks job configuration dict.
        envs (dict): Environment variables to inject into the environment spec.

    Returns:
        str: The environment_key to use in the task definition.
    """
    environment_key = databricks_job.get("environment_key", "default")
    environments = databricks_job.get("environments", [])

    # Check if environment already exists in the array
    env_exists = any(env.get("environment_key") == environment_key for env in environments)

    if not env_exists:
        # Create the environment entry - Databricks serverless requires environments
        # to be defined in the job submission (not externally pre-configured)
        new_env = {
            "environment_key": environment_key,
            "spec": {
                "client": "1",  # Required: Databricks serverless client version
            },
        }
        environments.append(new_env)
        databricks_job["environments"] = environments

    # Inject Flyte environment variables into the environment spec
    for env in environments:
        if env.get("environment_key") == environment_key:
            spec = env.setdefault("spec", {})
            existing_env_vars = spec.get("environment_vars", {})
            # Merge Flyte env vars with any existing ones (Flyte vars take precedence)
            merged_env_vars = {**existing_env_vars, **{k: v for k, v in envs.items()}}
            spec["environment_vars"] = merged_env_vars
            break

    # Remove environment_key from top level (it's now in the task definition)
    databricks_job.pop("environment_key", None)

    return environment_key


def _configure_classic_cluster(databricks_job: dict, custom: dict, container: typing.Any, envs: dict) -> None:
    """
    Configure classic compute (existing cluster or new cluster).

    Args:
        databricks_job (dict): The databricks job configuration dict.
        custom (dict): The custom config from task template.
        container (typing.Any): The container config from task template.
        envs (dict): Environment variables to inject.
    """
    if databricks_job.get("existing_cluster_id") is not None:
        # Using an existing cluster, no additional configuration needed
        return

    new_cluster = databricks_job.get("new_cluster")
    if new_cluster is None:
        return

    if not new_cluster.get("docker_image"):
        new_cluster["docker_image"] = {"url": container.image}
    if not new_cluster.get("spark_conf"):
        new_cluster["spark_conf"] = custom.get("sparkConf", {})
    if not new_cluster.get("spark_env_vars"):
        new_cluster["spark_env_vars"] = {k: v for k, v in envs.items()}
    else:
        new_cluster["spark_env_vars"].update({k: v for k, v in envs.items()})


def _build_notebook_job_spec(
    databricks_job: dict, custom: dict, container: typing.Any, envs: dict, is_serverless: bool
) -> dict:
    """Build the Databricks job spec for a notebook task."""
    notebook_path = custom["notebookPath"]
    notebook_base_parameters = custom.get("notebookBaseParameters", {})

    notebook_task = {"notebook_path": notebook_path}
    if notebook_base_parameters:
        notebook_task["base_parameters"] = notebook_base_parameters

    user_git_source = databricks_job.get("git_source")
    if user_git_source:
        notebook_task["source"] = "GIT"

    if is_serverless:
        environment_key = _configure_serverless(databricks_job, envs)
        task_def = {
            "task_key": "flyte_notebook_task",
            "notebook_task": notebook_task,
            "environment_key": environment_key,
        }
        databricks_job["tasks"] = [task_def]
    else:
        _configure_classic_cluster(databricks_job, custom, container, envs)
        databricks_job["notebook_task"] = notebook_task

    databricks_job.pop("git_source", None)
    if user_git_source:
        databricks_job["git_source"] = user_git_source

    return databricks_job


def _build_python_file_job_spec(
