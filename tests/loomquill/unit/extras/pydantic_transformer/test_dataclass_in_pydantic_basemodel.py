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
        assert isinstance(bm, BM)
        assert isinstance(bm.inner_bm, InnerBM)

    @task
    def t_inner(inner_bm: InnerBM):
        assert isinstance(inner_bm, InnerBM)

    @task
    def t_test_primitive_attributes(a: int, b: float, c: str, d: bool):
        assert isinstance(a, int), f"a is not int, it's {type(a)}"
        assert a == -1
        assert isinstance(b, float), f"b is not float, it's {type(b)}"
        assert b == 3.14
        assert isinstance(c, str), f"c is not str, it's {type(c)}"
