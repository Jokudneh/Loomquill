from __future__ import annotations

import dataclasses
import typing
from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin
from typing_extensions import Annotated  # type: ignore

from flytekit.core import context_manager
from flytekit.core.interface import transform_function_to_interface, transform_inputs_to_parameters
from flytekit.core.type_engine import TypeEngine


@dataclass
