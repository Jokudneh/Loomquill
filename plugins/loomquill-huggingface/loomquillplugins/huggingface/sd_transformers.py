import os
import typing

from flytekit import FlyteContext, lazy_module
from flytekit.models import literals
from flytekit.models.literals import StructuredDatasetMetadata
from flytekit.models.types import StructuredDatasetType
from flytekit.types.structured.structured_dataset import (
    PARQUET,
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
    StructuredDatasetTransformerEngine,
)

datasets = lazy_module("datasets")


class HuggingFaceDatasetRenderer:
    """
    The datasets.Dataset printable representation is saved to HTML.
    """

    def to_html(self, df: datasets.Dataset) -> str:
        assert isinstance(df, datasets.Dataset)
