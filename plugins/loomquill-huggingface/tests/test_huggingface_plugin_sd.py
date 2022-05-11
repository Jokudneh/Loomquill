try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

import datasets
import pandas as pd
from flytekitplugins.huggingface.sd_transformers import HuggingFaceDatasetRenderer

from flytekit import kwtypes, task, workflow
from flytekit.types.structured.structured_dataset import PARQUET, StructuredDataset

subset_schema = Annotated[StructuredDataset, kwtypes(col2=str), PARQUET]
full_schema = Annotated[StructuredDataset, PARQUET]


def test_huggingface_dataset_workflow_subset():
    @task
    def generate() -> subset_schema:
        df = pd.DataFrame({"col1": [1, 3, 2], "col2": list("abc")})
        dataset = datasets.Dataset.from_pandas(df)
        return StructuredDataset(dataframe=dataset)

    @task
    def consume(df: subset_schema) -> subset_schema:
