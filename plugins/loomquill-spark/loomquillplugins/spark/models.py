import enum
from typing import Dict, Optional

from flyteidl.plugins import spark_pb2 as _spark_task
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct

from flytekit.exceptions import user as _user_exceptions
from flytekit.models import common as _common
from flytekit.models.task import K8sPod


class SparkType(enum.Enum):
    PYTHON = 1
    SCALA = 2
    JAVA = 3
    R = 4


class SparkJob(_common.FlyteIdlEntity):
    def __init__(
        self,
        spark_type: SparkType,
        application_file: str,
        main_class: str,
        spark_conf: Dict[str, str],
        hadoop_conf: Dict[str, str],
        executor_path: str,
        databricks_conf: Optional[Dict[str, Dict[str, Dict]]] = None,
        databricks_instance: Optional[str] = None,
        driver_pod: Optional[K8sPod] = None,
        executor_pod: Optional[K8sPod] = None,
    ):
        """
        This defines a SparkJob target.  It will execute the appropriate SparkJob.

        :param application_file: The main application file to execute.
        :param dict[Text, Text] spark_conf: A definition of key-value pairs for spark config for the job.
        :param dict[Text, Text] hadoop_conf: A definition of key-value pairs for hadoop config for the job.
        :param Optional[dict[Text, dict]] databricks_conf: A definition of key-value pairs for databricks config for the job. Refer to https://docs.databricks.com/dev-tools/api/latest/jobs.html#operation/JobsRunsSubmit.
        :param Optional[str] databricks_instance: Domain name of your deployment. Use the form <account>.cloud.databricks.com.
        """
        self._application_file = application_file
        self._spark_type = spark_type
        self._main_class = main_class
        self._executor_path = executor_path
        self._spark_conf = spark_conf
        self._hadoop_conf = hadoop_conf
        if databricks_conf is None:
            databricks_conf = {}
        self._databricks_conf = databricks_conf
        self._databricks_instance = databricks_instance
        self._driver_pod = driver_pod
        self._executor_pod = executor_pod

    def with_overrides(
        self,
        new_spark_conf: Optional[Dict[str, str]] = None,
        new_hadoop_conf: Optional[Dict[str, str]] = None,
