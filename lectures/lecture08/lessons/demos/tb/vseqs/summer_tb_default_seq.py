import cocotb
from cocotb.triggers import Combine
from pyuvm import uvm_sequence

from summer_tb_base_seq import summer_tb_base_seq
from uvc.ssdt import uvc_ssdt_basic_seq, uvc_ssdt_seq_item


class summer_tb_default_seq(summer_tb_base_seq):
    """ Default sequence for the Summer's TB.
    Drive two transactions though the SUMMER.
    """

    def __init__(self, name="summer_tb_default_seq"):
        super().__init__(name)
        # Create reusable producer and consumer UVC sequences using the factory.
        self.producer_seq = uvc_ssdt_basic_seq.create("summer_ssdt_prod_seq")
        self.consumer_seq = uvc_ssdt_basic_seq.create("summer_ssdt_cons_seq")

    async def body(self):
        await super().body()

        # Create the first input transaction and assign it to the producer
        # sequence.
        seq_item = uvc_ssdt_seq_item.create("producer_item")
        seq_item.data = 46
        self.producer_seq.seq_item = seq_item

        # Start both UVC sequences concurrently on their agent sequencers.
        prod_task = cocotb.start_soon(self.producer_seq.start(self.sequencer.ssdt_producer_sequencer))
        cons_task = cocotb.start_soon(self.consumer_seq.start(self.sequencer.ssdt_consumer_sequencer))

        # Wait for both UVC sequences to finish.
        await Combine(prod_task, cons_task)
        self.sequencer.logger.info(
            f"Input transaction data: {self.producer_seq.rsp.data}",
        )
        self.sequencer.logger.info(
            f"Output transaction data: {self.consumer_seq.rsp.data}",
        )

        # Reuse the sequences with a second input transaction.
        seq_item = uvc_ssdt_seq_item.create("producer_item")
        seq_item.data = 100
        self.producer_seq.seq_item = seq_item

        # Start both UVC sequences concurrently on their agent sequencers.
        prod_task = cocotb.start_soon(self.producer_seq.start(self.sequencer.ssdt_producer_sequencer))
        cons_task = cocotb.start_soon(self.consumer_seq.start(self.sequencer.ssdt_consumer_sequencer))

        # Wait for both UVC sequences to finish.
        await Combine(prod_task, cons_task)
        self.sequencer.logger.info(
            f"Input transaction data: {self.producer_seq.rsp.data}",
        )
        self.sequencer.logger.info(
            f"Output transaction data: {self.consumer_seq.rsp.data}",
        )
