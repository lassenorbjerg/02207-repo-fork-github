""" Saturation Filter Environment UVM component. """

from pyuvm import ConfigDB, uvm_env

from sat_tb_virt_sequencer import sat_tb_virt_sequencer

class sat_tb_env(uvm_env):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.cfg = None
        self.virtual_sequencer: sat_tb_virt_sequencer | None = None

    def build_phase(self):
        super().build_phase()

        self.virtual_sequencer = sat_tb_virt_sequencer.create(name="virtual_sequencer", parent=self)
        self.cfg = ConfigDB().get(self, "", "cfg")
        ConfigDB().set(self, "sat_tb_virt_sequencer", "cfg", self.cfg)





