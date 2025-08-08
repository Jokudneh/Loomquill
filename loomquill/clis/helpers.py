import sys
from typing import Tuple, Union

import click
from flyteidl.admin.launch_plan_pb2 import LaunchPlan
from flyteidl.admin.task_pb2 import TaskSpec
from flyteidl.admin.workflow_pb2 import WorkflowSpec
from flyteidl.core import identifier_pb2 as _identifier_pb2
from flyteidl.core import workflow_pb2 as _workflow_pb2

from flytekit.configuration import DOMAIN_PLACEHOLDER, PROJECT_PLACEHOLDER, VERSION_PLACEHOLDER


def parse_args_into_dict(input_arguments):
    """
    Takes a tuple like (u'input_b=mystr', u'input_c=18') and returns a dictionary of input name to the
    original string value

    :param Tuple[Text] input_arguments:
    :rtype: dict[Text, Text]
    """

    return {split_arg[0]: split_arg[1] for split_arg in [input_arg.split("=", 1) for input_arg in input_arguments]}


def str2bool(str):
    """
    bool('False') is True in Python, so we need to do some string parsing.  Use the same words in ConfigParser
    :param Text str:
    :rtype: bool
    """
    return str.lower() not in ["false", "0", "off", "no"]


# TODO Deprecated delete after deleting flyte_cli register
def _hydrate_identifier(
