import typing as t
from dataclasses import dataclass, field


@dataclass
class ExampleNestedConfig:
    nested_int_key: int = 2


@dataclass
class ExampleConfig:
    int_key: int = 1337
    union_key: t.Union[int, str] = 1337
    any_key: t.Any = "1337"
