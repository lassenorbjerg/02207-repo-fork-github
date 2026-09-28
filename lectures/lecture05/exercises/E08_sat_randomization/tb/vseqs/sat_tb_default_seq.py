import cocotb
from cocotb.triggers import Combine
from pyuvm import uvm_sequence

from uvc.ssdt import uvc_ssdt_basic_seq, uvc_ssdt_seq_item


class sat_tb_default_seq(uvm_sequence):
    """ Default sequence for the Saturation Filter's TB.
    Drive two transactions though the SAT.
    """

    def __init__(self, name="sat_tb_default_seq"):
        super().__init__(name)
        # Create reusable producer and consumer UVC sequences using the factory.
        self.producer_seq = uvc_ssdt_basic_seq.create("sat_ssdt_prod_seq")
        self.consumer_seq = uvc_ssdt_basic_seq.create("sat_ssdt_cons_seq")

    async def body(self):
        await super().body()

        # Create a non-saturating transaction and assign it to the producer
        # sequence.
        seq_item = uvc_ssdt_seq_item.create("producer_item")
        seq_item.data = 46
        self.producer_seq.seq_item = seq_item


        # Start both UVC sequences concurrently on their agent sequencers.
        prod_task = cocotb.start_soon(self.producer_seq.start(self.sequencer.ssdt_producer_sequencer))
        cons_task = cocotb.start_soon(self.consumer_seq.start(self.sequencer.ssdt_consumer_sequencer))

        # Wait for both UVC sequences to finish.
        await Combine(prod_task, cons_task)

        # Reuse the sequences with a new saturating transaction.
        seq_item = uvc_ssdt_seq_item.create("producer_item")
        seq_item.data = 100
        self.producer_seq.seq_item = seq_item


        # Start both UVC sequences concurrently on their agent sequencers.
        prod_task = cocotb.start_soon(self.producer_seq.start(self.sequencer.ssdt_producer_sequencer))
        cons_task = cocotb.start_soon(self.consumer_seq.start(self.sequencer.ssdt_consumer_sequencer))

        # Wait for both UVC sequences to finish.
        await Combine(prod_task, cons_task)
