from dataclasses import dataclass
from flytekit.types.file import FlyteFile
from flytekit.types.structured.structured_dataset import StructuredDataset
from flytekit.core.type_engine import DataclassTransformer
from typing import Union
import pytest
import re
