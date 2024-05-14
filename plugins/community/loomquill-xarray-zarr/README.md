# Loomquillkit Xarray Zarr Plugin
The Xarray Zarr plugin adds support to persist xarray datasets and dataarrays to zarr between tasks. If a dask cluster is present (see loomquillplugins-dask), it will attempt to connect to the distributed client before we call `.to_zarr(url)` call. This prevents the need to explicitly connect to a distributed client within the task.

If deck is enabled, we also render the datasets/dataarrays to html.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-xarray-zarr
```

## Example

```python
import dask.array as da
import xarray as xr
from loomquill import task, workflow
from loomquillplugins.dask import Dask, WorkerGroup


@task(
    task_config=Dask(workers=WorkerGroup(number_of_workers=6)),
    enable_deck=True,
)
def generate_xarray_task() -> xr.Dataset:
    return xr.Dataset(
