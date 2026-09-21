""" Saturation Filter Environment UVM component. """

from pyuvm import ConfigDB, uvm_env

from lectures.lecture04.exercises.E06_sat_pyuvm_env_vseq.tb.sat_tb_virt_sequencer import sat_tb_virt_sequencer

class sat_tb_env(uvm_env):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.cfg = None
        self.virtual_sequencer = None

    def build_phase(self):
        super().build_phase()

        self.virtual_sequencer = sat_tb_virt_sequencer.create(name="virtual_sequencer", parent=self)





