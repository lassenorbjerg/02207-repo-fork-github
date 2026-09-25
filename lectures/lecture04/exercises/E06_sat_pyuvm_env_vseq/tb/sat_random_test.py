#
# Simple PyUVM test using interface wrappers.
#

import pyuvm
from pyuvm import uvm_factory

from sat_default_test import sat_default_test


class sat_random_test(sat_default_test):
    def start_of_simulation_phase(self):
        super().start_of_simulation_phase()
