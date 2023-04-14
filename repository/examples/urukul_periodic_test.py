from artiq.coredevice.ad9910 import RAM_MODE_CONT_RAMPUP
from artiq.experiment import *

class Tutorial(EnvExperiment):
	#We initialize both the core and the dds0 we intend to use
	def build(self):
		#this is the kasli
        	self.setattr_device("core")
        	#this is the rf output
        	self.setattr_device("urukul0_ch0")
        	#this is the thing that controls switches and clocks
        	self.setattr_device("urukul0_cpld")
        	
	def prepare(self):
		#self.amp = [0.0, 0.0, 0.0, 0.7, 0.0, 0.7, 0.7] # Reversed Order periodic		
		self.amp = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0] # Reversed Order ramp up
		self.asf_ram = [0] * len(self.amp) # This one is therefore all 0's but the length of the above
	@kernel
	def init_dds(self, dds):
		self.core.break_realtime() #this allows the computer to catch up to the kasli
		dds.init() #this initializes the passed device
		dds.set_att(6.*dB) #we set the attenuation of our signal to 6dB
		dds.cfg_sw(True) #sets the CPLD CFG RF switch state to True, enabling output signals

	@kernel
	def configure_ram_mode(self, dds):
		self.core.break_realtime()#let computer catch up
		dds.set_cfr1(ram_enable=0)#This is the correct mode for loading or reading values
		self.urukul0_cpld.io_update.pulse_mu(8)#this sends an 8 machine unit long pulse of TTL signal internally to trigger the updated ram_enable value
		
		#first update done
		
		self.urukul0_cpld.set_profile(0) # Enable the corresponding RAM profile
		# Profile 0 is the default, the options are 0,1,2,3,4,5,6,7
		dds.set_profile_ram(start=0, end=len(self.asf_ram)-1, step=250, profile=0, mode=RAM_MODE_CONT_RAMPUP) # this says to start the RAM profile at bit0, continue for the length of our asf_ram list, take 250 t_DDS[4ns] for each element in the RAM profile, using the reference for profile 0, our actual signal seems to be 4 times as long on the DS1102E oscilloscope
		self.urukul0_cpld.io_update.pulse_mu(8)#another ttl pulse to apply the previous updates
		
		#second update done
		
		dds.amplitude_to_ram(self.amp, self.asf_ram)#this writes the amplitude values from the computer self.amp to the other computer array that we will write onto the RAM, self.asf_ram in units of full scale (fractional from max, I think) 
		dds.write_ram(self.asf_ram)#this writes the array self.asf_ram to the active RAM profile[0] using the step[250ns], start[0], and end[6] address set by set_profile_ram and self.urukul0_cpld.set_profile
		self.core.break_realtime()#Let the computer catch up
		
		dds.set(frequency=5*MHz, ram_destination=2)#emit a 5MHz rf signal using the RAM values at the given ram_destination 2 is ASF[amplitude modulation], 0 is FTW[frequency tuning modulation], 1 is POW[phase offset], 3is POWASF[combined phase and amplitude modulation?]
		# Pass osk_enable=1 to set_cfr1() if it is not an amplitude RAM
		dds.set_cfr1(ram_enable=1, ram_destination=2)#this enables ram values to play back
		self.urukul0_cpld.io_update.pulse_mu(8)#another ttl pulse to apply the last set of updates
		
		#third update done
		
	@kernel
	def run(self):
		self.core.reset()#kill old threads
		self.core.break_realtime()#let computer catch up
		self.urukul0_cpld.init()#initialize switch
		self.init_dds(self.urukul0_ch0)#see function dds refers to given device
		self.configure_ram_mode(self.urukul0_ch0)#see function dds refers to given device
		
		delay(5000*ms) #send for 5000ms
		self.urukul0_ch0.power_down()	#turn off the signal
		self.urukul0_ch0.cfg_sw(False)	#turn off the output switch

