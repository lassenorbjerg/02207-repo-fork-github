from cocotb.triggers import ClockCycles, ReadOnly, RisingEdge
from pyuvm import uvm_root, uvm_sequence



DATA_W = 8
THRESHOLD = 64


class sat_tb_default_seq(uvm_sequence):
    def __init__(self, name="uvm_sequence"):
        super().__init__(name)
        self.sequencer = None
        self.cfg = None

    async def pre_body(self):
        await super().pre_body()

        self.cfg = self.sequencer.cfg

    async def _transaction_helper(self, data):
        cfg  = self.cfg
        
        cfg.if_input.data.value = data
        cfg.if_input.valid.value = 1

        await RisingEdge(cfg.clk)
        await ReadOnly()

        while cfg.if_output.valid.value != 1:
            await RisingEdge(cfg.clk)
            await ReadOnly()

        assert cfg.if_output.valid.value == 1
        assert cfg.if_output.data.value == data if data < THRESHOLD else THRESHOLD

        await RisingEdge(cfg.clk)

        cfg.if_input.data.value = 0
        cfg.if_input.valid.value = 0

        await RisingEdge(cfg.clk)


    async def body(self):
        await super().body()

        await self._transaction_helper(THRESHOLD - 5)
        await self._transaction_helper(THRESHOLD + 5)
