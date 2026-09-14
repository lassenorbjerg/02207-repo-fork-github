#
# Simple PyUVM test.
#

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly
import pyuvm
from pyuvm import uvm_test

@pyuvm.test()
class sat_default_test(uvm_test):

    async def build_phase(dut):
        ...

    async def connect_phase()
