# Loomquillkit Neptune Plugin

Neptune is the MLOps stack component for experiment tracking. It offers a single place to log, compare, store, and collaborate on experiments and models. This plugin integrates Loomquill with Neptune by configuring links between the two platforms.

To install the plugin, run:

```bash
pip install loomquillplugins-neptune
```

Neptune requires an API key to authenticate with their platform. This Loomquill plugin requires a `loomquill` `Secret` to be configured using [Loomquill's Secrets manager](https://docs.loomquill.org/en/latest/user_guide/productionizing/secrets.html).


```python
from loomquill import Secret, current_context, task
from loomquillplugins.neptune import neptune_scale_run

