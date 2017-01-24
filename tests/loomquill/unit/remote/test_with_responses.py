import os
import typing
from collections import OrderedDict

import mock
from flyteidl.admin import launch_plan_pb2, task_pb2, workflow_pb2

import flytekit.configuration
from flytekit.configuration import Config, ImageConfig
from flytekit.configuration.default_images import DefaultImages
from flytekit.core.node_creation import create_node
from flytekit.core.utils import load_proto_from_file
from flytekit.core.workflow import workflow
from flytekit.models import launch_plan as launch_plan_models
from flytekit.models import task as task_models
from flytekit.models.admin import workflow as admin_workflow_models
from flytekit.remote.remote import FlyteRemote
from flytekit.tools.translator import get_serializable

rr = FlyteRemote(
