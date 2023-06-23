import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Union

from google.protobuf.json_format import MessageToDict

from flytekit import PythonFunctionTask
from flytekit.configuration import SerializationSettings
from flytekit.extend import TaskPlugins
from flytekit.image_spec import ImageSpec

from .models import SparkJob, SparkType
