from artiq.experiment import *

import dax.sim.test_case

from dax_example.system import DaxExampleSystem


class DetectionTestCase(dax.sim.test_case.PeekTestCase):

    def setUp(self):
        # Construct and initialize system environment
        self.env = self.construct_env(DaxExampleSystem)
        self.env.dax_init()

    def test_detect(self, duration=200 * us):
        for i, pmt in enumerate(self.env.detection._pmt_counter):
            # Set standard deviation to zero for easier testing
            self.push(pmt, 'input_stdev', 0.0)

            for input_freq in 0 * Hz, 100 * kHz:
                # Set input frequency, represents the PMT signal
                self.push(pmt, 'input_freq', input_freq)

                # Perform detection
                with parallel:
                    self.env.detection.detect_channels([i], duration, detection_beam=True)
                    self.expect(self.env.detection._detection_sw, 'state', True, 'Detection beam not switched on')
                self.expect(self.env.detection._detection_sw, 'state', False, 'Detection beam not switched off')

                # Get count and verify result
                count = self.env.detection.count(i)
                self.assertAlmostEqual(count, input_freq * duration, delta=1)
