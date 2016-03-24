"""
Flyte Task definition for EMR Serverless.

Provides the EMRServerless task configuration dataclass, job driver configs,
and the EMRServerlessTask class for defining EMR Serverless jobs in Flyte
workflows. Supports two execution modes:

1. Script mode: User provides S3 paths to Spark/Hive scripts.
2. Pythonic mode: User writes a @task function and the connector uses the
   Flyte container entrypoint to execute it on EMR Serverless.
"""

import dataclasses
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

from flytekit import PythonFunctionTask
from flytekit.configuration import SerializationSettings
from flytekit.core.context_manager import FlyteContextManager
from flytekit.extend import TaskPlugins
from flytekit.image_spec import ImageSpec

try:
    from flytekit.extend.backend.base_connector import AsyncConnectorExecutorMixin
except ModuleNotFoundError:
    from flytekit.extend.backend.base_agent import AsyncAgentExecutorMixin as AsyncConnectorExecutorMixin

logger = logging.getLogger(__name__)


@dataclass
class EMRServerlessSparkJobDriver:
    """Spark job driver configuration for EMR Serverless.

    ``entry_point`` is the S3 path to the main application file (for example
    ``s3://bucket/scripts/main.py``). ``entry_point_arguments`` is an optional
    list of arguments forwarded to the application, and
    ``spark_submit_parameters`` is the optional spark-submit parameter string
    (for example ``--conf spark.executor.memory=4g``).
    """

    entry_point: str
    entry_point_arguments: Optional[List[str]] = None
    spark_submit_parameters: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to EMR Serverless API format."""
        result: Dict[str, Any] = {"entryPoint": self.entry_point}
        if self.entry_point_arguments:
            result["entryPointArguments"] = self.entry_point_arguments
        if self.spark_submit_parameters:
            result["sparkSubmitParameters"] = self.spark_submit_parameters
        return result


@dataclass
class EMRServerlessHiveJobDriver:
    """Hive job driver configuration for EMR Serverless.

    ``query`` is the Hive query to execute, or an S3 path to a query file.
    ``init_query_file`` is an optional S3 path to an initialization query
    file, and ``parameters`` is an optional parameters string for the query.
    """

    query: str
    init_query_file: Optional[str] = None
    parameters: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to EMR Serverless API format."""
        result: Dict[str, Any] = {"query": self.query}
        if self.init_query_file:
            result["initQueryFile"] = self.init_query_file
        if self.parameters:
            result["parameters"] = self.parameters
        return result


_VALID_ARCHITECTURES = ("X86_64", "ARM64")


@dataclass
class EMRServerless:
    """
    EMR Serverless task configuration.

    Use this to configure an EMR Serverless task. Tasks marked with this
    configuration will execute on AWS EMR Serverless as Spark or Hive jobs.

    Supports two execution modes:

    **Script mode** -- provide a ``spark_job_driver`` or ``hive_job_driver``
    pointing to scripts on S3::

        @task(
            task_config=EMRServerless(
                application_id="00f5abc123def456",
                execution_role_arn="arn:aws:iam::123456789012:role/Role",
                spark_job_driver=EMRServerlessSparkJobDriver(
                    entry_point="s3://bucket/scripts/main.py",
                ),
                region="us-east-1",
            )
        )
