from artiq.experiment import *
from local_system.system import *
from dax.experiment import *

def print_underflow():
	print("RTIO underflow occured")

class TTLDash(SQRLSystem,EnvExperiment):
    #We initialize both the core and the ttl0 we intend to use
    def build(self):
        super(TTLDash,self).build() #this builds all the ttlout's and the core

        self._ttl_num = self.get_argument('Output TTL Index [4-15]', NumberValue(5, min=4, max=15, step=1, ndecimals=0))
        self._pulses = self.get_argument('Number of Pulses', NumberValue(1, min=0, max=1000000, step=1, ndecimals=0))
        self._high_duration = self.get_argument('Duration of high signal (seconds)', NumberValue(0.4*us, min=0.4*us, max=1, step=1*us, ndecimals=7))
        self._low_duration = self.get_argument('Duration of low signal (seconds)', NumberValue(0.4*us, min=0.4*us, max=1, step=1*us, ndecimals=7))
        self.update_kernel_invariants('_ttl_num','_pulses','_high_duration','_low_duration')
        
                
    @kernel
    def run(self):
        self.core.reset() #I think this cancels previous instructions that may be hanging
        self.ttlout.ttl[self._ttl_num-4].output() #This sets the ttl0 to output mode, by default it is in high impedance input mode
        try:
        	for i in range(self._pulses):#we send _pulses number of pulses with _low and _high duration through _ttl_num ttl
            		delay(self._low_duration)
            		self.ttlout.ttl[self._ttl_num-4].pulse(self._high_duration) #sub 800ns for a full cycle causes underflow errors
        except:
         	print_underflow()


        #as of writing this code, 0,1,2,3 are all permanently set to input mode 4 works and I expect the other ones with led reading out also function to send signals
        #ttl0,1,2,3 are also apparently [see device_db.py] the only ones capable of being set to input, they may have a hardware switch set to input only at the moment as per their schematics
