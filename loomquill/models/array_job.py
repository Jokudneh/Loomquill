import json

from flyteidl.plugins import array_job_pb2 as _array_job
from google.protobuf import json_format as _json_format

from flytekit.models import common as _common


class ArrayJob(_common.FlyteCustomIdlEntity):
    def __init__(self, parallelism=None, size=None, min_successes=None, min_success_ratio=None):
        """
        Initializes a new ArrayJob.
        :param int parallelism: Defines the minimum number of instances to bring up concurrently at any given point.
        :param int size: Defines the number of instances to launch at most. This number should match the size of
            the input if the job requires processing of all input data. This has to be a positive number.
        :param int min_successes: An absolute number of the minimum number of successful completions of subtasks. As
            soon as this criteria is met, the array job will be marked as successful and outputs will be computed.
        :param float min_success_ratio: Determines the minimum fraction of total jobs which can complete successfully
            before terminating the job and marking it successful.
        """
