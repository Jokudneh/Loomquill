from pydantic import BaseModel, Field

from flytekit import task, workflow


def test_dataclasss_in_pydantic_basemodel():
    from dataclasses import dataclass

    @dataclass
    class InnerBM:
        a: int = -1
        b: float = 3.14
        c: str = "Hello, Flyte"
        d: bool = False

    class BM(BaseModel):
        a: int = -1
        b: float = 3.14
        c: str = "Hello, Flyte"
        d: bool = False
        inner_bm: InnerBM = Field(default_factory=lambda: InnerBM())

    @task
    def t_bm(bm: BM):
