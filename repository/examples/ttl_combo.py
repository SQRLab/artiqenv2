from artiq.experiment import *

def print_underflow():
	print("RTIO underflow occured")

class Tutorial(EnvExperiment):
	#We initialize both the core and the ttl0 we intend to use
	def build(self):
		self.setattr_device("core")
		self.setattr_device("ttl4")
		self.setattr_device("ttl5")

	@kernel
	def run(self):
		self.core.reset() #I think this cancels previous instructions that may be hanging
		self.ttl4.output() #This sets the ttl0 to output mode, by default it is in high impedance input mode
		self.ttl5.output() #This sets the ttl0 to output mode, by default it is in high impedance input mode
		try:
			for i in range(1000000):
				with parallel:
					self.ttl4.pulse(2*us)
					self.ttl5.pulse(4*us)
				delay(4*us)
		except:
			print_underflow()



