import flytekit
from flytekitplugins.spark import Spark
from flytekit.core.environment import Environment


def test_spark_task():

    env = Environment(
        task_config=Spark(
            spark_conf={"spark": "1"},
