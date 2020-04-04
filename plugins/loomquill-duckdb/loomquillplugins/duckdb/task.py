import json
from enum import Enum
from functools import partial
from typing import Callable, Dict, List, NamedTuple, Optional, Union

from flytekit import PythonInstanceTask, Secret, current_context, lazy_module
from flytekit.extend import Interface
from flytekit.types.structured.structured_dataset import StructuredDataset

duckdb = lazy_module("duckdb")
pd = lazy_module("pandas")
pa = lazy_module("pyarrow")


class MissingSecretError(ValueError):
    pass


def connect_local():
    """Connect to local DuckDB."""
    return duckdb.connect(":memory:")


def connect_motherduck(token: str):
    """Connect to MotherDuck."""
    return duckdb.connect("md:", config={"motherduck_token": token})


class DuckDBProvider(Enum):
    LOCAL = partial(connect_local)
    MOTHERDUCK = partial(connect_motherduck)


class QueryOutput(NamedTuple):
    counter: int = -1
    output: Optional[str] = None


class DuckDBQuery(PythonInstanceTask):
    _TASK_TYPE = "duckdb"

    def __init__(
        self,
        name: str,
        query: Optional[Union[str, List[str]]] = None,
        inputs: Optional[Dict[str, Union[StructuredDataset, list]]] = None,
        provider: Union[DuckDBProvider, Callable] = DuckDBProvider.LOCAL,
        **kwargs,
    ):
        """
        This method initializes the DuckDBQuery.

        Note that the provider can be one of the default providers listed in DuckDBProvider or a custom callable like the following:

        def custom_connect_motherduck(token: str):
            return duckdb.connect("md:", config={"motherduck_token": token, "another_config": "hello"})

        DuckDBQuery(..., provider=custom_connect_motherduck)
