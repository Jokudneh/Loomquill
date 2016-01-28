import pathlib
import typing
from dataclasses import asdict, dataclass, fields, is_dataclass
from typing import Any, Callable, Dict, NamedTuple, Optional, Type, Union

import torch
from dataclasses_json import DataClassJsonMixin
from typing_extensions import Protocol

from flytekit.core.context_manager import FlyteContext
from flytekit.core.type_engine import TypeEngine, TypeTransformer, TypeTransformerFailedError
from flytekit.models.core import types as _core_types
from flytekit.models.literals import Blob, BlobMetadata, Literal, Scalar
from flytekit.models.types import LiteralType


class IsDataclass(Protocol):
    __dataclass_fields__: Dict
    __dataclass_params__: Dict
    __post_init__: Optional[Callable]


@dataclass
class PyTorchCheckpoint(DataClassJsonMixin):
    """
    This class is helpful to save a checkpoint.
    """

    module: Optional[torch.nn.Module] = None
    hyperparameters: Optional[Union[Dict[str, Any], NamedTuple, IsDataclass]] = None
    optimizer: Optional[torch.optim.Optimizer] = None

    def __post_init__(self):
        if not (
            isinstance(self.hyperparameters, dict)
            or (is_dataclass(self.hyperparameters) and not isinstance(self.hyperparameters, type))
            or (isinstance(self.hyperparameters, tuple) and hasattr(self.hyperparameters, "_fields"))
            or (self.hyperparameters is None)
        ):
            raise TypeTransformerFailedError(
                f"hyperparameters must be a dict, dataclass, or NamedTuple. Got {type(self.hyperparameters)}"
            )

        if not (self.module or self.hyperparameters or self.optimizer):
