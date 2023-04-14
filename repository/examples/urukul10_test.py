from artiq.experiment import *

class Tutorial(EnvExperiment):
	#We initialize both the core and the dds0 we intend to use
	def build(self):
        	self.setattr_device("core")
        	self.setattr_device("urukul1_ch0")
        	self.setattr_device("urukul1_cpld")
        
	@kernel
	def run(self):
		self.core.reset()
		self.urukul1_cpld.init()
		self.urukul1_ch0.init()
		self.urukul1_ch0.cfg_sw(True)
		self.urukul1_ch0.set_att(6.*dB)
		self.urukul1_ch0.set(10*MHz)
		delay(5000*ms)
		self.urukul1_ch0.power_down()
		
