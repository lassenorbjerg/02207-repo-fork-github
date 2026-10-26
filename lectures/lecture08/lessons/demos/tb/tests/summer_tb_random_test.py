import pyuvm
from pyuvm import uvm_factory

from summer_tb_base_seq import summer_tb_base_seq
from summer_tb_base_test import summer_tb_base_test
from vseqs.summer_tb_random_seq import summer_tb_random_seq


@pyuvm.test()
class summer_tb_random_test(summer_tb_base_test):

    def __init__(self, name="summer_tb_random_test", parent=None):
        super().__init__(name, parent)

    def start_of_simulation_phase(self):
        super().start_of_simulation_phase()
        uvm_factory().set_type_override_by_type(
            original_type=summer_tb_base_seq,
            override_type=summer_tb_random_seq,
        )

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()
        # Start the virtual sequence on the virtual sequencer
        await self.virtual_sequence.start(seqr=self.tb_env.virtual_sequencer)
        self.drop_objection()
