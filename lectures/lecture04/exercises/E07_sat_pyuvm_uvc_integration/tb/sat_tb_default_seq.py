import cocotb
from cocotb.triggers import Combine
from pyuvm import uvm_root, uvm_sequence

from uvc.ssdt import uvc_ssdt_basic_seq, uvc_ssdt_seq_item


from cocotb.triggers import ClockCycles, ReadOnly, RisingEdge
from pyuvm import uvm_root, uvm_sequence



DATA_W = 8
THRESHOLD = 64


class sat_tb_default_seq(uvm_sequence):
    def __init__(self, name="sat_tb_default_seq"):  # NOTE: Changed default name
        super().__init__(name)
        self.sequencer = None
        self.cfg = None

        # NOTE: Unsure
        self.producer_seq = None
        self.consumer_seq = None

    async def pre_body(self):
        await super().pre_body()

        self.cfg = self.sequencer.cfg

        # NOTE: Unsure
        self.producer_seq = uvc_ssdt_basic_seq.create(name="producer_seq")
        self.consumer_seq = uvc_ssdt_basic_seq.create(name="consumer_seq")

    async def _transaction_helper(self, data):

        seq_item = uvc_ssdt_seq_item.create("producer_item")
        seq_item.data = data
        self.producer_seq.seq_item = seq_item

        # NOTE: Unsure if should be here or another place
        prod_task = cocotb.start_soon(
            self.producer_seq.start(
                seqr=self.sequencer.ssdt_producer_sequencer))
        cons_task = cocotb.start_soon(
            self.consumer_seq.start(
                seqr=self.sequencer.ssdt_consumer_sequencer))
        # Finishes when the both tasks finishes
        await Combine(prod_task, cons_task)



    async def body(self):
        await super().body()

        await self._transaction_helper(THRESHOLD - 5)
        await self._transaction_helper(THRESHOLD + 5)
