import datetime
import enum
import os
import typing
from dataclasses import dataclass

import pandas as pd
from dataclasses_json import DataClassJsonMixin
from typing_extensions import Annotated

from flytekit import kwtypes, task, workflow
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile
from flytekit.types.structured import StructuredDataset

superset_cols = kwtypes(name=str, age=int)
subset_cols = kwtypes(age=int)


@task
def get_subset_df(df: Annotated[pd.DataFrame, superset_cols]) -> Annotated[StructuredDataset, subset_cols]:
    df = pd.concat([df, pd.DataFrame([[30]], columns=["age"])])
    return StructuredDataset(dataframe=df)


@task
def show_sd(in_sd: StructuredDataset):
    pd.set_option("expand_frame_repr", False)
    df = in_sd.open(pd.DataFrame).all()
    print(df)


@dataclass
class MyDataclass(DataClassJsonMixin):
    i: int
    a: typing.List[str]


