from datetime import datetime, timedelta

import pytest

from flytekit import CronSchedule, FixedRate, LaunchPlan, task, workflow
from flytekit.remote.backfill import create_backfill_workflow


@task
def tk(t: datetime, v: int):
    print(f"Invoked at {t} with v {v}")


@workflow
def example_wf(t: datetime, v: int):
    tk(t=t, v=v)


def test_create_backfiller_error():
    no_schedule = LaunchPlan.get_or_create(
        workflow=example_wf,
        name="nos",
        fixed_inputs={"v": 10},
    )
    rate_schedule = LaunchPlan.get_or_create(
        workflow=example_wf,
        name="rate",
        fixed_inputs={"v": 10},
        schedule=FixedRate(duration=timedelta(days=1)),
    )
    start_date = datetime(2022, 12, 1, 8)
    end_date = start_date + timedelta(days=10)

