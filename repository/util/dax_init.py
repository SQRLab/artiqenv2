"""
One important feature of a DAX system is the initialization function ``dax_init()`.
With this function, all devices in a system can be put into a well-defined state before starting an experiment.
The DAX initialization experiment just calls the ``dax_init()`` function.
"""

from local_system.system import *


class DaxInit(SQRLSystem, EnvExperiment):
    """DAX initialization"""

    def run(self):
        # Initialize system
        self.dax_init()
