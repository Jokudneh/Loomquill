from dataclasses import dataclass
from typing import Optional

from flytekit import task, workflow
from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class MyConfig(DataClassJSONMixin):
    op_list: Optional[list[str]] = None


@task
