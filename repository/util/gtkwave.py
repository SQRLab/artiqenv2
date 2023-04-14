"""
DAX has a notion of clients which are abstract experiments that can be instantiated against a DAX system.

This file instantiates a GTKWave save generator experiment that can be used to generate GTKWave save files.
These save files can be used when inspecting VCD simulation output from DAX.sim.
"""

import dax.clients.gtkwave

from local_system.system import *


# noinspection PyTypeChecker
class GTKWaveSaveGenerator(dax.clients.gtkwave.GTKWaveSaveGenerator(SQRLSystem)):
    """GTKWave save file generator"""
    pass
