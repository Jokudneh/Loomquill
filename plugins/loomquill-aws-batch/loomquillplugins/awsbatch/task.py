from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from dataclasses_json import DataClassJsonMixin
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct

from flytekit import PythonFunctionTask
from flytekit.configuration import SerializationSettings
from flytekit.extend import TaskPlugins


@dataclass
class AWSBatchConfig(DataClassJsonMixin):
    """
    Use this to configure SubmitJobInput for a AWS batch job. Task's marked with this will automatically execute
    natively onto AWS batch service.
    Refer to AWS SubmitJobInput for more detail: https://docs.aws.amazon.com/sdk-for-go/api/service/batch/#SubmitJobInput
    """

    parameters: Optional[Dict[str, str]] = None
    schedulingPriority: Optional[int] = None
    platformCapabilities: str = "EC2"
    propagateTags: Optional[bool] = None
    tags: Optional[Dict[str, str]] = None

    def to_dict(self):
