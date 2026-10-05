import cocotb
import vsc
from cocotb.triggers import Combine

from sat_tb_base_seq import sat_tb_base_seq
from uvc.ssdt import uvc_ssdt_default_seq, uvc_ssdt_seq_item


@vsc.randobj
class sat_tb_rand_n_seq(sat_tb_base_seq):
    """ Launch a random number of sequences on each agent. """

    def __init__(self, name="ssdt_b2b_rand_n_seq"):

        super().__init__(name)

        # Create sequences
        self.producer_seq = uvc_ssdt_default_seq.create("sat_filter_ssdt_prod_seq")
        self.consumer_seq = uvc_ssdt_default_seq.create("sat_filter_ssdt_cons_seq")
        self.producer_responses = []

        self.number_of_seqs = vsc.rand_uint32_t()

    @vsc.constraint
    def number_of_seqs_pos_max(self):
        self.number_of_seqs > 0
        self.number_of_seqs <= 100  # noqa: PLR2004

    async def body(self):

        # Launch sequences
        await super().body()

        self.sequencer.logger.info(f"Launching {self.number_of_seqs} sequences.")

        prod_task = cocotb.start_soon(self.prod_transactions())
        cons_task = cocotb.start_soon(self.cons_transactions())

        # Finishes when all tasks finishes
        await Combine(prod_task, cons_task)

    async def prod_transactions(self):

        for _ in range(self.number_of_seqs):
            seq_item = uvc_ssdt_seq_item.create(name="producer_item")
            seq_item.randomize()
            self.producer_seq.seq_item = seq_item
            await self.producer_seq.start(self.sequencer.ssdt_producer_sequencer)
            self.producer_responses.append(int(self.producer_seq.rsp.data))

    async def cons_transactions(self):

        for _ in range(self.number_of_seqs):
            await self.consumer_seq.start(self.sequencer.ssdt_consumer_sequencer)
