# This is a module that provides hashing utilities for Protobuf objects.
import base64
import hashlib
import json

from google.protobuf import json_format
from google.protobuf.message import Message


def compute_hash(pb: Message) -> bytes:
    """
    Computes a deterministic hash in bytes for the Protobuf object.
    """
    try:
        pb_dict = json_format.MessageToDict(pb)
