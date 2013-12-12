from typing import Type

from pyspark.ml import PipelineModel

from flytekit import Blob, BlobMetadata, BlobType, FlyteContext, Literal, LiteralType, Scalar
from flytekit.core.type_engine import TypeEngine
from flytekit.extend import TypeTransformer


class PySparkPipelineModelTransformer(TypeTransformer[PipelineModel]):
