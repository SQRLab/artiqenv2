from artiq.experiment import *
from local_system.system import *
from dax.experiment import *

# the '-> TBool' component instructs the kernel what value type to expect in return for calling this remote procedure call (RPC) this is a function you can call from the kernel to get an update from the terminal. However, it does not work with the dashboard, hence why it's commented out
#def input_led_state() -> TBool:
#    return input("Enter desired LED state: ") == "1"

#This is the portion of the code that runs on the computer explicitly, building the drivers for accessing these components
class LEDTest(SQRLSystem,Experiment):

    def build(self):
        super(LEDTest,self).build()
        self._led_state = self.get_argument('LED state', BooleanValue(True))
        self._led_num = self.get_argument('LED number', NumberValue(0, min=0, max=1, step=1, ndecimals=0))
        self.update_kernel_invariants('_led_state','_led_num')
        
#This is the portion of the code that runs on or is managed by the kasli
    @kernel
    def run(self):
        self.core.reset() #reset the core, I'm not sure why but it's at the start of every run function
        if self._led_state:
        	self.led.led[self._led_num].on()
        else:
        	self.led.led[self._led_num].off()

