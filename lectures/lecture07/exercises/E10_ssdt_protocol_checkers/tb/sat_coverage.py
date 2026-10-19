""" Sat Coverage collector"""

import vsc


# Covergroup class to sample the ovf signal
@vsc.covergroup
class covergroup_sat:
    def __init__(self, name):
        self.options.name = name

        # Define the parameters accepted by the sample function
        self.with_sample(
            ovf = vsc.bit_t(1),
            count = vsc.uint32_t(),
        )

        self.cp_count = vsc.coverpoint(self.count, bins={
            "count": vsc.bin_array([], [1, 100]),
        })

        self.cp_ovf = vsc.coverpoint(self.ovf, bins = {
            "ovf_0" : vsc.bin(0),
            "ovf_1" : vsc.bin(1)},
        )

        self.cp_ovf_count_cross = vsc.cross([self.cp_ovf, self.cp_count])
