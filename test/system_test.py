import dax.sim.test_case

from dax_example.system import DaxExampleSystem


class SystemTestCase(dax.sim.test_case.PeekTestCase):

    def test_kernel_invariants(self):
        # Construct and initialize system environment
        env = self.construct_env(DaxExampleSystem)
        env.dax_init()

        # Test modules
        for m in env.registry.get_module_list():
            self._test_kernel_invariants(m)
        # Test services
        for s in env.registry.get_service_list():
            self._test_kernel_invariants(s)

    def _test_kernel_invariants(self, component):
        # Test kernel invariants of this component
        for k in component.kernel_invariants:
            self.assertTrue(hasattr(component, k), f'Name "{k:s}" of "{component.get_system_key():s}" was marked '
                                                   f'kernel invariant, but this attribute does not exist')

    def test_dax_init(self):
        # Construct and initialize system environment
        env = self.construct_env(DaxExampleSystem)
        env.dax_init()

        # Trap module
        self.assertIs(env.trap._cool_sw, env.trap._cool_dds.sw)
        self.expect(env.trap._cool_sw, 'state', env.trap._cool_init_state)
        self.expect(env.trap._cool_dds, 'freq', env.trap._cool_freq)

        # Detection module
        self.assertIs(env.detection._detection_sw, env.detection._detection_dds.sw)
        self.expect(env.detection._detection_sw, 'state', False)
        self.expect(env.detection._detection_dds, 'freq', env.detection._detection_freq)
        for pmt in env.detection._pmt_ttl:
            self.expect(pmt, 'direction', 0)  # Check if the direction is set to input

        # LED module
        for led in env.led.led:
            self.expect(led, 'state', 0)

        # CPLD module
        for cpld in env.cpld.cpld:
            self.expect(cpld, 'init_att', True)  # Check if ``get_att_mu()`` was called
