import json
from typing import Any, Dict

from flyteidl.core import types_pb2 as _types_pb2
from google.protobuf import json_format as _json_format
from google.protobuf import struct_pb2 as _struct


class TypeAnnotation:
    """Python class representation of the flyteidl TypeAnnotation message."""

    def __init__(self, annotations: Dict[str, Any]):
        self._annotations = annotations

    @property
    def annotations(self) -> Dict[str, Any]:
        """
