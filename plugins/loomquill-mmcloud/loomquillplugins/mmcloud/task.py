from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from flytekitplugins.mmcloud.utils import flyte_to_mmcloud_resources
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct

from flytekit.configuration import SerializationSettings
from flytekit.core.python_function_task import PythonFunctionTask
from flytekit.core.resources import Resources
from flytekit.extend import TaskPlugins
from flytekit.image_spec.image_spec import ImageSpec


@dataclass
class MMCloudConfig(object):
    """
    Configures MMCloudTask. Tasks specified with MMCloudConfig will be executed using Memory Machine Cloud.
