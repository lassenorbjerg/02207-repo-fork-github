"""PyUVM test for the signal checker."""

import cocotb
import pyuvm
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge
from pyuvm import ConfigDB, uvm_env, uvm_test

from SignalChecker import SignalChecker

class SignalCheckerEnv(uvm_env):
    def build_phase(self):
        super().build_phase()
        self.checker = SignalChecker.create("checker", self)

@pyuvm.test()
class SignalCheckerTest(uvm_test):
    """Drive one passing case followed by one failing case."""

    def build_phase(self):
        super().build_phase()
        self.dut = cocotb.top

        ConfigDB().set(self, "env.checker", "clk", self.dut.clk)
        ConfigDB().set(self, "env.checker", "sig_a", self.dut.sig_a)
        ConfigDB().set(self, "env.checker", "sig_b", self.dut.sig_b)
        self.env = SignalCheckerEnv.create("env", self)

    async def _drive_check(self, sig_b_value):
        # Assert sig_a for one clock, then hold sig_b until the checker samples
        # it five rising edges later.
        await FallingEdge(self.dut.clk)
        self.dut.sig_a.value = 1
        await FallingEdge(self.dut.clk)
        self.dut.sig_a.value = 0
        self.dut.sig_b.value = sig_b_value

        for _ in range(5):
            await RisingEdge(self.dut.clk)
        await FallingEdge(self.dut.clk)

    async def run_phase(self):
        self.raise_objection()

        self.dut.clk.value = 0
        self.dut.sig_a.value = 0
        self.dut.sig_b.value = 0
        cocotb.start_soon(Clock(self.dut.clk, 10, unit="ns").start())

        await self._drive_check(sig_b_value=1)
        await self._drive_check(sig_b_value=0)

        self.drop_objection()
