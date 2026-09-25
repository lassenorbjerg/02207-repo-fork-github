#
# Simple PyUVM test using interface wrappers.
#

import pyuvm
from pyuvm import uvm_factory

from sat_default_test import sat_default_test
from sat_tb_defaut_seq import sat_tb_default_seq
from sat_tb_random_seq import sat_tb_random_seq

@pyuvm.test()
class sat_random_test(sat_default_test):
    def start_of_simulation_phase(self):
        super().start_of_simulation_phase()

        uvm_factory().set_type_override_by_type(
            original_type=sat_tb_default_seq,
            override_type=sat_tb_random_seq,
        )
