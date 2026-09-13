#
# Simple PyUVM test using interface wrappers.
#

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, ReadOnly, RisingEdge
import pyuvm
from pyuvm import uvm_test


class ssdt_interface_wrapper():
    def __init__(self, clk=None, rst=None, name="ssdt_interface"):
        self.name = name
        self.clk = clk
        self.rst = rst
        self.valid = None
        self.data = None

    def connect(self, clk_signal, reset_signal, valid_signal, data_signal):
        self.clk = clk_signal
        self.rst = reset_signal
        self.valid = valid_signal
        self.data = data_signal

