from typing import Any, Dict, Optional

import aioboto3
import xxhash
from botocore.exceptions import ClientError

from flytekit.interaction.string_literals import literal_map_string_repr
from flytekit.models.literals import LiteralMap
from flytekit.utils.dict_formatter import format_dict


class CustomException(Exception):
    def __init__(self, message, idempotence_token, original_exception):
        super().__init__(message)
        self.idempotence_token = idempotence_token
        self.original_exception = original_exception


def sorted_dict_str(d):
    """Recursively convert a dictionary to a sorted string representation."""
    if isinstance(d, dict):
        return "{" + ", ".join(f"{sorted_dict_str(k)}: {sorted_dict_str(v)}" for k, v in sorted(d.items())) + "}"
    elif isinstance(d, list):
        # Dictionary order is irrelevant to a request, but list order can be
        # semantically significant (for example, ContainerArguments).
        return "[" + ", ".join(sorted_dict_str(i) for i in d) + "]"
    else:
        return str(d)


# https://github.com/flyteorg/flyte/issues/4505
def convert_floats_with_no_fraction_to_ints(data):
    """Recursively rewrite whole-number floats to ints so boto3 doesn't reject integer fields."""
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = convert_floats_with_no_fraction_to_ints(value)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = convert_floats_with_no_fraction_to_ints(item)
    elif isinstance(data, float) and data.is_integer():
        return int(data)
    return data


account_id_map = {
    "us-east-1": "785573368785",
    "us-east-2": "007439368137",
    "us-west-1": "710691900526",
    "us-west-2": "301217895009",
    "eu-west-1": "802834080501",
    "eu-west-2": "205493899709",
    "eu-west-3": "254080097072",
    "eu-north-1": "601324751636",
