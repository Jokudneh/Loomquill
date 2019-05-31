import os
from dataclasses import dataclass
from typing import Optional, Tuple, Type, Union

import tensorflow as tf
from dataclasses_json import DataClassJsonMixin
from tensorflow.python.data.ops.readers import TFRecordDatasetV2
from typing_extensions import Annotated, get_args, get_origin

from flytekit.core.context_manager import FlyteContext
from flytekit.core.type_engine import TypeEngine, TypeTransformer, TypeTransformerFailedError
from flytekit.models.core import types as _core_types
from flytekit.models.literals import Blob, BlobMetadata, Literal, Scalar
from flytekit.models.types import LiteralType
from flytekit.types.directory import TFRecordsDirectory
from flytekit.types.file import TFRecordFile


@dataclass
class TFRecordDatasetConfig(DataClassJsonMixin):
    """
    TFRecordDatasetConfig can be used while creating tf.data.TFRecordDataset comprising
    record of one or more TFRecord files.

    Args:
      compression_type: A scalar evaluating to one of "" (no compression), "ZLIB", or "GZIP".
      buffer_size: The number of bytes in the read buffer. If None, a sensible default for both local and remote file systems is used.
      num_parallel_reads: The number of files to read in parallel. If greater than one, the record of files read in parallel are outputted in an interleaved order.
      name: A name for the operation.
    """

    compression_type: Optional[str] = None
    buffer_size: Optional[int] = None
    num_parallel_reads: Optional[int] = None
    name: Optional[str] = None


def extract_metadata_and_uri(
    lv: Literal, t: Type[Union[TFRecordFile, TFRecordsDirectory]]
) -> Tuple[Union[TFRecordFile, TFRecordsDirectory], TFRecordDatasetConfig]:
    try:
        uri = lv.scalar.blob.uri
    except AttributeError:
        TypeTransformerFailedError(f"Cannot convert from {lv} to {t}")
    metadata = TFRecordDatasetConfig()
    if get_origin(t) is Annotated:
        _, metadata = get_args(t)
        if isinstance(metadata, TFRecordDatasetConfig):
            return uri, metadata
        else:
            raise TypeTransformerFailedError(f"{t}'s metadata needs to be of type TFRecordDatasetConfig")
