from datetime import datetime

import yaml
from flyteidl.core import metrics_pb2 as _metrics_pb2

from flytekit.models import common as _common_models


def aggregate_spans(spans):
    breakdown = {}

    tasks = {}
    nodes = {}
    workflows = {}

    for span in spans:
        id_type = span.WhichOneof("id")
        if id_type == "operation_id":
            operation_id = span.operation_id

            start_time = datetime.fromtimestamp(span.start_time.seconds + span.start_time.nanos / 1e9)
            end_time = datetime.fromtimestamp(span.end_time.seconds + span.end_time.nanos / 1e9)
            total_time = (end_time - start_time).total_seconds()

            if operation_id in breakdown:
                breakdown[operation_id] += total_time
            else:
                breakdown[operation_id] = total_time
        else:
            id, underlying_span = aggregate_reference_span(span)

            if id_type == "workflow_id":
                workflows[id] = underlying_span
            elif id_type == "node_id":
                nodes[id] = underlying_span
            elif id_type == "task_id":
                tasks[id] = underlying_span

            for operation_id, total_time in underlying_span["breakdown"].items():
                if operation_id in breakdown:
                    breakdown[operation_id] += total_time
                else:
                    breakdown[operation_id] = total_time

