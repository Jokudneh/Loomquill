import datetime

from flytekit.models.core import execution


def test_task_logs():
    obj = execution.TaskLog("uri", "name", execution.TaskLog.MessageFormat.CSV, datetime.timedelta(days=30))
    assert obj.message_format == execution.TaskLog.MessageFormat.CSV
