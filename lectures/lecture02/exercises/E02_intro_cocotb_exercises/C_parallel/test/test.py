#__RELEASE_REMOVE_TOTAL__
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge


@cocotb.test()
async def mux_basic_test(dut):

    Clock(signal=dut.clk,period=2,unit='ns').start()

    await RisingEdge(dut.clk)

    A = 5
    B = 1
    C = 5

    dut.A.value = A
    dut.B.value = B
    dut.C.value = C

    await RisingEdge(dut.clk)

    A = 3
    B = 4
    C = 5

    dut.A.value = A
    dut.B.value = B
    dut.C.value = C

    await RisingEdge(dut.clk)


@cocotb.test()
async def mux_randomized_test(dut):

    Clock(signal=dut.clk,period=2,unit='ns').start()

    for _ in range(20):
        await RisingEdge(dut.clk)
        A = random.randint(0, 7)
        B = random.randint(0, 7)
        C = random.randint(0, 7)

        dut.A.value = A
        dut.B.value = B
        dut.C.value = C
