from datetime import timedelta

import mock
from flyteidl.admin import project_pb2 as _project_pb2
from flyteidl.service import dataproxy_pb2 as _data_proxy_pb2
from google.protobuf.duration_pb2 import Duration

from flytekit.clients.friendly import SynchronousFlyteClient as _SynchronousFlyteClient
from flytekit.configuration import PlatformConfig
from flytekit.models.project import Project as _Project

@mock.patch("flytekit.clients.friendly._RawSynchronousFlyteClient.update_project")
def test_update_project(mock_raw_update_project):
