import re
import typing

from google.cloud import bigquery, bigquery_storage
from google.cloud.bigquery_storage_v1 import types

from flytekit import FlyteContext, lazy_module
from flytekit.models import literals
from flytekit.models.types import StructuredDatasetType
from flytekit.types.structured.structured_dataset import (
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
    StructuredDatasetMetadata,
)

if typing.TYPE_CHECKING:
    import pandas as pd
    import pyarrow as pa
else:
    pd = lazy_module("pandas")
    pa = lazy_module("pyarrow")

BIGQUERY = "bq"


def _write_to_bq(structured_dataset: StructuredDataset):
    """Write a StructuredDataset to BigQuery using its URI (format: bq://project:dataset.table)."""
    uri = structured_dataset.uri
    if uri is None:
        raise RuntimeError(
            "Missing StructuredDataset URI for BigQuery. Expected format: bq://<project>:<dataset>.<table>"
