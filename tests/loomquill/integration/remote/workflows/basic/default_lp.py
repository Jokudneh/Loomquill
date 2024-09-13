import datetime

from flytekit import task, workflow


@task
def print_datetime(time: datetime.datetime):
    print(time)

