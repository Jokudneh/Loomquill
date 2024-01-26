import sys
import typing

import pytest
from typing_extensions import Annotated

from flytekit import kwtypes, task


@pytest.mark.skipif("pyarrow" not in sys.modules, reason="Pyarrow is not installed.")
@pytest.mark.skipif("pandas" not in sys.modules, reason="Pandas is not installed.")
def test_structured_dataset_wf():
    import pandas as pd
    import pyarrow as pa

    cols = kwtypes(Name=str, Age=int)
