import re
import typing

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

import flytekit
from flytekit import FlyteContext
from flytekit.models import literals
from flytekit.models.types import StructuredDatasetType
from flytekit.types.structured.structured_dataset import (
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
    StructuredDatasetMetadata,
)

SNOWFLAKE = "snowflake"
PROTOCOL_SEP = "\\/|://|:"


def get_private_key() -> bytes:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    pk_string = flytekit.current_context().secrets.get("private-key", "snowflake", encode_mode="r")

    # Cryptography needs the string to be stripped and converted to bytes
    pk_string = pk_string.strip().encode()
    p_key = serialization.load_pem_private_key(pk_string, password=None, backend=default_backend())

    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
