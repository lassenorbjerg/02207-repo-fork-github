#
# Simple cocotb test.
#

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly

DATA_W = 8
THRESHOLD = 64

async def transaction(dut, data):

    dut.in_data.value = data
    dut.in_valid.value = 1

    await RisingEdge(dut.clk)

    assert dut.out_valid.value == 1
    assert dut.out_data.value == data if data < THRESHOLD else THRESHOLD

    dut.in_data.value = 0
    dut.in_valid.value = 0

    await RisingEdge(dut.clk)


@cocotb.test()
async def simple_test(dut):
    Clock(signal=dut.clk, period=2, unit="ns").start()

    dut.rst.value = 1
    dut.in_valid.value = 0
    dut.in_data.value = 0

    await RisingEdge(dut.clk)

    dut.rst.value = 0

    await RisingEdge(dut.clk)

    await transaction(dut, THRESHOLD - 5)

    await transaction(dut, THRESHOLD + 5)

