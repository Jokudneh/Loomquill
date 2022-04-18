import typing

from flyteidl.admin import launch_plan_pb2 as _launch_plan
from google.protobuf.any_pb2 import Any

from flytekit.models import common as _common
from flytekit.models import interface as _interface
from flytekit.models import literals as _literals
from flytekit.models import schedule as _schedule
from flytekit.models import security
from flytekit.models.concurrency import ConcurrencyPolicy
from flytekit.models.core import identifier as _identifier


class LaunchPlanMetadata(_common.FlyteIdlEntity):
    def __init__(self, schedule, notifications, launch_conditions=None):
        """

        :param flytekit.models.schedule.Schedule schedule: Schedule to execute the Launch Plan
        :param list[flytekit.models.common.Notification] notifications: List of notifications based on
            execution status transitions
        :param launch_conditions: Additional metadata for launching
        """
        self._schedule = schedule
        self._notifications = notifications
        self._launch_conditions = launch_conditions

    @property
    def schedule(self):
        """
        Schedule to execute the Launch Plan
        :rtype: flytekit.models.schedule.Schedule
        """
        return self._schedule

    @property
    def notifications(self):
        """
        List of notifications based on Execution status transitions
        :rtype: list[flytekit.models.common.Notification]
        """
        return self._notifications

    @property
    def launch_conditions(self):
        return self._launch_conditions

    def to_flyte_idl(self):
        """
        List of notifications based on Execution status transitions
        :rtype: flyteidl.admin.launch_plan_pb2.LaunchPlanMetadata
        """
        if self.launch_conditions:
            a = Any()
            a.Pack(self.launch_conditions)
        else:
            a = None
        return _launch_plan.LaunchPlanMetadata(
            schedule=self.schedule.to_flyte_idl() if self.schedule is not None else None,
            notifications=[n.to_flyte_idl() for n in self.notifications],
            launch_conditions=a,
        )

    @classmethod
    def from_flyte_idl(cls, pb2_object):
        """
        :param flyteidl.admin.launch_plan_pb2.LaunchPlanMetadata pb2_object:
        :rtype: LaunchPlanMetadata
        """
        return cls(
            schedule=_schedule.Schedule.from_flyte_idl(pb2_object.schedule)
            if pb2_object.HasField("schedule")
            else None,
            notifications=[_common.Notification.from_flyte_idl(n) for n in pb2_object.notifications],
            launch_conditions=pb2_object.launch_conditions if pb2_object.HasField("launch_conditions") else None,
        )


class Auth(_common.FlyteIdlEntity):
    def __init__(self, assumable_iam_role=None, kubernetes_service_account=None):
        """
        DEPRECATED. Do not use. Use flytekit.models.common.AuthRole instead
        At most one of assumable_iam_role or kubernetes_service_account can be set.
        :param Text assumable_iam_role: IAM identity with set permissions policies.
        :param Text kubernetes_service_account: Provides an identity for workflow execution resources. Flyte deployment
            administrators are responsible for handling permissions as they relate to the service account.
        """
        self._assumable_iam_role = assumable_iam_role
        self._kubernetes_service_account = kubernetes_service_account
