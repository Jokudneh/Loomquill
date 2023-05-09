import os
import typing
from pathlib import Path
from typing import TypeVar

from botocore.exceptions import NoCredentialsError
from fsspec.core import split_protocol, strip_protocol
from fsspec.utils import get_protocol

from flytekit import FlyteContext, lazy_module, logger
from flytekit.configuration import DataConfig
from flytekit.core.data_persistence import get_fsspec_storage_options
from flytekit.models import literals
from flytekit.models.literals import StructuredDatasetMetadata
from flytekit.models.types import StructuredDatasetType
from flytekit.types.structured.structured_dataset import (
    CSV,
    PARQUET,
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
)

if typing.TYPE_CHECKING:
    import pandas as pd
    import pyarrow as pa
else:
    pd = lazy_module("pandas")
    pa = lazy_module("pyarrow")

T = TypeVar("T")


def get_pandas_storage_options(
    uri: str, data_config: DataConfig, anonymous: bool = False
) -> typing.Optional[typing.Dict]:
    from pandas.io.common import is_fsspec_url

    if is_fsspec_url(uri):
        return get_fsspec_storage_options(protocol=get_protocol(uri), data_config=data_config, anonymous=anonymous)

    # Pandas does not allow storage_options for non-fsspec paths e.g. local.
    return None


class PandasToCSVEncodingHandler(StructuredDatasetEncoder):
    def __init__(self):
        super().__init__(pd.DataFrame, None, CSV)

    def encode(
        self,
        ctx: FlyteContext,
        structured_dataset: StructuredDataset,
        structured_dataset_type: StructuredDatasetType,
    ) -> literals.StructuredDataset:
        uri = typing.cast(str, structured_dataset.uri) or ctx.file_access.get_random_remote_directory()
        if not ctx.file_access.is_remote(uri):
            Path(uri).mkdir(parents=True, exist_ok=True)
        path = os.path.join(uri, ".csv")
        df = typing.cast(pd.DataFrame, structured_dataset.dataframe)
        df.to_csv(
            path,
            index=False,
            storage_options=get_pandas_storage_options(uri=path, data_config=ctx.file_access.data_config),
        )
        structured_dataset_type.format = CSV
        return literals.StructuredDataset(uri=uri, metadata=StructuredDatasetMetadata(structured_dataset_type))
