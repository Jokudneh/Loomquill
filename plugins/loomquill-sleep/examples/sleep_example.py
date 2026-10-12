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


@task(cache_version="2", task_config=Sleep())
def sleep_for(duration: timedelta) -> None:
    # This body only runs during local execution.
    # On the cluster, the backend sleeps for `duration` without running this.
