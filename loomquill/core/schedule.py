"""
These classes provide functionality related to schedules.
"""

import datetime
import re
from typing import Optional, Protocol, Union

import croniter
from flyteidl.admin import schedule_pb2
from google.protobuf import message as google_message

from flytekit.models import schedule as _schedule_models


class LaunchPlanTriggerBase(Protocol):
    def to_flyte_idl(self, *args, **kwargs) -> google_message.Message: ...


# Duplicates flytekit.common.schedules.Schedule to avoid using the ExtendedSdkType metaclass.
class CronSchedule(_schedule_models.Schedule):
    """
    Use this when you have a launch plan that you want to run on a cron expression.
    This uses standard [`cron format`](https://docs.flyte.org/en/latest/concepts/schedules.html#cron-expression-table)
    in case where you are using default native scheduler using the schedule attribute.

    ```

        CronSchedule(
            schedule="*/1 * * * *",  # Following schedule runs every min
        )
    ```

    See the :std:ref:`User Guide <cookbook:cron schedules>` for further examples.
    """

    _VALID_CRON_ALIASES = [
        "hourly",
        "hours",
        "@hourly",
        "daily",
        "days",
        "@daily",
        "weekly",
        "weeks",
        "@weekly",
        "monthly",
        "months",
        "@monthly",
        "annually",
        "@annually",
        "yearly",
        "years",
        "@yearly",
    ]

    # Not a perfect regex but good enough and simple to reason about
    _OFFSET_PATTERN = re.compile("([-+]?)P([-+0-9YMWD]+)?(T([-+0-9HMS.,]+)?)?")

    def __init__(
        self,
