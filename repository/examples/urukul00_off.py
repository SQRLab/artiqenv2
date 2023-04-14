from artiq.experiment import *

class Tutorial(EnvExperiment):
	#We initialize both the core and the dds0 we intend to use
	def build(self):
        	self.setattr_device("core")
        	self.setattr_device("urukul0_ch0")
        	self.setattr_device("urukul0_cpld")
        
	@kernel
	def run(self):
		self.core.reset()
		self.urukul0_cpld.init()
		self.urukul0_ch0.init()

