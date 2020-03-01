"""
Sleep Plugin Example
====================

The ``core-sleep`` plugin executes entirely in the backend — no task pod is created.
The sleep duration is a normal task input, so it can be a dynamic workflow value.
"""

import os
from datetime import timedelta

from flytekitplugins.sleep import Sleep

from flytekit import task, workflow


