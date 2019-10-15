# -*- coding: utf-8 -*-
#
import re
import sys

import statsd

from flytekit.configuration import StatsConfig

RESERVED_TAG_WORDS = frozenset(
    ["asg", "az", "backend", "canary", "host", "period", "region", "shard", "window", "source"]
)

# TODO should this be a whitelist instead?
FORBIDDEN_TAG_VALUE_CHARACTERS = re.compile("[|.:]")

_stats_client = None


class ScopeableStatsProxy(object):
    """
    A Proxy object for an underlying statsd client.
    Adds a new call, scope(prefix), which returns a new proxy to the same
    client which will prefix all calls to underlying methods with the scoped prefix:
    new_client = client.get_stats('a')
