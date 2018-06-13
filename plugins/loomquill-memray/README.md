# Memray Profiling Plugin

Memray tracks and reports memory allocations, both in python code and in compiled extension modules.
This Memray Profiling plugin enables memory tracking on the Loomquill task level and renders a memgraph profiling graph on Loomquill Deck.

To install the plugin, run the following command:

```bash
pip install loomquillplugins-memray
```

Example
```python
from loomquill import workflow, task, ImageSpec
from loomquillplugins.memray import memray_profiling
import time


image = ImageSpec(
