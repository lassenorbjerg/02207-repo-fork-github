""" Summer Coverage collector"""

import vsc
from pyuvm import uvm_subscriber


# Covergroup for consecutive summer input values.
@vsc.covergroup
class _covergroup_summer:
    def __init__(self, name):
        self.options.name = name

        # Define the parameters accepted by the sample function
        self.with_sample(
            current_value = vsc.bit_t(8),
            previous_value = vsc.bit_t(8),
        )

        self.cp_current_value = vsc.coverpoint(self.current_value, bins={
            "values": vsc.bin_array([], [0, 255]),
        })

        self.cp_previous_value = vsc.coverpoint(self.previous_value, bins={
            "values": vsc.bin_array([], [0, 255]),
        })

        self.cp_current_previous_cross = vsc.cross([
            self.cp_current_value,
            self.cp_previous_value,
        ])


class summer_coverage(uvm_subscriber):
    """Collect coverage from producer transactions."""

    def __init__(self, name="summer_coverage", parent=None):
        super().__init__(name, parent)
        self.covergroup = _covergroup_summer(name=f"{name}_covergroup")
        self.previous_value = 0

    def write(self, item):
        current_value = int(item.data)
        self.covergroup.sample(current_value, self.previous_value)
        self.previous_value = current_value
