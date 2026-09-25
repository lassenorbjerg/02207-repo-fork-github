from cocotb.triggers import ClockCycles, ReadOnly, RisingEdge
from pyuvm import uvm_root, uvm_sequence



DATA_W = 8
THRESHOLD = 64


class sat_tb_default_seq(uvm_sequence):
    def __init__(self, name="sat_tb_default_seq"):  # NOTE: Changed default name
        super().__init__(name)
        self.sequencer = None
        self.cfg = None

    async def pre_body(self):  # NOTE: This is supposed to be async right? TAG
        await super().pre_body()

        self.cfg = self.sequencer.cfg
        # NOTE: Video defines self.input_if = self.cfg.input_if. We define a variable in _transaction_helper that achieves the same thing

    async def _transaction_helper(self, data):
        cfg  = self.cfg
        clk = cfg.input_if.clk
        
        await RisingEdge(clk)  # NOTE: video waits before as well

        # NOTE: BUGFOUND: NOTE: if is a postfix. NOT a prefix. if_input before
        cfg.input_if.data.value = data
        cfg.input_if.valid.value = 1

        await RisingEdge(clk)
        await ReadOnly()

        while cfg.output_if.valid.value != 1:
            await RisingEdge(clk)
            await ReadOnly()

        assert cfg.output_if.valid.value == 1
        assert cfg.output_if.data.value == data if data < THRESHOLD else THRESHOLD

        await RisingEdge(clk)

        cfg.input_if.data.value = 0
        cfg.input_if.valid.value = 0

        await RisingEdge(clk)


    async def body(self):
        await super().body()

        await self._transaction_helper(THRESHOLD - 5)
        await self._transaction_helper(THRESHOLD + 5)
