#
# Simple PyUVM test using interface wrappers.
#

import cocotb
import pyuvm
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from pyuvm import ConfigDB, uvm_test

from sat_tb_config import sat_tb_config
from sat_tb_default_seq import sat_tb_default_seq
from sat_tb_env import sat_tb_env
from uvc.ssdt import (
    ssdt_interface_wrapper,
)


