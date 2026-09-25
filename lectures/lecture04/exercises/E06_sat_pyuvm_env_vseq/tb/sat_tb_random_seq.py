import random

from cocotb.triggers import ClockCycles, ReadOnly, RisingEdge
from sat_tb_defaut_seq import sat_tb_default_seq, THRESHOLD

class sat_tb_random_seq(sat_tb_default_seq):
    def __init__(self, name="sat_tb_random_seq"):
        super().__init__(name)

    async def body(self):
        for _ in range(10):
            await self._transaction_helper(random.randint(0,THRESHOLD*2))

