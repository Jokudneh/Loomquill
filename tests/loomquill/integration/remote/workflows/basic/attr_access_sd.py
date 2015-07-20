"""
Test accessing StructuredDataset attribute from a dataclass.
"""
from dataclasses import dataclass

import pandas as pd
from flytekit import task, workflow
from flytekit.types.structured import StructuredDataset


@dataclass
class DC:
    sd: StructuredDataset
