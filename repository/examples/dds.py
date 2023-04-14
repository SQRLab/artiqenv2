from artiq.coredevice.ad9910 import RAM_MODE_CONT_RAMPUP
from artiq.experiment import *
from local_system.system import *
from dax.experiment import *

class DDSDash(SQRLSystem, EnvExperiment):
	#We initialize both the core and the dds0 we intend to use
	def build(self):
	
		super(DDSDash,self).build() #this builds all the dds's and the core
		

		self._dds_num = self.get_argument('DDS number [0,1,2]', 
			NumberValue(0, min=0, max=2, step=1, ndecimals=0))
		self._dds_chan = self.get_argument('DDS channel [0,1,2,3]', 
			NumberValue(0, min=0, max=3, step=1, ndecimals=0))
		#self._dds_index = self._dds_num*4 + self._dds_chan
		#self._cpld_index = self._dds_num
		
		#These input ranges should match the hardware capabilities here https://m-labs.hk/docs/sinara-datasheets/4410-4412.pdf 
		self._frequency = self.get_argument('Frequency of signal (MHz)',
			 NumberValue(5.0, min=3.2, max=60.0, step=0.25e-6, ndecimals=8))
		self._amplitude = self.get_argument('Amplitude of signal (fraction of max voltage)',
			 NumberValue(1.0, min=0.01, max=1.0, step=0.01, ndecimals=2))
		self._phase = self.get_argument('Phase Offset of signal (turns [which is 2Pi rads])',
			 NumberValue(0.0, min=0.0, max=1.0, step=0.00002, ndecimals=5))
		self._att = self.get_argument('Attenuation of the signal (db)',
			 NumberValue(6.0, min=0.0, max=31.5, step=0.1, ndecimals=1))
		self._pulse_length = self.get_argument('Duration of signal (ms)',
			 NumberValue(500.0, min=0.0, max=600000.0, step=1.0, ndecimals=3))		
		self.update_kernel_invariants('_dds_num','_dds_chan','_frequency','_amplitude',
			'_phase','_att','_pulse_length')
        	
	def prepare(self):
		self.phase = [self._phase,self._phase,self._phase] # phase values in units of turns[2Pi rads]
		self.amp = [self._amplitude,self._amplitude,self._amplitude] # amplitude values 0-1.0 fraction of max voltage
		self.asf_ram = [0] * len(self.amp) # This initializes the array we write to the hardware
		self.pow_ram = [0] * len(self.phase) # This initializes the array we write to the hardware
		
	@kernel
	def init_dds(self, dds):
		self.core.break_realtime() #this allows the computer to catch up to the kasli
		dds.init() #this initializes the passed device
		dds.set_att(self._att*dB) #we set the attenuation of our signal to 6dB
		dds.cfg_sw(True) #sets the CPLD CFG RF switch state to True, enabling output signals

	@kernel
	def configure_ram_mode(self, dds):
		self.core.break_realtime()#let computer catch up
		dds.set_cfr1(ram_enable=0)#This is the correct mode for loading or reading values
		self.cpld.cpld[self._dds_num].io_update.pulse_mu(8)#this sends an 8 machine unit long pulse of TTL signal internally to trigger the updated ram_enable value
		
		#first update done
		
		self.cpld.cpld[self._dds_num].set_profile(0) # Enable the corresponding RAM profile 
		# Profile 0 is the default, the options are 0,1,2,3,4,5,6,7
		dds.set_profile_ram(start=0, end=len(self.asf_ram)-1, step=250, profile=0, mode=RAM_MODE_CONT_RAMPUP) # this says to start the RAM profile at bit0, continue for the length of our asf_ram list, take 250 t_DDS[4ns] for each element in the RAM profile, using the reference for profile 0, our actual signal seems to be 4 times as long on the DS1102E oscilloscope
		self.cpld.cpld[self._dds_num].io_update.pulse_mu(8)#another ttl pulse to apply the previous updates
		
		#second update done
		
		dds.turns_amplitude_to_ram(self.phase,self.amp, self.asf_ram)#this writes the amplitude values from the computer self.amp to the other computer array that we will write onto the RAM, self.asf_ram in units of full scale (fractional from max, I think) 
		dds.write_ram(self.asf_ram)#this writes the array self.asf_ram to the active RAM profile[0] using the step[250ns], start[0], and end[6] address set by set_profile_ram and self.urukul0_cpld.set_profile
		self.core.break_realtime()#Let the computer catch up		
		
		dds.set(frequency=self._frequency*MHz, ram_destination=3)#emit a 5MHz rf signal using the RAM values at the given ram_destination 2 is ASF[amplitude modulation], 0 is FTW[frequency tuning modulation], 1 is POW[phase offset], 3is POWASF[combined phase and amplitude modulation?]
		# Pass osk_enable=1 to set_cfr1() if it is not an amplitude RAM
		dds.set_cfr1(ram_enable=1, ram_destination=3)#this enables ram values to play back
		self.cpld.cpld[self._dds_num].io_update.pulse_mu(8)#another ttl pulse to apply the last set of updates
		
		#third update done
		
		
	@kernel
	def run(self):
		self.core.reset()#kill old threads
		self.core.break_realtime()#let computer catch up
		self.cpld.cpld[self._dds_num].init()#initialize switch
		delay(500*ms) #wait to prevent underflow errors, we can probably reduce this in the future
		self.init_dds(self.dds.dds[self._dds_num*4 + self._dds_chan])#see function dds refers to given device
		self.configure_ram_mode(self.dds.dds[self._dds_num*4 + self._dds_chan])#see function dds refers to given device
		#self._dds_num*4 + self._dds_chan
		delay(self._pulse_length*ms) #send for 5000ms
		self.dds.dds[self._dds_num*4 + self._dds_chan].power_down()	#turn off the signal
		self.dds.dds[self._dds_num*4 + self._dds_chan].cfg_sw(False)	#turn off the output switch

