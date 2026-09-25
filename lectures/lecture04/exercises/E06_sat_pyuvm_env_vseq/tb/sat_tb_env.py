"""Saturation Filter Environment UVM component."""

from pyuvm import ConfigDB, uvm_env

from sat_tb_virt_sequencer import sat_tb_virtual_sequencer


class sat_tb_env(uvm_env):
    def __init__(self, name="sat_tb_env", parent=None):  # NOTE: Added default values
        super().__init__(name, parent)
        self.cfg = None
        self.virtual_sequencer = None

    def build_phase(self):
        super().build_phase()

        self.virtual_sequencer = sat_tb_virtual_sequencer.create(
            name="virtual_sequencer", parent=self
        )

        self.cfg = ConfigDB().get(
            context=self,
            inst_name="",
            field_name="cfg",
        )
        ConfigDB().set(
            context=self,
            inst_name="virtual_sequencer",  # NOTE: BUGFOUND: NOTE: This was "sat_tb_virt_sequencer" in segfault
            field_name="cfg",
            value=self.cfg,
        )
