"""
This is a deprecated module. Model files for plugins should go alongside the microlib.
See ``plugins/flytekit-kf-pytorch/flytekitplugins/kfpytorch/models.py`` as an example.
"""

## Todo - change this to qubole_presto once Luis's PR gets merged
# from flyteidl.plugins import qubole_presto as _qubole
from flyteidl.plugins import presto_pb2 as _presto

from flytekit.models import common as _common


class PrestoQuery(_common.FlyteIdlEntity):
    def __init__(self, routing_group=None, catalog=None, schema=None, statement=None):
        """
        Initializes a new PrestoQuery.

        :param string routing_group:
        :param string catalog:
        :param string schema:
        :param string statement:

