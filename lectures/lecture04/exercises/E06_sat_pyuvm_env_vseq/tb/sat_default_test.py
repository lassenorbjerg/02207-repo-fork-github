#
# Simple PyUVM test using interface wrappers.
#

import cocotb
import pyuvm
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from pyuvm import ConfigDB, uvm_test

from sat_tb_config import sat_tb_config
from sat_tb_defaut_seq import sat_tb_default_seq
from sat_tb_env import sat_tb_env



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


DATA_W = 8
THRESHOLD = 64

async def transaction(dut, data):

    dut.in_.data.value = data
    dut.in_.valid.value = 1

    await RisingEdge(dut.clk)
    await ReadOnly()

    while dut.out_.valid.value != 1:
        await RisingEdge(dut.clk)
        await ReadOnly()

    assert dut.out_.valid.value == 1
    assert dut.out_.data.value == data if data < THRESHOLD else THRESHOLD

    await RisingEdge(dut.clk)

    dut.in_.data.value = 0
    dut.in_.valid.value = 0

    await RisingEdge(dut.clk)


@pyuvm.test()
class sat_interface_test(uvm_test):
    def build_phase(self):
        super().build_phase()
        dut = cocotb.top
        self.dut = dut
        self.clk = dut.clk
        self.env = sat_tb_env.create("env", parent=self)

    def connect_phase(self):
        dut=self.dut
        self.in_ = ssdt_interface_wrapper()
        self.in_.connect(
            clk_signal=dut.clk,
            reset_signal=dut.rst,
            valid_signal=dut.in_valid,
            data_signal=dut.in_data,
        )
        self.out_ = ssdt_interface_wrapper()
        self.out_.connect(
            clk_signal=dut.clk,
            reset_signal=dut.rst,
            valid_signal=dut.out_valid,
            data_signal=dut.out_data,
        )

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()

        dut_in: ssdt_interface_wrapper = self.in_
        dut_out: ssdt_interface_wrapper = self.out_

        Clock(signal=dut_in.clk, period=2, unit="ns").start()

        dut_in.rst.value = 1
        dut_in.valid.value = 0
        dut_in.data.value = 0

        await RisingEdge(dut_in.clk)

        dut_in.rst.value = 0

        await RisingEdge(dut_in.clk)

        self.drop_objection()

