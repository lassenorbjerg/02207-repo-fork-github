#
# Simple PyUVM test.
#

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, ReadOnly
import pyuvm
from pyuvm import uvm_test

