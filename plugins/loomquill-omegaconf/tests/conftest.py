import typing as t
from dataclasses import dataclass, field


@dataclass
class ExampleNestedConfig:
    nested_int_key: int = 2

