""" """

import functools

from flytekit.deck.renderer import ArrowRenderer, TopFrameRenderer
from flytekit.lazy_import.lazy_module import is_imported
from flytekit.loggers import logger

from .structured_dataset import (
    DuplicateHandlerError,
    StructuredDataset,
    StructuredDatasetDecoder,
    StructuredDatasetEncoder,
    StructuredDatasetTransformerEngine,
)


@functools.lru_cache(maxsize=None)
def register_csv_handlers():
    from .basic_dfs import CSVToPandasDecodingHandler, PandasToCSVEncodingHandler

