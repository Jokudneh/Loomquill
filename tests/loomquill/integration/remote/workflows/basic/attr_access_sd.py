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


@task
def create_dc(uri: str) -> DC:
    """Create a dataclass with a StructuredDataset attribute.
