""" Saturation Filter virtual Sequencer.
"""

from pyuvm import ConfigDB, uvm_sequencer


class sat_tb_virt_sequencer(uvm_sequencer):
    def __init__(self, name="sat_virtual_seqer", parent=None):
        super().__init__(name, parent)
        self.cfg = None
        self.virtual_sequencer = None


    def build_phase(self):
        super().build_phase()

        self.virtual_sequencer = vseqr

