import pyuvm
from pyuvm import uvm_factory

from sat_tb_base_seq import sat_tb_base_seq
from vseqs.sat_tb_random_seq import sat_tb_random_seq

@pyuvm.test()
class sat_tb_random_test(sat_tb_base_seq):
    
    def __init__(self, name="sat_tb_default_test", parent=None):
        super().__init__(name, parent)

    def start_of_simulation_phase(self):
        super().start_of_simulation_phase()
        # Create a factory type override that globally replaces the base
        # virtual sequence with the default virtual sequence.
        uvm_factory().set_type_override_by_type(
            original_type=sat_tb_base_seq,
            override_type=sat_tb_random_seq,
        )

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()
        # Start the virtual sequence on the virtual sequencer
        for _ in range(10):
            await self.virtual_sequence.start(seqr=self.tb_env.virtual_sequencer)
        self.drop_objection()
