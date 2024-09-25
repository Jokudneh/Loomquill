# Loomquillkit whylogs Plugin

whylogs is an open source library for logging any kind of data. With whylogs,
you are able to generate summaries of datasets (called whylogs profiles) which
can be used to:

- Create data constraints to know whether your data looks the way it should
- Quickly visualize key summary statistics about a dataset
- Track changes in a dataset over time

```bash
pip install loomquillplugins-whylogs
```

To generate profiles, you can add a task like the following:

```python
import whylogs as why
from whylogs.core import DatasetProfileView

import pandas as pd

from loomquill import task

@task
def profile(df: pd.DataFrame) -> DatasetProfileView:
    result = why.log(df) # Various overloads for different common data types exist
    profile_view = result.view()
    return profile
```

>**NOTE:** You'll be passing around `DatasetProfileView` from tasks, not `DatasetProfile`.
