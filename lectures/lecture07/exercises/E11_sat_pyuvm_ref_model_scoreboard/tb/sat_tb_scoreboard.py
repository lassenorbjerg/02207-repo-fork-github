""" Saturation Filter Scoreboard
- Verification component that contains checkers and verifies the functionality of the design.
- Receives transaction level objects captured from the interfaces of a DUT via TLM Analysis Ports.
- Includes the Reference Model.
"""

from pyuvm import uvm_scoreboard, uvm_tlm_analysis_fifo


class sat_tb_scoreboard(uvm_scoreboard):
    """ Scoreboard for Saturation Filter. """

    def __init__(self, name="sat_filter_scoreboard", parent=None):

        super().__init__(name, parent)

        # FIFO for connecting to UVC's ap
        self.uvc_ssdt_consumer_fifo = uvm_tlm_analysis_fifo(
            name   = "uvc_ssdt_consumer_fifo",
            parent = self,
        )
        self.ref_model_fifo = uvm_tlm_analysis_fifo(
            name = "ref_model_fifo",
            parent = self,
        )

        # recording number of successes and failures
        self.succes = 0
        self.failure = 0

    async def run_phase(self):
        """
        - Get the item from the FIFOs
        - Compare the samples received
        """

        await super().run_phase()

        while True:
            con_item = await self.uvc_ssdt_consumer_fifo.get()
            ref_item = await self.ref_model_fifo.get()
            if con_item.data == ref_item.data:
                self.succes += 1
            else:
                self.failure += 1
                self.logger.debug("Failure")
                self.log_items(con_item, ref_item)


    # Report the results of the comparisons
    def check_phase(self):
        super().check_phase()
        self.logger.debug(f"{(self.succes,self.failure)}")
        assert self.failure == 0


    def log_items(self, consumer_item, ref_model_item):
        """Print scoreboard items."""
        separator = "-" * 35

        self.logger.debug(separator)
        self.logger.debug(" | consumer_item | ref_model_item |")
        self.logger.debug(f" |   {consumer_item.data:4d}   |   {ref_model_item.data:4d}")
        self.logger.debug(separator)
        self.logger.debug(f" | {consumer_item}  |\n | {ref_model_item}  |")
        self.logger.debug(separator)

