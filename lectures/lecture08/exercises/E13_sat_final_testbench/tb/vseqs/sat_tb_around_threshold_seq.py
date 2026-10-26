import cocotb
from cocotb.triggers import Combine

from sat_tb_base_seq import sat_tb_base_seq
from uvc.ssdt import uvc_ssdt_basic_seq, uvc_ssdt_seq_item


class sat_tb_around_threshold_seq(sat_tb_base_seq):
    """Virtual sequence with producer data within threshold window."""

    def __init__(self, name="sat_tb_around_threshold_seq"):

        super().__init__(name)

        self.producer_seq = uvc_ssdt_basic_seq.create("sat_filter_ssdt_prod_seq")
        self.consumer_seq = uvc_ssdt_basic_seq.create("sat_filter_ssdt_cons_seq")
        self.producer_responses = []

    async def body(self):

        await super().body()

        for _ in range(10):
            seq_item = uvc_ssdt_seq_item.create("producer_item")

            with seq_item.randomize_with() as item:
                item.data >= 64 - 10
                item.data <= 64 + 10

            self.producer_seq.seq_item = seq_item

            prod_task = cocotb.start_soon(
                self.producer_seq.start(self.sequencer.ssdt_producer_sequencer),
            )
            cons_task = cocotb.start_soon(
                self.consumer_seq.start(self.sequencer.ssdt_consumer_sequencer),
            )
            await Combine(prod_task, cons_task)
            self.producer_responses.append(int(self.producer_seq.rsp.data))
