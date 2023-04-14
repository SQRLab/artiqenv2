"""
DAX has a notion of clients which are abstract experiments that can be instantiated against a DAX system.

This file instantiates an introspect experiment that is used to generate visual representations of your system.
The experiment generates PDF files that show the hierarchy and relations of module and services.
"""

import dax.clients.introspect

from local_system.system import *


# noinspection PyTypeChecker
class Introspect(dax.clients.introspect.Introspect(SQRLSystem)):
    pass
