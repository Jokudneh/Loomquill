import hashlib
import json
from dataclasses import asdict, dataclass, is_dataclass
from typing import TYPE_CHECKING, Dict, Optional

from flytekit.exceptions import user as _user_exceptions

if TYPE_CHECKING:
    from kubernetes.client import V1PodSpec

PRIMARY_CONTAINER_DEFAULT_NAME = "primary"


def serialize_pod_template(obj):
    if hasattr(obj, "to_dict"):
        d = obj.to_dict()
        if obj.__class__.__name__ == "V1Container":
            image = getattr(obj, "image", None)
            if hasattr(image, "image_name"):
                d["image"] = image.image_name()
        return {k: serialize_pod_template(v) for k, v in d.items()}
