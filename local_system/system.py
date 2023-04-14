import logging

from dax.experiment import *

from dax.modules.led import LedModule #this is in the dax directory 
from dax.modules.cpld_init import CpldInitModule
from local_system.modules.ttlout import TtlOutModule
from local_system.modules.dds import DdsModule

class SQRLSystem(DaxSystem):
    """
    This is based on the dax_example but will hold the various modules representing our subsystems. We'll want this to have functionality for the dds, ttl, camera grabber, zotino (DC array), and Sampler (adc) systems. Eventually we'll need to specialize these for our system.
    """
    SYS_ID = 'sqrl_system'
    SYS_VER = 1
    DAX_INFLUX_DB_KEY = None

    def build(self):
        # Adjust logging level
        self.logger.setLevel(min(self.logger.getEffectiveLevel(), logging.INFO))

        # Call super
        super(SQRLSystem, self).build()

        # Add standard modules
        self.led = LedModule(self, 'led', *('led0', 'led1'), init_kernel=False) #this loads in our leds as self.led.led[index]
        self.cpld = CpldInitModule(self, 'cpld', init_kernel=False) #this loads in the urukul cpld devices such as urukul1_cpld (from the device_db) as self.cpld.cpld[index]?
        self.update_kernel_invariants('led', 'cpld')

        # Add custom modules [I need to make these modules, but once I do, we never have to worry about instantiating in any of the programs]
	#self.ttlin = TtlInModule(self, 'ttlin', *('ttl0', 'ttl1','ttl2','ttl3'), init_kernel=False)
        self.ttlout = TtlOutModule(self, 'ttlout', *('ttl4', 'ttl5','ttl6','ttl7','ttl8', 'ttl9','ttl10','ttl11','ttl12', 'ttl13','ttl14','ttl15'), init_kernel=False)
        self.dds = DdsModule(self,'dds',*('urukul0_ch0','urukul0_ch1','urukul0_ch2','urukul0_ch3',
                'urukul1_ch0','urukul1_ch1','urukul1_ch2','urukul1_ch3',
                'urukul2_ch0','urukul2_ch1','urukul2_ch2','urukul2_ch3'))
        self.update_kernel_invariants('ttlout','dds')
        	
    @kernel
    def init(self):
        # Call all initialization kernels at once, merging multiple smaller kernels into one
        self.led.init_kernel()
        self.cpld.init_kernel()
