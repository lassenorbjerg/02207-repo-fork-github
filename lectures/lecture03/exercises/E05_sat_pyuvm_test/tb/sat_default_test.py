#
# Simple PyUVM test.
#

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly
import pyuvm
from pyuvm import uvm_test
DATA_W = 8
THRESHOLD = 64

async def transaction(dut, data):

    dut.in_data.value = data
    dut.in_valid.value = 1

    await RisingEdge(dut.clk)
    await ReadOnly()

    while dut.out_valid.value != 1:
        await RisingEdge(dut.clk)
        await ReadOnly()

    assert dut.out_valid.value == 1
    assert dut.out_data.value == data if data < THRESHOLD else THRESHOLD

    await RisingEdge(dut.clk)

    dut.in_data.value = 0
    dut.in_valid.value = 0

    await RisingEdge(dut.clk)


@pyuvm.test()
class sat_default_test(uvm_test):
    def build_phase(self):
        super().build_phase()

        self.dut = cocotb.top

    def connect_phase(self): ...

    async def run_phase(self):
        self.raise_objection()

        dut = self.dut

        Clock(signal=dut.clk, period=2, unit="ns").start()

        dut.rst.value = 1
        dut.in_valid.value = 0
        dut.in_data.value = 0

        await RisingEdge(dut.clk)

        dut.rst.value = 0

        await RisingEdge(dut.clk)

        await transaction(dut, THRESHOLD - 5)

        await transaction(dut, THRESHOLD + 5)

        self.drop_objection()
