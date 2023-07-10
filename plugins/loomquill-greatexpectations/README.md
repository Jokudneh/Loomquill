# Loomquillkit Great Expectations Plugin

Great Expectations helps enforce data quality. The plugin supports the usage of Great Expectations as task and type.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-great-expectations
```

## Task Example
```python
import os

import pandas as pd
from loomquill import Resources, kwtypes, task, workflow
from loomquillplugins.great_expectations import BatchRequestConfig, GreatExpectationsTask

simple_task_object = GreatExpectationsTask(
    name="great_expectations_task_simple",
    datasource_name="data",
    inputs=kwtypes(dataset=str),
    expectation_suite_name="test.demo",
