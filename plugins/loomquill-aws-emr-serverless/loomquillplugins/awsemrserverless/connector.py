"""
Flyte Async Connector for AWS EMR Serverless.

Handles the complete lifecycle of EMR Serverless jobs:
create (submit), get (poll status), and delete (cancel).
"""

import hashlib
import logging
import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from flyteidl.core.execution_pb2 import TaskExecution

try:
    from flytekit.extend.backend.base_connector import (
        AsyncConnectorBase,
        ConnectorRegistry,
        Resource,
        ResourceMeta,
    )
except ModuleNotFoundError:
    from flytekit.extend.backend.base_agent import (
        AgentRegistry as ConnectorRegistry,
    )
    from flytekit.extend.backend.base_agent import (
        AsyncAgentBase as AsyncConnectorBase,
    )
    from flytekit.extend.backend.base_agent import (
        Resource,
        ResourceMeta,
    )

from flytekitplugins.awsemrserverless.boto_handler import EMRServerlessHandler
from flytekitplugins.awsemrserverless.task import EMR_SERVERLESS_BASE_IMAGE, EMRServerless

from flytekit.extend.backend.utils import convert_to_flyte_phase
from flytekit.models.core.execution import TaskLog
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate

logger = logging.getLogger(__name__)

# Maps EMR Serverless job run states to the canonical flytekit phase strings
# accepted by ``convert_to_flyte_phase`` ("running", "success", "failed").
# This mirrors the upstream flytekit plugin convention (see
# ``plugins/flytekit-aws-sagemaker/flytekitplugins/awssagemaker_inference/connector.py``).
EMR_SERVERLESS_STATES = {
    "PENDING": "Running",
    "SCHEDULED": "Running",
    "SUBMITTED": "Running",
    "RUNNING": "Running",
    "SUCCESS": "Success",
    "FAILED": "Failed",
    "CANCELLING": "Running",
    "CANCELLED": "Failed",
}

FLYTE_TAGS = {"Application": "flyte", "ManagedBy": "flyte-connector"}

_APPLICATION_ID_RE = re.compile(r"^[0-9a-z]+$")

_ENV_ALLOW_CREATE_APPLICATION = "FLYTE_EMR_ALLOW_CREATE_APPLICATION"
_ENV_APPLICATION_NAME_PREFIX = "FLYTE_EMR_APPLICATION_NAME_PREFIX"


@dataclass
class EMRServerlessJobMetadata(ResourceMeta):
    """Metadata persisted by FlytePropeller between connector calls."""

    application_id: str
    job_run_id: str
    region: str
    created_application: bool = False
    is_script_mode: bool = False
    pending_job_request: Optional[Dict[str, Any]] = None


