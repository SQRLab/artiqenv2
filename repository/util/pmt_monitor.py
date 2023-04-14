"""
DAX has a notion of clients which are abstract experiments that can be instantiated against a DAX system.

This file instantiates PMT monitor experiments that can be used to monitor input on one or more PMT channels.
The PMT monitor experiments are highly configurable and utilize hardware buffers for maximum RTIO performance.
"""

import dax.clients.pmt_monitor

from local_system.system import *


# noinspection PyTypeChecker
#class PmtMonitor(dax.clients.pmt_monitor.PmtMonitor(SQRLSystem)):
#    """PMT monitor"""
#    pass


# noinspection PyTypeChecker
#class MultiPmtMonitor(dax.clients.pmt_monitor.MultiPmtMonitor(SQRLSystem)):
#    """Multi PMT monitor"""
#    pass
