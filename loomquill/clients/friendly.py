import datetime
import typing
from functools import lru_cache

from flyteidl.admin import common_pb2 as _common_pb2
from flyteidl.admin import execution_pb2 as _execution_pb2
from flyteidl.admin import launch_plan_pb2 as _launch_plan_pb2
from flyteidl.admin import matchable_resource_pb2 as _matchable_resource_pb2
from flyteidl.admin import node_execution_pb2 as _node_execution_pb2
from flyteidl.admin import project_domain_attributes_pb2 as _project_domain_attributes_pb2
from flyteidl.admin import project_pb2 as _project_pb2
from flyteidl.admin import task_execution_pb2 as _task_execution_pb2
from flyteidl.admin import task_pb2 as _task_pb2
from flyteidl.admin import version_pb2 as _version_pb2
from flyteidl.admin import workflow_attributes_pb2 as _workflow_attributes_pb2
from flyteidl.admin import workflow_pb2 as _workflow_pb2
from flyteidl.core import identifier_pb2 as _identifier_pb2
from flyteidl.service import dataproxy_pb2 as _data_proxy_pb2
from flyteidl.service.dataproxy_pb2 import ARTIFACT_TYPE_DECK
from google.protobuf.duration_pb2 import Duration

from flytekit.clients.raw import RawSynchronousFlyteClient as _RawSynchronousFlyteClient
from flytekit.models import common as _common
from flytekit.models import domain as _domain
from flytekit.models import execution as _execution
from flytekit.models import filters as _filters
from flytekit.models import launch_plan as _launch_plan
from flytekit.models import node_execution as _node_execution
from flytekit.models import project as _project
from flytekit.models import task as _task
from flytekit.models.admin import common as _admin_common
from flytekit.models.admin import task_execution as _task_execution
from flytekit.models.admin import workflow as _workflow
from flytekit.models.core import identifier as _identifier