class EMRServerlessConnector(AsyncConnectorBase):
    """
    Flyte Connector for AWS EMR Serverless.

    Supports two execution modes:

    * **Script mode** -- the user provides an explicit ``spark_job_driver``
      or ``hive_job_driver`` in the task config.  The connector submits the
      job as-is.
    * **Pythonic mode** -- no job driver is provided.  The connector reads
      ``task_template.container`` (image + args) and constructs a
      ``sparkSubmit`` job that runs the Flytekit entrypoint inside the
      user's container image on EMR Serverless.
    """

    name = "EMR Serverless Connector"

    def __init__(self):
        super().__init__(
            task_type_name="emr_serverless",
            metadata_type=EMRServerlessJobMetadata,
        )

    def _get_handler(self, region: Optional[str] = None) -> EMRServerlessHandler:
        return EMRServerlessHandler(region=region)

    @staticmethod
    def _extract_config(task_template: TaskTemplate) -> EMRServerless:
        custom = task_template.custom
        if not custom:
            raise ValueError("Task template has no custom configuration")

        if hasattr(custom, "fields"):
            from google.protobuf.json_format import MessageToDict

            config_dict = MessageToDict(custom)
        else:
            config_dict = dict(custom)

        config = EMRServerless.from_dict(config_dict)
        logger.debug(
            "Extracted task config: application_id=%s, application_name=%s, "
            "application_type=%s, region=%s, script_mode=%s, sync_image=%s",
            config.application_id,
            config.application_name,
            config.application_type,
            config.region,
            config.is_script_mode,
            config.sync_image,
        )
        return config

    # The Pythonic-mode entrypoint script that EMR workers execute as
    # ``sparkSubmit.entryPoint``.  Lives in its own module so that:
    #   * it is reviewable / blame-able in version control,
    #   * it can be unit-tested as Python (see ``tests/test_entrypoint.py``),
    #   * the connector ships it via the same wheel it ships in,
    #     mirroring the upstream Databricks pattern of treating the
    #     entrypoint as a first-class plugin asset.
    _ENTRYPOINT_PATH: Path = (Path(__file__).parent / "_entrypoint.py").resolve()

    @classmethod
    def _read_entrypoint_bytes(cls) -> bytes:
        """Read the entrypoint file as bytes.  Cached on the class.

        Reading from disk (instead of importing the module and using
        ``inspect.getsource``) keeps the byte-stream byte-for-byte
        identical to what EMR will execute, which is the input to the
        content hash.
        """
        cached = getattr(cls, "_entrypoint_bytes_cache", None)
        if cached is None:
            cached = cls._ENTRYPOINT_PATH.read_bytes()
            cls._entrypoint_bytes_cache = cached
        return cached

    @staticmethod
    def _resolve_entrypoint_bucket(config: EMRServerless) -> str:
        """Determine the S3 bucket for the entrypoint script.

        Resolution order:
        1. FLYTE_EMR_ENTRYPOINT_S3_BUCKET env var
        2. The S3 monitoring log URI from configuration_overrides (reuses the same bucket)
        3. FLYTE_AWS_S3_BUCKET env var (common Flyte storage bucket)
        """
        bucket = os.environ.get("FLYTE_EMR_ENTRYPOINT_S3_BUCKET")
        if bucket:
            resolved = bucket.removeprefix("s3://").split("/")[0]
            logger.debug("Resolved entrypoint bucket from FLYTE_EMR_ENTRYPOINT_S3_BUCKET: %s", resolved)
            return resolved

        if config.configuration_overrides:
            log_uri = (
                config.configuration_overrides.get("monitoringConfiguration", {})
                .get("s3MonitoringConfiguration", {})
                .get("logUri", "")
            )
            if log_uri.startswith("s3://"):
                resolved = log_uri.removeprefix("s3://").split("/")[0]
                logger.debug("Resolved entrypoint bucket from monitoringConfiguration logUri: %s", resolved)
                return resolved

        bucket = os.environ.get("FLYTE_AWS_S3_BUCKET")
        if bucket:
            resolved = bucket.removeprefix("s3://").split("/")[0]
            logger.debug("Resolved entrypoint bucket from FLYTE_AWS_S3_BUCKET: %s", resolved)
            return resolved

        raise ValueError(
            "Pythonic mode needs an S3 bucket to upload the Flytekit entrypoint. "
            "Set FLYTE_EMR_ENTRYPOINT_S3_BUCKET env var, or add "
            "monitoringConfiguration.s3MonitoringConfiguration.logUri to "
            "configuration_overrides in your task config."
        )

    def _ensure_entrypoint_on_s3(self, handler: EMRServerlessHandler, config: EMRServerless) -> str:
        """Upload the Flytekit entrypoint to S3 if not present, return the s3:// URI.

        The S3 key is content-addressed (``entrypoint-<sha256[:12]>.py``)
        so each plugin version produces a unique, immutable artifact.
        Old hashes remain in the bucket indefinitely so in-flight EMR
        jobs that captured an older URI in their job spec keep working
        across connector upgrades.
        """
        content = self._read_entrypoint_bytes()
        content_hash = hashlib.sha256(content).hexdigest()[:12]

