import importlib
import os
import sys
import warnings
from concurrent import futures

import grpc
import rich_click as click
from flyteidl.service import agent_pb2
from flyteidl.service.agent_pb2_grpc import (
    add_AgentMetadataServiceServicer_to_server,
    add_AsyncAgentServiceServicer_to_server,
    add_SyncAgentServiceServicer_to_server,
)
from rich.console import Console
from rich.table import Table


@click.group("serve")
@click.pass_context
def serve(ctx: click.Context):
    """
    Start the specific service.
    """
    pass


@serve.command()
@click.option(
    "--port",
    default="8000",
    is_flag=False,
    type=int,
    help="Grpc port for the agent service",
)
@click.option(
    "--prometheus_port",
    default="9090",
    is_flag=False,
    type=int,
    help="Prometheus port for the agent service",
)
@click.option(
    "--worker",
    default="10",
    is_flag=False,
    type=int,
    help="Number of workers for the grpc server",
)
@click.option(
    "--timeout",
    default=None,
    is_flag=False,
    type=int,
    help="It will wait for the specified number of seconds before shutting down grpc server. It should only be used "
    "for testing.",
