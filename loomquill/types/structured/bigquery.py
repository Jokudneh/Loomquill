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