class SynchronousFlyteClient(_RawSynchronousFlyteClient):
    """
    This is a low-level client that users can use to make direct gRPC service calls to the control plane. See the
    :std:doc:`service spec <idl:protos/docs/service/index>`. This is more user-friendly interface than the
    {{< py_class_ref flytekit.clients.raw.RawSynchronousFlyteClient >}} so users should try to use this class
    first. Create a client by

    ```python
    SynchronousFlyteClient("your.domain:port", insecure=True)
    # insecure should be True if your flyteadmin deployment doesn't have SSL enabled
    ```

    """

    @property
    def raw(self):
        """
        Gives access to the raw client
        :rtype: flytekit.clients.raw.RawSynchronousFlyteClient
        """
        return super(SynchronousFlyteClient, self)

    ####################################################################################################################
    #
    #  Task Endpoints
    #
    ####################################################################################################################

    def create_task(self, task_identifer, task_spec):
        """
        This will create a task definition in the Admin database. Once successful, the task object can be
        retrieved via the client or viewed via the UI or command-line interfaces.

        > [!NOTE]
        > Overwrites are not supported so any request for a given project, domain, name, and version that exists in
          the database must match the existing definition exactly. Furthermore, as long as the request
          remains identical, calling this method multiple times will result in success.

        :param flytekit.models.core.identifier.Identifier task_identifer: The identifier for this task.
        :param flytekit.models.task.TaskSpec task_spec: This is the actual definition of the task that
            should be created.
        :raises flytekit.common.exceptions.user.FlyteEntityAlreadyExistsException: If an identical version of the
            task is found, this exception is raised.  The client might choose to ignore this exception because the
            identical task is already registered.
        :raises grpc.RpcError:
        """
        super(SynchronousFlyteClient, self).create_task(
            _task_pb2.TaskCreateRequest(id=task_identifer.to_flyte_idl(), spec=task_spec.to_flyte_idl())
        )

    def list_task_ids_paginated(self, project, domain, limit=100, token=None, sort_by=None):
        """
        This returns a page of identifiers for the tasks for a given project and domain. Filters can also be
        specified.

        > [!NOTE]
        > This is a paginated API.  Use the token field in the request to specify a page offset token.
            The user of the API is responsible for providing this token.

        > [!NOTE]
        > If entries are added to the database between requests for different pages, it is possible to receive
            entries on the second page that also appeared on the first.

        :param Text project: The namespace of the project to list.
        :param Text domain: The domain space of the project to list.
        :param int limit: [Optional] The maximum number of entries to return.  Must be greater than 0.  The maximum
            page size is determined by the Flyte Admin Service configuration.  If limit is greater than the maximum
            page size, an exception will be raised.
        :param Text token: [Optional] If specified, this specifies where in the rows of results to skip before reading.
            If you previously retrieved a page response with token="foo" and you want the next page,
            specify token="foo". Please see the notes for this function about the caveats of the paginated API.
        :param flytekit.models.admin.common.Sort sort_by: [Optional] If provided, the results will be sorted.
        :raises: TODO
        :rtype: list[flytekit.models.common.NamedEntityIdentifier], Text
        """
        identifier_list = super(SynchronousFlyteClient, self).list_task_ids_paginated(
            _common_pb2.NamedEntityIdentifierListRequest(
                project=project,
                domain=domain,
                limit=limit,
                token=token,
                sort_by=None if sort_by is None else sort_by.to_flyte_idl(),
            )
        )
        return (
            [_common.NamedEntityIdentifier.from_flyte_idl(identifier_pb) for identifier_pb in identifier_list.entities],
            str(identifier_list.token),
        )

    def list_tasks_paginated(self, identifier, limit=100, token=None, filters=None, sort_by=None):
        """
        This returns a page of task metadata for tasks in a given project and domain.  Optionally,
        specifying a name will limit the results to only tasks with that name in the given project and domain.

        > [!NOTE]
        > This is a paginated API.  Use the token field in the request to specify a page offset token.
            The user of the API is responsible for providing this token.

        > [!NOTE]
        > If entries are added to the database between requests for different pages, it is possible to receive
            entries on the second page that also appeared on the first.

        :param flytekit.models.common.NamedEntityIdentifier identifier: NamedEntityIdentifier to list.
        :param int limit: [Optional] The maximum number of entries to return.  Must be greater than 0.  The maximum
            page size is determined by the Flyte Admin Service configuration.  If limit is greater than the maximum
            page size, an exception will be raised.
        :param int token: [Optional] If specified, this specifies where in the rows of results to skip before reading.
            If you previously retrieved a page response with token="foo" and you want the next page,
            specify token="foo". Please see the notes for this function about the caveats of the paginated API.
        :param list[flytekit.models.filters.Filter] filters: [Optional] If specified, the filters will be applied to
            the query.  If the filter is not supported, an exception will be raised.
        :param flytekit.models.admin.common.Sort sort_by: [Optional] If provided, the results will be sorted.
        :raises: TODO
        :rtype: list[flytekit.models.task.Task], Text
        """
        task_list = super(SynchronousFlyteClient, self).list_tasks_paginated(
            resource_list_request=_common_pb2.ResourceListRequest(
                id=identifier.to_flyte_idl(),
                limit=limit,
                token=token,
                filters=_filters.FilterList(filters or []).to_flyte_idl(),
                sort_by=None if sort_by is None else sort_by.to_flyte_idl(),
            )
        )
        # TODO: tmp workaround
        for pb in task_list.tasks:
            pb.id.resource_type = _identifier.ResourceType.TASK
        return (
            [_task.Task.from_flyte_idl(task_pb2) for task_pb2 in task_list.tasks],
            str(task_list.token),
        )

    @lru_cache
    def get_task(self, id):
        """
        This returns a single task for a given identifier.

        :param flytekit.models.core.identifier.Identifier id: The ID representing a given task.
        :raises: TODO
        :rtype: flytekit.models.task.Task
        """
        return _task.Task.from_flyte_idl(
            super(SynchronousFlyteClient, self).get_task(_common_pb2.ObjectGetRequest(id=id.to_flyte_idl()))
        )

    ####################################################################################################################
    #
    #  Workflow Endpoints
    #
    ####################################################################################################################

    def create_workflow(self, workflow_identifier, workflow_spec):
        """
        This will create a workflow definition in the Admin database. Once successful, the workflow object can be
        retrieved via the client or viewed via the UI or command-line interfaces.

        > [!NOTE]
        > Overwrites are not supported so any request for a given project, domain, name, and version that exists in
            the database must match the existing definition exactly. Furthermore, as long as the request
            remains identical, calling this method multiple times will result in success.
