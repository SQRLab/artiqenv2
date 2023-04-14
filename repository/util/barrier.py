"""
DAX contains a few simple experiments that are ready to use.
This file imports the barrier experiment that can be used to block experiments from running on a system.

Note that the barrier experiment also has a function :func:`Barrier.submit`.
Every experiment can call this function to immediately submit a barrier experiment.
"""

from dax.util.experiments import Barrier  # noqa: F401
