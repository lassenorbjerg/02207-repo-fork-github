import cocotb
from cocotb.triggers import Combine

from summer_tb_base_seq import summer_tb_base_seq
from uvc.ssdt import uvc_ssdt_basic_seq, uvc_ssdt_seq_item


class summer_tb_random_seq(summer_tb_base_seq):
    """Virtual sequence with random producer data"""

    def __init__(self, name="summer_tb_random_seq"):

        super().__init__(name)

        self.producer_seq = uvc_ssdt_basic_seq.create("summer_ssdt_prod_seq")
        self.consumer_seq = uvc_ssdt_basic_seq.create("summer_ssdt_cons_seq")
        self.producer_responses = []

    async def body(self):

        await super().body()

        for _ in range(10):
            seq_item = uvc_ssdt_seq_item.create("producer_item")
            seq_item.randomize()
            self.producer_seq.seq_item = seq_item

            prod_task = cocotb.start_soon(
                self.producer_seq.start(self.sequencer.ssdt_producer_sequencer),
            )
            cons_task = cocotb.start_soon(
                self.consumer_seq.start(self.sequencer.ssdt_consumer_sequencer),
            )
            await Combine(prod_task, cons_task)
            self.sequencer.logger.info(
                f"Input transaction data: {self.producer_seq.rsp.data}",
            )
            self.sequencer.logger.info(
                f"Output transaction data: {self.consumer_seq.rsp.data}",
            )
            self.producer_responses.append(int(self.producer_seq.rsp.data))
