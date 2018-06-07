import random as _random

random = _random.Random()
"""
An instance of the global random number generator used by flytekit.  Flytekit maintains it's own random instance
to ensure that calls to random.seed(...) do not affect the pseudo-random behavior of flytekit. This random should be
