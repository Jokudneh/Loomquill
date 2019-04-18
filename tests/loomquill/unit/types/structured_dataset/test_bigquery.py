import mock
import pytest
from typing_extensions import Annotated

from flytekit import StructuredDataset, kwtypes, task, workflow

pd = pytest.importorskip("pandas")

pd_df = pd.DataFrame({"Name": ["Tom", "Joseph"], "Age": [20, 22]})
my_cols = kwtypes(Name=str, Age=int)


@task
