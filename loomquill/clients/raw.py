from __future__ import annotations

import typing

import grpc
from flyteidl.admin.project_pb2 import GetDomainRequest, ProjectListRequest
from flyteidl.admin.signal_pb2 import SignalList, SignalListRequest, SignalSetRequest, SignalSetResponse
from flyteidl.service import admin_pb2_grpc as _admin_service
from flyteidl.service import dataproxy_pb2 as _dataproxy_pb2
from flyteidl.service import dataproxy_pb2_grpc as dataproxy_service
from flyteidl.service import signal_pb2_grpc as signal_service
from flyteidl.service.dataproxy_pb2_grpc import DataProxyServiceStub

from flytekit.clients.auth_helper import (
    get_channel,
    upgrade_channel_to_authenticated,
    upgrade_channel_to_proxy_authenticated,
    wrap_exceptions_channel,
)
from flytekit.configuration import PlatformConfig
from flytekit.loggers import logger


class RawSynchronousFlyteClient(object):
    """
    This is a thin synchronous wrapper around the auto-generated GRPC stubs for communicating with the admin service.

    This client should be usable regardless of environment in which this is used. In other words, configurations should
    be explicit as opposed to inferred from the environment or a configuration file. To create a client,

    ```python
    from flytekit.configuration import PlatformConfig
    RawSynchronousFlyteClient(PlatformConfig(endpoint="a.b.com", insecure=True))  # or
    SynchronousFlyteClient(PlatformConfig(endpoint="a.b.com", insecure=True))
    ```
    """

    _dataproxy_stub: DataProxyServiceStub

    def __init__(self, cfg: PlatformConfig, **kwargs):
        """
        Initializes a gRPC channel to the given Flyte Admin service.

        Args:
          url: The server address.
          insecure: if insecure is desired
        """
        # Set the value here to match the limit in Admin, otherwise the client will cut off and the user gets a
        # StreamRemoved exception.
        # https://github.com/flyteorg/flyte/blob/e8588f3a04995a420559327e78c3f95fbf64dc01/flyteadmin/pkg/common/constants.go#L14
        # 32KB for error messages, 20MB for actual messages.
        # Keepalive options let gRPC detect dead connections (idle TCP drops by
        # load balancers / NAT) and reconnect transparently, instead of leaving
        # subsequent RPCs blocked indefinitely on a black-hole socket.
        options = [
            ("grpc.max_metadata_size", 32 * 1024),
            ("grpc.max_receive_message_length", 20 * 1024 * 1024),
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.keepalive_permit_without_calls", 1),
            ("grpc.http2.max_pings_without_data", 0),
        ] + kwargs.pop("options", [])
        self._cfg = cfg
        self._channel = wrap_exceptions_channel(
            cfg,
            upgrade_channel_to_authenticated(
                cfg, upgrade_channel_to_proxy_authenticated(cfg, get_channel(cfg, options=options, **kwargs))
            ),
        )
        self._stub = _admin_service.AdminServiceStub(self._channel)
        self._signal = signal_service.SignalServiceStub(self._channel)
        self._dataproxy_stub = dataproxy_service.DataProxyServiceStub(self._channel)

        logger.info(
            f"Flyte Client configured -> {self._cfg.endpoint} in {'insecure' if self._cfg.insecure else 'secure'} mode."
        )
        # metadata will hold the value of the token to send to the various endpoints.
        self._metadata = None

    @classmethod
    def with_root_certificate(cls, cfg: PlatformConfig, root_cert_file: str) -> RawSynchronousFlyteClient:
        b = None
        with open(root_cert_file, "rb") as fp:
            b = fp.read()
        return RawSynchronousFlyteClient(cfg, credentials=grpc.ssl_channel_credentials(root_certificates=b))

    @property
    def url(self) -> str:
        return self._cfg.endpoint

    ####################################################################################################################
    #
    #  Task Endpoints
    #
    ####################################################################################################################

    def create_task(self, task_create_request):
        """
        This will create a task definition in the Admin database. Once successful, the task object can be
        retrieved via the client or viewed via the UI or command-line interfaces.

        > [!NOTE]
        > Overwrites are not supported so any request for a given project, domain, name, and version that exists in
            the database must match the existing definition exactly. This also means that as long as the request
            remains identical, calling this method multiple times will result in success.

        :param: flyteidl.admin.task_pb2.TaskCreateRequest task_create_request: The request protobuf object.
        :rtype: flyteidl.admin.task_pb2.TaskCreateResponse
        :raises flytekit.common.exceptions.user.FlyteEntityAlreadyExistsException: If an identical version of the task
            is found, this exception is raised.  The client might choose to ignore this exception because the identical
            task is already registered.
        :raises grpc.RpcError:
        """
        return self._stub.CreateTask(task_create_request, metadata=self._metadata)
