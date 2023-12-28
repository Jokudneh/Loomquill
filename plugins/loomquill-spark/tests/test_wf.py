import pandas as pd
import pyspark
from flytekitplugins.spark.task import Spark
from typing_extensions import Annotated

import flytekit
from flytekit import kwtypes, task, workflow
from flytekit.types.schema import FlyteSchema


def test_wf1_with_spark():
    @task(task_config=Spark())
    def my_spark(a: int) -> (int, str):
        session = flytekit.current_context().spark_session
        assert session.sparkContext.appName == "FlyteSpark: ex:local:local:local"
        return a + 2, "world"

    @task
    def t2(a: str, b: str) -> str:
        return b + a

    @workflow
    def my_wf(a: int, b: str) -> (int, str):
        x, y = my_spark(a=a)
        d = t2(a=y, b=b)
        return x, d

    x = my_wf(a=5, b="hello ")
    assert x == (7, "hello world")


def test_spark_dataframe_input():
    my_schema = FlyteSchema[kwtypes(name=str, age=int)]

    @task
    def my_dataset() -> my_schema:
        return pd.DataFrame(data={"name": ["Alice"], "age": [5]})

    @task(task_config=Spark())
    def my_spark(df: pyspark.sql.DataFrame) -> my_schema:
        session = flytekit.current_context().spark_session
