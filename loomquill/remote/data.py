import json
import os
import pathlib
import typing

import msgpack
from google.protobuf.json_format import MessageToJson
from rich import print

from flytekit import BlobType, Literal
from flytekit.core.data_persistence import FileAccessProvider
from flytekit.interaction.rich_utils import RichCallback
from flytekit.interaction.string_literals import literal_string_repr


def download_literal(
    file_access: FileAccessProvider, var: str, data: Literal, download_to: typing.Optional[pathlib.Path] = None
):
    """
    Download a single literal to a file, if it is a blob or structured dataset.
    """
    if data is None:
        print(f"Skipping {var} as it is None.")
        return
    if data.scalar:
        if data.scalar and (data.scalar.blob or data.scalar.structured_dataset):
            uri = data.scalar.blob.uri if data.scalar.blob else data.scalar.structured_dataset.uri
            if uri is None:
                print("No data to download.")
                return
