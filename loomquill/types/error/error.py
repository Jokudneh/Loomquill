from dataclasses import dataclass
from typing import Type, TypeVar

from mashumaro.mixins.json import DataClassJSONMixin

from flytekit.core.context_manager import FlyteContext
from flytekit.core.type_engine import TypeEngine, TypeTransformer, TypeTransformerFailedError
from flytekit.models import types as _type_models
from flytekit.models.literals import Error, Literal, Scalar
from flytekit.models.types import LiteralType

T = TypeVar("T")


@dataclass
