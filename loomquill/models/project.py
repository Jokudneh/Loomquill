from flyteidl.admin import project_pb2 as _project_pb2

from flytekit.models import common as _common


class Project(_common.FlyteIdlEntity):
    class ProjectState(object):
        ACTIVE = _project_pb2.Project.ACTIVE
        ARCHIVED = _project_pb2.Project.ARCHIVED
        SYSTEM_GENERATED = _project_pb2.Project.SYSTEM_GENERATED

    def __init__(self, id, name, description, state=ProjectState.ACTIVE):
        """
        A project represents a logical grouping used to organize entities (tasks, workflows, executions) in the Flyte
        platform.

        :param Text id: A globally unique identifier associated with this project.
        :param Text name: A human-readable name for this project.
        :param Text name: A concise description for this project.
        """
