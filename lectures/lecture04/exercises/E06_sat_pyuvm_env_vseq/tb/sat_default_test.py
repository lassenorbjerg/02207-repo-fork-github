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
from ssdt_interface import ssdt_interface_wrapper  # NOTE: Import instead of defined here


@pyuvm.test()
class sat_default_test(uvm_test):
    def build_phase(self):
        super().build_phase()
        self.dut = cocotb.top
        self.input_if = ssdt_interface_wrapper(name="input_if")
        self.output_if = ssdt_interface_wrapper(name="output_if")

        self.cfg = sat_tb_config.create(name="cfg")  # type: ignore
        self.cfg.input_if = self.input_if
        self.cfg.output_if = self.output_if

        self.sat_tb_env = sat_tb_env.create(name="sat_tb_env", parent=self)

        ConfigDB().set(
            context=self,
            inst_name="sat_tb_env",
            field_name="cfg",
            value=self.cfg,
        )

    def connect_phase(self):
        dut = self.dut
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

        clock = Clock(signal=dut_in.clk, period=2, unit="ns")
        cocotb.start_soon(clock.start())  # NOTE: clock was started immediately in segfault

        dut_in.rst.value = 1
        dut_in.valid.value = 0
        dut_in.data.value = 0

        await RisingEdge(dut_in.clk)

        dut_in.rst.value = 0

        await RisingEdge(dut_in.clk)

        # NOTE: BUGFOUND: NOTE: old
        # seq = sat_tb_default_seq()
        # await seq.start(seqr=self.env.virtual_sequencer)
        # NOTE: BUGFOUND: NOTE: new
        self.top_virtual_sequence = sat_tb_default_seq.create(name="top_virtual_sequence")
        self.top_virtual_sequence.start(seqr=self.sat_tb_env.virtual_sequencer)

        self.drop_objection()
