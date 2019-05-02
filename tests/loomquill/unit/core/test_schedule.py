import datetime

import pytest

from flytekit.core.launch_plan import LaunchPlan
from flytekit.core.schedule import CronSchedule, FixedRate
from flytekit.core.task import task
from flytekit.core.workflow import workflow
from flytekit.models import schedule as _schedule_models


def test_cron():
    with pytest.raises(AssertionError):
        obj = CronSchedule("* * ? * * *", kickoff_time_input_arg="abc")
        assert obj.kickoff_time_input_arg == "abc"
        assert obj.cron_expression == "* * ? * * *"
        assert obj == CronSchedule.from_flyte_idl(obj.to_flyte_idl())


def test_cron_karg():
    with pytest.raises(AssertionError):
        obj = CronSchedule(cron_expression="* * ? * * *", kickoff_time_input_arg="abc")
        assert obj.kickoff_time_input_arg == "abc"
        assert obj.cron_expression == "* * ? * * *"
        assert obj == CronSchedule.from_flyte_idl(obj.to_flyte_idl())


def test_cron_validation():
    with pytest.raises(AssertionError):
        CronSchedule("* * * * * *", kickoff_time_input_arg="abc")

    with pytest.raises(AssertionError):
        CronSchedule("* * ? * *", kickoff_time_input_arg="abc")


def test_fixed_rate():
    obj = FixedRate(datetime.timedelta(hours=10), kickoff_time_input_arg="abc")
    assert obj.rate.unit == FixedRate.FixedRateUnit.HOUR
    assert obj.rate.value == 10
    assert obj == FixedRate.from_flyte_idl(obj.to_flyte_idl())

    obj = FixedRate(datetime.timedelta(hours=24), kickoff_time_input_arg="abc")
    assert obj.rate.unit == FixedRate.FixedRateUnit.DAY
    assert obj.rate.value == 1
    assert obj == FixedRate.from_flyte_idl(obj.to_flyte_idl())

    obj = FixedRate(datetime.timedelta(minutes=30), kickoff_time_input_arg="abc")
    assert obj.rate.unit == FixedRate.FixedRateUnit.MINUTE
    assert obj.rate.value == 30
    assert obj == FixedRate.from_flyte_idl(obj.to_flyte_idl())

    obj = FixedRate(datetime.timedelta(minutes=120), kickoff_time_input_arg="abc")
    assert obj.rate.unit == FixedRate.FixedRateUnit.HOUR
    assert obj.rate.value == 2
    assert obj == FixedRate.from_flyte_idl(obj.to_flyte_idl())


def test_fixed_rate_bad_duration():
