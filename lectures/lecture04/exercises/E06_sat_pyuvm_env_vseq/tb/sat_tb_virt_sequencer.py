"""Saturation Filter virtual Sequencer."""

from pyuvm import ConfigDB, uvm_sequencer


class sat_tb_virtual_sequencer(uvm_sequencer):  # NOTE: Changed class name
    def __init__(self, name="sat_tb_virtual_sequencer", parent=None):  # NOTE: Changed default name
        super().__init__(name, parent)
        self.cfg = None

    def build_phase(self):
        super().build_phase()

        self.cfg = ConfigDB().get(self, "", "cfg")
