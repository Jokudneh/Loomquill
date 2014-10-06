from flytekit.models.admin import common

DEFAULT_SORT_ASC = common.Sort(key="created_at", direction=common.Sort.Direction.ASCENDING)


def iterate_node_executions(
    client,
    workflow_execution_identifier=None,
    task_execution_identifier=None,
    limit=None,
    filters=None,
    sort_by=DEFAULT_SORT_ASC,
    unique_parent_id=None,
):
    """
    This returns a generator for node executions.
    :param flytekit.clients.friendly.SynchronousFlyteClient client:
    :param flytekit.models.core.identifier.WorkflowExecutionIdentifier workflow_execution_identifier:
    :param flytekit.models.core.identifier.TaskExecutionIdentifier task_execution_identifier:
    :param int limit: The maximum number of elements to retrieve
    :param list[flytekit.models.filters.Filter] filters:
    :param flytekit.models.admin.common.Sort sort_by: [Optional] Defaults to created_at field in ASC order.
    :rtype: Iterator[flytekit.models.node_execution.NodeExecution]
    """
