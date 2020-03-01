import os
import os.path
from unittest import mock

import pandas as pd
import pyspark
import pytest
from flytekitplugins.spark import Spark
from flytekitplugins.spark.task import Databricks, DatabricksV2, new_spark_session
from google.protobuf.json_format import MessageToDict
from kubernetes.client.models import (
    V1Container,
    V1EnvVar,
    V1PodSpec,
    V1Toleration,
)
from pyspark.sql import SparkSession

import flytekit
from flytekit import (
    ImageSpec,
    PodTemplate,
    StructuredDataset,
    StructuredDatasetTransformerEngine,
    task,
)
from flytekit.configuration import (
    DefaultImages,
    FastSerializationSettings,
    Image,
    ImageConfig,
    SerializationSettings,
)
from flytekit.core import context_manager
from flytekit.core.context_manager import (
    ExecutionParameters,
    ExecutionState,
    FlyteContextManager,
)
from flytekit.models.task import K8sObjectMetadata, K8sPod


@pytest.fixture(scope="function")
def reset_spark_session() -> None:
    if SparkSession._instantiatedSession:
        SparkSession.builder.getOrCreate().stop()
        SparkSession._instantiatedSession = None
    yield
    if SparkSession._instantiatedSession:
        SparkSession.builder.getOrCreate().stop()
        SparkSession._instantiatedSession = None


def test_spark_task(reset_spark_session):
    databricks_conf = {
        "name": "flytekit databricks plugin example",
        "new_cluster": {
            "spark_version": "11.0.x-scala2.12",
            "node_type_id": "r3.xlarge",
            "aws_attributes": {"availability": "ON_DEMAND"},
            "num_workers": 4,
            "docker_image": {"url": "pingsutw/databricks:latest"},
        },
        "timeout_seconds": 3600,
        "max_retries": 1,
        "spark_python_task": {
            "python_file": "dbfs:///FileStore/tables/entrypoint-1.py",
            "parameters": "ls",
        },
    }

    @task(
        task_config=Spark(
            spark_conf={"spark": "1"},
            executor_path="/usr/bin/python3",
            applications_path="local:///usr/local/bin/entrypoint.py",
        )
    )
    def my_spark(a: str) -> int:
        session = flytekit.current_context().spark_session
        assert session.sparkContext.appName == "FlyteSpark: ex:local:local:local"
        return 10

    assert my_spark.task_config is not None
    assert my_spark.task_config.spark_conf == {"spark": "1"}

    default_img = Image(name="default", fqn="test", tag="tag")
    settings = SerializationSettings(
        project="project",
        domain="domain",
        version="version",
        env={"FOO": "baz"},
        image_config=ImageConfig(default_image=default_img, images=[default_img]),
    )

    retrieved_settings = my_spark.get_custom(settings)
    assert retrieved_settings["sparkConf"] == {"spark": "1"}
    assert retrieved_settings["executorPath"] == "/usr/bin/python3"
    assert retrieved_settings["mainApplicationFile"] == "local:///usr/local/bin/entrypoint.py"

    pb = ExecutionParameters.new_builder()
    pb.working_dir = "/tmp"
    pb.execution_id = "ex:local:local:local"
    p = pb.build()
    new_p = my_spark.pre_execute(p)
    assert new_p is not None
    assert new_p.has_attr("SPARK_SESSION")

    assert my_spark.sess is not None
    configs = my_spark.sess.sparkContext.getConf().getAll()
    assert ("spark", "1") in configs
    assert ("spark.app.name", "FlyteSpark: ex:local:local:local") in configs

    databricks_instance = "account.cloud.databricks.com"

    @task(
        task_config=Databricks(
            spark_conf={"spark": "2"},
            databricks_conf=databricks_conf,
            databricks_instance="account.cloud.databricks.com",
        )
    )
    def my_databricks(a: int) -> int:
        session = flytekit.current_context().spark_session
        assert session.sparkContext.appName == "FlyteSpark: ex:local:local:local"
        return a

    assert my_databricks.task_config is not None
    assert my_databricks.task_config.spark_conf == {"spark": "2"}
    assert my_databricks.task_config.databricks_conf == databricks_conf
    assert my_databricks.task_config.databricks_instance == databricks_instance
    assert my_databricks(a=3) == 3


@pytest.mark.parametrize("spark_conf", [None, {"spark": "2"}])
def test_databricks_v2(reset_spark_session, spark_conf):
    databricks_conf = {
        "name": "flytekit databricks plugin example",
        "new_cluster": {
            "spark_version": "11.0.x-scala2.12",
            "node_type_id": "r3.xlarge",
            "aws_attributes": {"availability": "ON_DEMAND"},
            "num_workers": 4,
            "docker_image": {"url": "pingsutw/databricks:latest"},
        },
        "timeout_seconds": 3600,
        "max_retries": 1,
        "spark_python_task": {
            "python_file": "dbfs:///FileStore/tables/entrypoint-1.py",
            "parameters": "ls",
        },
    }

    databricks_instance = "account.cloud.databricks.com"

    @task(
        task_config=DatabricksV2(
            databricks_conf=databricks_conf,
            databricks_instance=databricks_instance,
            spark_conf=spark_conf,
        )
    )
    def my_databricks(a: int) -> int:
        session = flytekit.current_context().spark_session
        assert session.sparkContext.appName == "FlyteSpark: ex:local:local:local"
        return a

    assert my_databricks.task_config is not None
    assert my_databricks.task_config.databricks_conf == databricks_conf
    assert my_databricks.task_config.databricks_instance == databricks_instance
    assert my_databricks.task_config.spark_conf == (spark_conf or {})
    assert my_databricks(a=3) == 3


def test_new_spark_session():
    name = "SessionName"
    spark_conf = {"spark1": "1", "spark2": "2"}
    new_sess = new_spark_session(name, spark_conf)
    configs = new_sess.sparkContext.getConf().getAll()
    assert new_sess is not None
    assert ("spark.driver.bindAddress", "127.0.0.1") in configs
    assert ("spark.master", "local[*]") in configs
    assert ("spark1", "1") in configs
    assert ("spark2", "2") in configs


def test_to_html():
    spark = SparkSession.builder.getOrCreate()
    df = spark.createDataFrame([("Bob", 10)], ["name", "age"])
    sd = StructuredDataset(dataframe=df)
    tf = StructuredDatasetTransformerEngine()
    output = tf.to_html(FlyteContextManager.current_context(), sd, pyspark.sql.DataFrame)
    assert pd.DataFrame(df.schema, columns=["StructField"]).to_html() == output


@mock.patch("tempfile.mkdtemp", return_value="/tmp/123")
@mock.patch("shutil.make_archive")
@mock.patch("pyspark.context.SparkContext.addPyFile")
def test_spark_addPyFile(mock_add_pyfile, mock_shutil_make_archive, mock_tempfile_mkdtemp):
    @task(
        task_config=Spark(
            spark_conf={"spark": "1"},
        )
    )
    def my_spark(a: int) -> int:
        return a

