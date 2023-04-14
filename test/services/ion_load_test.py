import dax.sim.test_case

from repository.services.ion_load import IonLoadExperiment


class IonLoadTestCase(dax.sim.test_case.PeekTestCase):

    def test_load_ions(self):
        for n in [1, 2, 3, 4]:
            # Construct a complete experiment and pass arguments
            env = self.construct_env(IonLoadExperiment, env_kwargs={'Number of ions': n})

            # Run the experiment
            env.prepare()
            env.run()

            # Test state of system datasets
            self.assertEqual(env.trap.num_ions(), n)
            self.assertEqual(len(env.detection.active_channels()), n)
