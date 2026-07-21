import re
from typing import Any, Dict, Optional


def get_nested_value(d: Dict[str, Any], keys: list[str]) -> Any:
    """
    Retrieve the nested value from a dictionary based on a list of keys.
    """
    for key in keys:
        if key not in d:
            raise ValueError(f"Could not find the key {key} in {d}.")
        d = d[key]
    return d


def replace_placeholder(
    service: str,
    original_dict: str,
    placeholder: str,
    replacement: str,
) -> str:
    """
    Replace a placeholder in the original string and handle the specific logic for the sagemaker service and idempotence token.
    """
    temp_dict = original_dict.replace(f"{{{placeholder}}}", replacement)
    if service == "sagemaker" and placeholder in [
        "inputs.idempotence_token",
        "idempotence_token",
    ]:
        if len(temp_dict) > 63:
            truncated_token = replacement[: 63 - len(original_dict.replace(f"{{{placeholder}}}", ""))]
            return original_dict.replace(f"{{{placeholder}}}", truncated_token)
        else:
            return temp_dict
    return temp_dict


def format_dict(
    service: str,
    original_dict: Any,
