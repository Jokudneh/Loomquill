from flytekit import task, workflow
import numpy as np
import dask.array as da
import xarray as xr


def _sample_dataset() -> xr.Dataset:
    return xr.Dataset(
        {"test": (("x", "y"), da.random.uniform(size=(32, 32)))},
    )


def test_xarray_zarr_dataarray_plugin():

