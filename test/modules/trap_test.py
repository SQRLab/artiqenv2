from artiq.experiment import *

import dax.sim.test_case

from dax_example.system import DaxExampleSystem


class TrapTestCase(dax.sim.test_case.PeekTestCase):

    def setUp(self):
        # Construct and initialize system environment
        self.env = self.construct_env(DaxExampleSystem)
        self.env.dax_init()

    def test_cool_config(self):
        for freq in [100 * MHz, 150 * MHz, 300 * MHz]:
            # Test config function
            self.env.trap.cool_config(freq)
            self.expect(self.env.trap._cool_dds, 'freq', freq)
            self.expect(self.env.trap._cool_dds, 'phase', 0.0)

            # Test reset function
            self.env.trap.cool_reset()
            self.expect(self.env.trap._cool_dds, 'freq', self.env.trap._cool_freq)
            self.expect(self.env.trap._cool_dds, 'phase', 0.0)

    def test_cool_pulse(self):
        # Test initial state
        self.expect(self.env.trap._cool_sw, 'state', self.env.trap._cool_init_state)

        # Test default pulse time
        t = now_mu()
        self.env.trap.cool_pulse()
        self.assertEqual(now_mu() - t, self.env.core.seconds_to_mu(self.env.trap._cool_time))
        self.expect(self.env.trap._cool_sw, 'state', False)

        # Test if a pulse results in the correct switching behavior
        for _ in range(4):
            delay(10 * us)
            with parallel:
                self.env.trap.cool_pulse()
                with sequential:
                    self.expect(self.env.trap._cool_sw, 'state', True)
                    delay(self.env.trap._cool_time)
                    self.expect(self.env.trap._cool_sw, 'state', False)
