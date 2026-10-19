""" Saturation Filter virtual Sequencer.
"""

from pyuvm import ConfigDB, uvm_sequencer


class sat_tb_virt_sequencer(uvm_sequencer):
    """ Virtual sequencer component for Saturation Filter TB. """

    def __init__(self, name="sat_filter_tb_virt_sequencer", parent=None):

        super().__init__(name, parent)

        self.cfg = None     # Empty handle for the configuration object

        self.ssdt_producer_sequencer = None
        self.ssdt_consumer_sequencer = None

    def build_phase(self):
        self.logger.debug("Start build_phase() -> SAT virtual sequencer")

        super().build_phase()

        # Get the configuration object sent to this sequencer through ConfigDB.
        self.cfg = ConfigDB().get(
            context     = self,
            inst_name   = "",
            field_name  = "cfg",
        )
        self.logger.debug("End build_phase() -> SAT virtual sequencer")
