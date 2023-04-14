from artiq.experiment import *
	
class LED(EnvExperiment):
	def build(self):
		self.setattr_device("core")
		self.setattr_device("led0")
		self.setattr_device("led1")
	@kernel
	def run(self):
		self.core.reset()
		self.led0.on()
		self.led1.on()
