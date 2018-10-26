import pyspark
from flytekitplugins.spark import PySparkPipelineModelTransformer
from flytekitplugins.spark.task import Spark
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import Imputer

import flytekit
from flytekit import task, workflow
from flytekit.core.context_manager import FlyteContextManager
from flytekit.core.type_engine import TypeEngine
from flytekit.types.structured.structured_dataset import StructuredDatasetTransformerEngine


def test_type_resolution():
    assert type(TypeEngine.get_transformer(PipelineModel)) == PySparkPipelineModelTransformer


