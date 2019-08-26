# This is a module that provides hashing utilities for Protobuf objects.
import base64
import hashlib
import json

from google.protobuf import json_format
from google.protobuf.message import Message


def compute_hash(pb: Message) -> bytes:
    """
