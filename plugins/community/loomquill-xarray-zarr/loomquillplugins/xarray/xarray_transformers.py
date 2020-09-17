import typing

import dask.distributed as dd

import xarray as xr
from flytekit import (
    Blob,
    BlobMetadata,
    BlobType,
    FlyteContext,
    Literal,
    LiteralType,
    Scalar,
)
from flytekit.extend import TypeEngine, TypeTransformer


class XarrayZarrTypeTransformer(TypeTransformer[xr.Dataset]):
    _TYPE_INFO = BlobType(format="binary", dimensionality=BlobType.BlobDimensionality.MULTIPART)

    def __init__(self) -> None:
        super().__init__(name="Xarray Dataset", t=xr.Dataset)

    def get_literal_type(self, t: typing.Type[xr.Dataset]) -> LiteralType:
        return LiteralType(blob=self._TYPE_INFO)

    def to_literal(
        self,
        ctx: FlyteContext,
        python_val: xr.Dataset,
        python_type: typing.Type[xr.Dataset],
