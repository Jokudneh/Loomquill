from collections import OrderedDict

import flytekit.configuration
from flytekit.configuration import Image, ImageConfig
from flytekit.tools.translator import get_serializable
from tests.flytekit.unit.extras.sqlite3.test_task import tk as not_tk


def test_sql_lhs():
    assert not_tk.lhs == "tk"


def test_sql_command():
    default_img = Image(name="default", fqn="test", tag="tag")
    serialization_settings = flytekit.configuration.SerializationSettings(
