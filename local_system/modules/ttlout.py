# Based on the LedModule by DAX
import numpy as np

import artiq.coredevice.ttl  # type: ignore[import]

from dax.experiment import *

__all__ = ['TtlOutModule']


class TtlOutModule(DaxModule):
    """Module to control user ttl output's."""

    _init_kernel: bool

    def build(self, *ttls: str, init_kernel: bool = False) -> None:  # type: ignore[override]
        """Build the TTL Output module.

        :param ttls: Keys of the ttl output devices to use in order from least to most significant
        :param init_kernel: Run initialization kernel during default module initialization
        """
        # Check arguments
        if not 1 <= len(ttls) <= 12:
            raise TypeError("Number of TTL's must be in the range [4..15] with 12 maximum ttl outputs")
        assert all(isinstance(ttl, str) for ttl in ttls), 'Provided ttl keys must be of type str'
        assert isinstance(init_kernel, bool), 'Init kernel flag must be of type bool'

        # Store attributes
        self._init_kernel = init_kernel
        self.logger.debug(f'Init kernel: {self._init_kernel}')

        # ttl array
        self.ttl = [self.get_device(ttl, artiq.coredevice.ttl.TTLOut) for ttl in ttls]
        self.update_kernel_invariants('ttl')
        self.logger.debug(f"Number of TTL Output's: {len(self.ttl)}")

    def init(self, *, force: bool = False) -> None:
        """Initialize this module.

        :param force: Force full initialization
        """
        if self._init_kernel or force:
            # Initialize the TTL's if the init flag is set
            self.logger.debug('Running initialization kernel for ttlouts')
            self.init_kernel()

    @kernel
    def init_kernel(self):  # type: () -> None
        """Kernel function to initialize this module.

        This function is called automatically during initialization unless the user configured otherwise.
        In that case, this function has to be called manually.
        """
        # Reset the core
        self.core.reset()

        # Turn all ttl's off
        self.off_all()

        # Wait until event is submitted
        self.core.wait_until_mu(now_mu())

    def post_init(self) -> None:
        pass

    """Module functionality"""

    @kernel
    def set_o(self, o: TBool, index: TInt32 = 0):
        self.ttl[index].set_o(o)

    @kernel
    def on(self, index: TInt32 = 0):
        self.ttl[index].on()

    @kernel
    def off(self, index: TInt32 = 0):
        self.ttl[index].off()

    @kernel
    def pulse(self, duration: TFloat, index: TInt32 = 0):
        self.ttl[index].pulse(duration)

    @kernel
    def pulse_mu(self, duration: TInt64, index: TInt32 = 0):
        self.ttl[index].pulse_mu(duration)

    #@kernel
    #def on_all(self):  # type: () -> None
    #    """Switch all ttl's on."""
    #    for ttl in self.ttl:
    #        # Number of ttl's does not exceed 15, hence they can all be set in parallel
    #        ttl.on()

    #@kernel
    #def off_all(self):  # type: () -> None
    #    """Switch all ttl's off."""
    #    for ttl in self.ttl:
    #        # Number of ttl's does not exceed 8, hence they can all be set in parallel
    #        ttl.off()

    #@kernel
    #def set_code(self, code: TInt32):
    #    """Visualize the lower bits of the code using the ttl's."""
    #    for ttl in self.ttl:
    #        # Set ttl (explicit casting required)
    #        ttl.set_o(bool(code & np.int32(0x1)))
    #        # Shift code
    #        code >>= np.int32(0x1)

