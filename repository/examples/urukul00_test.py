from artiq.experiment import *

class Tutorial(EnvExperiment):
	#We initialize both the core and the dds0 we intend to use
	def build(self):
		#the kasli
        	self.setattr_device("core")
        	#the rf output device
        	self.setattr_device("urukul0_ch0")
        	#the switch controller
        	self.setattr_device("urukul0_cpld")
        
	@kernel
	def run(self):
		#ends old threads
		self.core.reset()
		#turn on the switch then the rf device
		self.urukul0_cpld.init()
		self.urukul0_ch0.init()
		delay(500*ms)
		#enable output from rf device
		self.urukul0_ch0.cfg_sw(True)
		#attenuate output
		self.urukul0_ch0.set_att(6.*dB)
		delay(500*ms)
		#set frequency
		self.urukul0_ch0.set(10*MHz)
		#wait 5 real seconds
		delay(5000*ms)
		#turn off the signal
		self.urukul0_ch0.power_down()
		#turn off the output switch
		self.urukul0_ch0.cfg_sw(False)		
