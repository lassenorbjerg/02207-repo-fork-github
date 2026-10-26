""" Summer Scoreboard
- Verification component that contains checkers and verifies the functionality of the design.
- Receives transaction level objects captured from the interfaces of a DUT via TLM Analysis Ports.
- Includes the Reference Model.
"""

from pyuvm import uvm_scoreboard, uvm_tlm_analysis_fifo


class summer_tb_scoreboard(uvm_scoreboard):
    """ Scoreboard for Summer. """

    def __init__(self, name="summer_tb_scoreboard", parent=None):

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

            # Get items from queues
            self.uvc_ssdt_consumer_item = await self.uvc_ssdt_consumer_fifo.get()
            self.ref_model_item = await self.ref_model_fifo.get()

            # Log items as they arrive (only in DEBUG level)
            self.log_items(self.uvc_ssdt_consumer_item, self.ref_model_item)

            # compare items and update result
            if (self.uvc_ssdt_consumer_item == self.ref_model_item):
                self.succes += 1
                self.logger.info(f"Items are identical: {self.uvc_ssdt_consumer_item}")
            else:
                self.logger.error(f"Items not identical: \n \
                    {self.uvc_ssdt_consumer_item}, \n \
                    {self.ref_model_item}")
                self.failure += 1

    # Report the results of the comparisons
    def check_phase(self):
        super().check_phase()

        self.logger.info(f"Scoreboard found {self.succes} successes and {self.failure} failures")
        assert self.failure == 0, f"the test found {self.failure} failed comparisons"

    def log_items(self, consumer_item, ref_model_item):
        """Print scoreboard items."""
        separator = "-" * 35

        self.logger.debug(separator)
        self.logger.debug(" | consumer_item | ref_model_item |")
        self.logger.debug(f" |   {consumer_item.data:4d}   |   {ref_model_item.data:4d}")
        self.logger.debug(separator)
        self.logger.debug(f" | {consumer_item}  |\n | {ref_model_item}  |")
        self.logger.debug(separator)
