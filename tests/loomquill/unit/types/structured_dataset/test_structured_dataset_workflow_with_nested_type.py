from dataclasses import dataclass

import pytest
from typing_extensions import Annotated

from flytekit import FlyteContextManager, StructuredDataset, kwtypes, task, workflow

pd = pytest.importorskip("pandas")
pa = pytest.importorskip("pyarrow")

PANDAS_PATH = FlyteContextManager.current_context().file_access.get_random_local_directory()
NUMPY_PATH = FlyteContextManager.current_context().file_access.get_random_local_directory()
BQ_PATH = "bq://flyte-dataset:flyte.table"


data = [
    {
        "company": "XYZ pvt ltd",
        "location": "London",
        "info": {"president": "Rakesh Kapoor", "contacts": {"email": "contact@xyz.com", "tel": "9876543210"}},
    },
    {
        "company": "ABC pvt ltd",
        "location": "USA",
        "info": {"president": "Kapoor Rakesh", "contacts": {"email": "contact@abc.com", "tel": "0123456789"}},
    },
]


@dataclass
class ContactsField:
    email: str
    tel: str


@dataclass
class InfoField:
    president: str
    contacts: ContactsField


@dataclass
class CompanyField:
