""" Saturation Filter virtual Sequencer.
"""

from pyuvm import ConfigDB, uvm_sequencer

class sat_tb_virt_sequencer(uvm_sequencer):
    def __init__(self, name="sat_tb_virt_sequencer", parent=None):
        super().__init__(name, parent)
        self.cfg = None

        self.ssdt_producer_sequencer = None
        self.ssdt_consumer_sequencer = None

    def build_phase(self):
        super().build_phase()

        self.cfg = ConfigDB().get(self, "", "cfg")

