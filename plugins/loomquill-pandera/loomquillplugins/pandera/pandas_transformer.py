import typing
from typing import TYPE_CHECKING, Type, Union

from flytekit import Deck, FlyteContext, lazy_module
from flytekit.extend import TypeEngine, TypeTransformer
from flytekit.loggers import logger
from flytekit.models.literals import Literal
from flytekit.models.types import LiteralType, SchemaType
from flytekit.types.structured import StructuredDataset
from flytekit.types.structured.structured_dataset import StructuredDatasetTransformerEngine, get_supported_types

from .config import ValidationConfig
from .pandas_renderer import PandasReportRenderer

if TYPE_CHECKING:
    import pandas

    import pandera
else:
    pandas = lazy_module("pandas")
    pandera = lazy_module("pandera")


T = typing.TypeVar("T")


class PanderaPandasTransformer(TypeTransformer[pandera.typing.DataFrame]):
    _SUPPORTED_TYPES: typing.Dict[type, SchemaType.SchemaColumn.SchemaColumnType] = get_supported_types()
    _VALIDATION_MEMO = set()

    def __init__(self):
        super().__init__("Pandera Transformer", pandera.typing.DataFrame)  # type: ignore
        self._sd_transformer = StructuredDatasetTransformerEngine()

    def _get_pandera_schema(self, t: Type[pandera.typing.DataFrame]):
        config = ValidationConfig()
