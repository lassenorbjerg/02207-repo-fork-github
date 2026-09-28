import os

import cocotb
import pyuvm
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from pyuvm import ConfigDB, uvm_report_object, uvm_root, uvm_test

from sat_tb_base_seq import sat_tb_base_seq
from sat_tb_config import sat_tb_config
from sat_tb_env import sat_tb_env

# Use the reusable interface wrapper provided by the SSDT UVC.
from uvc.ssdt import (
    ssdt_interface_wrapper,
)


@pyuvm.test()
class sat_tb_base_test(uvm_test):
    """ Base test component for the Saturation Filter TB."""

    def __init__(self, name, parent=None):
        # Helper code to set pyuvm loglevel from the commandline
        # ----------------------------------------------------------------------
        if os.getenv("PYUVM_LOG_LEVEL") in ["DEBUG", "CRITICAL", "ERROR", "WARNING", "INFO", "NOTSET", "NullHandler"]:
            _PYUVM_LOG_LEVEL = os.getenv('PYUVM_LOG_LEVEL')
        else:
            _PYUVM_LOG_LEVEL = "INFO"
            if os.getenv("PYUVM_LOG_LEVEL") is not None:
                uvm_root().logger.warning(f"{'='*50}\n   Wrong value for 'PYUVM_LOG_LEVEL' in Makefile. Changing to default value: 'INFO'.\n    {'='*50}")

        uvm_report_object.set_default_logging_level(_PYUVM_LOG_LEVEL)
        # ----------------------------------------------------------------------

        super().__init__(name, parent)

        # Configuration object handler
        self.cfg = None

        # Declare Environment handler
        self.tb_env = None

        # Declare DUT handler
        self.dut = None

        # Declare Virtual Sequence handler
        self.virt_sequence = None

        # Agent's interfaces
        self.ssdt_prod_if = None
        self.ssdt_cons_if = None

    def build_phase(self):
        self.logger.debug("Start build_phase() -> SAT base test")
        super().build_phase()

        # Access the DUT through the cocotb.top handle
        self.dut = cocotb.top

        # Create the config using the factory
        self.cfg = sat_tb_config.create(name="sat_tb_config")

        # Instantiate interfaces for the producer at the DUT input and the
        # consumer at the DUT output.
        self.ssdt_prod_if = ssdt_interface_wrapper("ssdt_prod_if")
        self.ssdt_cons_if = ssdt_interface_wrapper("ssdt_cons_if")

        # Assign each interface to its agent configuration's virtual interface.
        self.cfg.ssdt_prod_cfg.vif = self.ssdt_prod_if
        self.cfg.ssdt_cons_cfg.vif = self.ssdt_cons_if

        # Instantiate Environment
        self.tb_env = sat_tb_env.create(name="sat_tb_env", parent=self)

        # Keep sharing the complete testbench configuration with the environment
        # through ConfigDB.
        ConfigDB().set(
            context     = self,
            inst_name   = 'sat_tb_env',
            field_name  = 'cfg',
            value       = self.cfg,
        )
        self.logger.debug("End build_phase() -> SAT base test")

    def connect_phase(self):
        self.logger.debug("Start connect_phase() -> SAT base test")

        # Connect the producer interface to the DUT input signals.
        self.ssdt_prod_if.connect(
            clk_signal=self.dut.clk,
            reset_signal=self.dut.rst,
            valid_signal=self.dut.in_valid,
            data_signal=self.dut.in_data,
        )
        # Connect the consumer interface to the DUT output signals.
        self.ssdt_cons_if.connect(
            clk_signal=self.dut.clk,
            reset_signal=self.dut.rst,
            valid_signal=self.dut.out_valid,
            data_signal=self.dut.out_data,
        )
        self.logger.debug("End connect_phase() -> SAT base test")

    async def run_phase(self):
        self.logger.debug("Start run_phase() -> SAT base test")

        # Create and start a 2ns period clock
        clock = Clock(self.ssdt_prod_if.clk, 2, unit="ns")
        cocotb.start_soon(clock.start())

        # Reset input values
        self.ssdt_prod_if.data.value = 0
        self.ssdt_prod_if.valid.value = 0

        # Reset device
        self.ssdt_prod_if.rst.value = 1
        await RisingEdge(self.ssdt_prod_if.clk)
        self.ssdt_prod_if.rst.value = 0

        # Create a virtual sequence
        self.virtual_sequence = sat_tb_base_seq.create(name="sat_tb_base_seq")

        self.logger.debug("End run_phase() -> SAT base test")
