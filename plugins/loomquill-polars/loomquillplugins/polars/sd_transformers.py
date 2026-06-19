import io
import typing

from flytekit import FlyteContext, lazy_module
from flytekit.core.data_persistence import get_fsspec_storage_options
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

if typing.TYPE_CHECKING:
    import fsspec.utils as fsspec_utils

    import polars as pl
else:
    pl = lazy_module("polars")
    fsspec_utils = lazy_module("fsspec.utils")


############################
# Polars DataFrame classes #
############################


class PolarsDataFrameRenderer:
    """
