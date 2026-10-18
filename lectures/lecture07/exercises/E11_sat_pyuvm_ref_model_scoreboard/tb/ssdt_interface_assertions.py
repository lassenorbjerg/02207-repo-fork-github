""" SSDT interface asserations wrapper"""

import cocotb
from cocotb.triggers import ReadOnly, RisingEdge
from cocotb.types import LogicArray


class ssdt_interface_assert_check:

    def __init__(self, clk_signal = None, rst_signal = None, valid_signal = None, data_signal = None, name = "ssdt_interface_assert_check"):

        self.name  = name

        self.clk   = clk_signal
        self.rst   = rst_signal

        self.valid = valid_signal
        self.data  = data_signal

        # Set as false if any assertion fail
        self.passed = True


    def check_assertions(self):
        cocotb.start_soon(self.reset_values())
        cocotb.start_soon(self.data_value())
        cocotb.start_soon(self.stable_data())

    # Reset requirement (PR 1):
    # If RST = 1, then VALID cannot be 1
    # NOTE: Check is sync to the clock
    async def reset_values(self):
        while True:
            await RisingEdge(self.clk)
            await ReadOnly()

            try:
                if int(self.rst.value) == 1:
                    assert int(self.valid.value) != 1, \
                        f"When reset, valid was {self.valid.value}"
            except AssertionError as msg:
                self.passed = False
                print(msg)

    # Data valitidy requirement (PR 2):
    # NOTE: Check is sync to the clock
    # If VALID = 1, then DATA cannot be X
    async def data_value(self):
        while True:
            await RisingEdge(self.clk)
            await ReadOnly()
            try:
                if (self.valid.value) == 1:
                    # .is_resolvable is True if all elements of the array are
                    # 0,1,L or H
                    # See https://docs.cocotb.org/en/v2.0.1/library_reference.html#cocotb.types.LogicArray.is_resolvable
                    assert self.data.value.is_resolvable , \
                        f"When valid, data was {self.data.value}"
            except AssertionError as msg:
                self.passed = False
                print(msg)

    # Data invalidity requirement (PR 3):
    # NOTE: Check is sync to the clock
    # If VALID = 0, then DATA must be 0
    async def stable_data(self):
        while True:
            await RisingEdge(self.clk)
            await ReadOnly()

            try:
                if self.valid.value == 0:
                    assert self.data.value == LogicArray('0' * len(self.data)), \
                        f"When not valid, data was {self.data.value}"
            except AssertionError as msg:
                self.passed = False
                print(msg)
