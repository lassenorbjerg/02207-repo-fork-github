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
from typing import TypeVar

configT =TypeVar(name="configT", bound=sat_tb_config)


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


@pyuvm.test()
class sat_default_test(uvm_test):
    def build_phase(self):
        super().build_phase()
        dut = cocotb.top
        self.dut = dut
        self.clk = dut.clk
        self.env: sat_tb_env = sat_tb_env.create("env", parent=self)
        self.config: sat_tb_config = sat_tb_config.create(name="config") # type: ignore
        self.config.input_if = ssdt_interface_wrapper(name="input_if")
        self.config.output_if = ssdt_interface_wrapper(name="output_if")
        ConfigDB().set(self, "env", "cfg", self.config)

    def connect_phase(self):
        dut=self.dut
        self.input_if.connect(
            clk_signal=dut.clk,
            reset_signal=dut.rst,
            valid_signal=dut.in_valid,
            data_signal=dut.in_data,
        )
        self.output_if.connect(
            clk_signal=dut.clk,
            reset_signal=dut.rst,
            valid_signal=dut.out_valid,
            data_signal=dut.out_data,
        )

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()

        dut_in: ssdt_interface_wrapper = self.input_if
        dut_out: ssdt_interface_wrapper = self.output_if

        Clock(signal=dut_in.clk, period=2, unit="ns").start()

        dut_in.rst.value = 1
        dut_in.valid.value = 0
        dut_in.data.value = 0

        await RisingEdge(dut_in.clk)

        dut_in.rst.value = 0

        await RisingEdge(dut_in.clk)

        seq = sat_tb_default_seq()
        await seq.start(seqr=self.env.virtual_sequencer)

        self.drop_objection()

