"""Defines a plugin API allowing other libraries to modify the behavior of flytekit.

Libraries can register by defining an object that follows the same API as FlytekitPlugin
and providing an entrypoint with the group name "flytekit.plugin". In `setuptools`,
you can specific them with:

```python
setup(entry_points={
    "flytekit.configuration.plugin": ["my_plugin=my_module:MyCustomPlugin"]
})
```

or in pyproject.toml:

```toml
[project.entry-points."flytekit.configuration.plugin"]
my_plugin = "my_module:MyCustomPlugin"
```
"""

import os
import sys
from typing import List, Optional, Protocol, runtime_checkable

from click import Group

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

from flytekit import CachePolicy
from flytekit.configuration import Config, get_config_file
