import pyuvm
from pyuvm import uvm_factory

from sat_tb_base_seq import sat_tb_base_seq
from sat_tb_base_test import sat_tb_base_test
from sat_tb_histogram import render_histogram
from vseqs.sat_tb_less_than_threshold_seq import sat_tb_less_than_threshold_seq


@pyuvm.test()
class sat_tb_less_than_threshold_test(sat_tb_base_test):

    def __init__(self, name="sat_tb_less_than_threshold_test", parent=None):
        super().__init__(name, parent)

    def start_of_simulation_phase(self):
        super().start_of_simulation_phase()
        uvm_factory().set_type_override_by_type(
            original_type=sat_tb_base_seq,
            override_type=sat_tb_less_than_threshold_seq,
        )

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()
        # Start the virtual sequence on the virtual sequencer
        await self.virtual_sequence.start(seqr=self.tb_env.virtual_sequencer)
        render_histogram(self.virtual_sequence.producer_responses, "sat_tb_less_than_threshold_test_histogram.pdf")
        self.drop_objection()
