from typing import Dict

from flytekit.configuration import StatsConfig
from flytekit.interfaces.stats import client as _stats_client


class TaggableStats(_stats_client.ScopeableStatsProxy):
    # List of functions we will proxy and prefix the first string argument on
    EXTENDABLE_FUNC = ["incr", "decr", "timing", "timer", "gauge", "set"]

    def __init__(self, client, full_prefix, cfg: StatsConfig, prefix=None, tags=None):
        super(TaggableStats, self).__init__(client, prefix=prefix)
        self._tags = tags if tags else {}
        self._full_prefix = full_prefix
        self._cfg = cfg

    def _create_wrapped_function(self, base_func):
        if self._scope_prefix:

            def name_wrap(stat, *args, **kwargs):
                tags = kwargs.pop("tags", {})
                tags.update(self._tags)
                if kwargs.pop("per_host", False):
                    tags["_f"] = "i"

