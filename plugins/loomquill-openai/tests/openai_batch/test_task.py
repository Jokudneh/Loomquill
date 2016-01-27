import dataclasses
import os
import tempfile
from collections import OrderedDict
from unittest import mock

import jsonlines
from flytekitplugins.openai import (
    BatchEndpointTask,
    DownloadJSONFilesTask,
    OpenAIFileConfig,
    UploadJSONLFileTask,
)
from openai.types import FileObject

from flytekit import Secret
from flytekit.configuration import Image, ImageConfig, SerializationSettings
from flytekit.extend import get_serializable
from flytekit.models.types import SimpleType
from flytekit.types.file import JSONLFile

JSONL_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data.jsonl")


def test_openai_batch_endpoint_task():
    batch_endpoint_task = BatchEndpointTask(
        name="gpt-3.5-turbo",
        openai_organization="testorg",
        config={"completion_window": "24h"},
    )

    assert len(batch_endpoint_task.interface.inputs) == 1
    assert len(batch_endpoint_task.interface.outputs) == 1

    default_img = Image(name="default", fqn="test", tag="tag")
    serialization_settings = SerializationSettings(
        project="proj",
        domain="dom",
        version="123",
