"""
This groups the standard functions including instantiation of our ttlin components numbered 0,1,2,3
Note that ttlin are all TTLInOut, they are just hard-set to be input only if this ever changes, we could accidentally blow up the ttl input by having it in output mode and sending in a signal (as the resistance is very low in output mode) see https://github.com/m-labs/artiq/blob/master/artiq/coredevice/ttl.py for details on functionality
"""

import numpy as np

from local_system.system import *
import artiq.coredevice.ttl


class ttlinModule(DaxModule):
	# Module to control ttl inputs
	_init_kernel: bool

	
	def build(self, *ttlins: str, init_kernel: bool = False) -> None:  # type: ignore[override]
		"""Build the LED module.

		:param ttlins: Keys of the ttl input devices to use in order from least to most significant ie. 'ttl0','ttl1' in a list
		:param init_kernel: Run initialization kernel during default module initialization
		"""
	
		# Check inputs
		if not 1 <= len(ttlins) <= 4:
			raise TypeError("Number of ttl inputs listed must be in the range [1...4]")
		assert all(isinstance(ttlin, str) for ttlin in ttlins), 'Provided ttl inputs must be of type str'
		assert isinstance(init_kernel, bool), 'Init kernel flag must be of type bool'

		# Store attributes
		self._init_kernel = init_kernel
		self.logger.debug(f'Init kernel: {self._init_kernel}')
	
		# TTL array
		self.ttlin = [self.get_device(led, artiq.coredevice.ttl.TTLInOut) for ttlin in ttlins]
		self.update_kernel_invariants('ttlin')
		self.logger.debug(f"Number of ttlin's: {len(self.ttlin)}")


	def init(self, *, force: bool = False) -> None:
		"""Initialize this module.

		:param force: Force full initialization
		"""
		if self._init_kernel or force:
			# Initialize the ttlin's if the init flag is set
			self.logger.debug('Running initialization kernel')
			self.init_kernel()

	@kernel
	def init_kernel(self):  # type: () -> None
		"""Kernel function to initialize this module.

		This function is called automatically during initialization unless the user configured otherwise.
		In that case, this function has to be called manually.
		"""
		# Reset the core
		self.core.reset()

		# Turn all ttlin's to input mode
		self.input()

		# Wait until event is submitted
		self.core.wait_until_mu(now_mu())

	def post_init(self) -> None:
		pass

	"""Module functionality as in the inherited functions for anything that derives from this"""

	@kernel
	def set_sens(self, value: TInt32 = 1,index: TInt32 = 0):
		# value is 1 if detecting rising edge, 2 if detecting falling edge, 3 if detecting both, 0 if detecting none
		self.ttlin[index]._set_sensitivity(self, value)
		
	@kernel
	def gate_rising_mu(self, duration: TInt32 = 1,index: TInt32 = 0):
		self.ttlin[index]._set_sensitivity(1)
		delay_mu(duration)
		self.ttlin[index]._set_sensitivity(0)
		return now_mu()
        	
	@kernel
	def gate_falling_mu(self, duration: TInt32 = 1,index: TInt32 = 0):
		self.ttlin[index]._set_sensitivity(2)
		delay_mu(duration)
		self.ttlin[index]._set_sensitivity(0)
		return now_mu()
			
	@kernel
	def gate_both_mu(self, duration: TInt32 = 1,index: TInt32 = 0):
		self.ttlin[index]._set_sensitivity(3)
		delay_mu(duration)
		self.ttlin[index]._set_sensitivity(0)
		return now_mu()
			
	@kernel
	def gate_rising(self, duration: TFloat = 1.0*us,index: TInt32 = 0):
		self.ttlin[index]._set_sensitivity(1)
		delay(duration)
		self.ttlin[index]._set_sensitivity(0)
		return now_mu()
			
	@kernel
	def gate_falling(self, duration: TFloat = 1.0*us,index: TInt32 = 0)):
		self.ttlin[index]._set_sensitivity(2)
		delay(duration)
		self.ttlin[index]._set_sensitivity(0)
		return now_mu()	
		
	@kernel
	def gate_both(self, duration: TFloat = 1.0*us,index: TInt32 = 0)):	
		self.ttlin[index]._set_sensitivity(3)
		delay(duration)
		self.ttlin[index]._set_sensitivity(0)
		return now_mu()	
# Here's where I stopped trying to build my own base module for the ttlinputs		
	@kernel
	def count():
	
	@kernel 
	def timestamp_mu():
	
	


