""" SSDT-UVC Coverage collector
"""

import vsc
from pyuvm import ConfigDB, uvm_subscriber

from .uvc_ssdt_seq_item import uvc_ssdt_seq_item


class uvc_ssdt_coverage(uvm_subscriber):

    def __init__(self, name, parent):

        super().__init__(name, parent)
        self.cfg = None

    def build_phase(self):

        self.logger.debug("build_phase() SSDT_Coverage")
        super().build_phase()

        # Create the covergroup
        # Get the configuration object
        self.cfg = ConfigDB().get(self, "", "cfg")

        self.cg_ssdt = covergroup_ssdt(f"{self.get_full_name()}.cg_ssdt", int(self.cfg.DATA_WIDTH))

    # "write" method to sample the covergroups
    def write(self, item: uvc_ssdt_seq_item):
        """Sampling method"""

        self.logger.debug(f"SSDT_Coverage received {item}")
        self.cg_ssdt.sample(item.data)


# Covergroup class
@vsc.covergroup
class covergroup_ssdt:

    def __init__(self, name, ssdt_configs):

        self.options.name = name

        # Define the parameters accepted by the sample function
        self.with_sample(
            data = vsc.bit_t(ssdt_configs),
        )

        MAX_VALUE = (2**ssdt_configs)

        self.cp_data = vsc.coverpoint(self.data, bins={
            "data_0" :          vsc.bin(0),
            "data_max" :        vsc.bin(MAX_VALUE-1),
            "data_others" :     vsc.bin([1, MAX_VALUE-2]),
            },
        )
