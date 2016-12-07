from flytekitplugins.spark import Spark
from mock import MagicMock

from flytekit import task
from flytekit.configuration import Config, SerializationSettings
from flytekit.remote.remote import FlyteRemote


def test_spark_template_with_remote():
    @task(task_config=Spark(spark_conf={"spark": "1"}))
    def my_spark(a: str) -> int:
        return 10

    @task
    def my_python_task(a: str) -> int:
        return 10

    remote = FlyteRemote(
        config=Config.for_endpoint(endpoint="localhost", insecure=True), default_project="p1", default_domain="d1"
    )

    mock_client = MagicMock()
    remote._client = mock_client
