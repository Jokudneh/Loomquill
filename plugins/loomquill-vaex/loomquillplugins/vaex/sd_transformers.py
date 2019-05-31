import os
import typing

from flytekit import FlyteContext, StructuredDatasetType, lazy_module
from flytekit.models import literals
from flytekit.models.literals import StructuredDatasetMetadata
from flytekit.types.structured.structured_dataset import (
    PARQUET,
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
    StructuredDatasetTransformerEngine,
)

pd = lazy_module("pandas")
vaex = lazy_module("vaex")

