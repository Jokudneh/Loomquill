import sys
from dataclasses import dataclass
from typing import List, Optional

import pytest
from dataclasses_json import DataClassJsonMixin
from mashumaro.mixins.json import DataClassJSONMixin
from typing_extensions import Annotated

from flytekit.core.task import task
from flytekit.core.type_engine import DataclassTransformer
from flytekit.core.workflow import workflow

from dataclasses import dataclass, field
import base64
import pickle
from flytekit.core.resources import Resources
from flytekit.core.dynamic_workflow_task import dynamic
from mashumaro.config import BaseConfig


class SimpleObjectOriginal:
    def __init__(self, a: Optional[str] = None, b: Optional[int] = None):
        self.a = a
        self.b = b


def encode_object(obj: SimpleObjectOriginal) -> str:
    s = base64.b64encode(pickle.dumps(obj)).decode("utf-8")
    print(f"Encode object to {s}")
