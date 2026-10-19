""" Saturation Filter Reference Model
"""

from pyuvm import uvm_analysis_port, uvm_subscriber


class sat_ref_model(uvm_subscriber):
    """ Handler for Reference Model."""

    def __init__(self, name="sat_ref_model", parent=None):
        super().__init__(name, parent)
        self.uvm_analysis_port = uvm_analysis_port.create(name="uvm_analysis_port")


    def write(self, item):
        # This is the write function of the analysis export from the uvm_subscriber
        self.logger.debug(f"Ref. model recieved {item}")
        cloned = item.clone()

        self.logger.debug(f"Ref. model sent {cloned}")
        self.logger.debug("")
        cloned.data = item.data if item.data < 64 else 64
        self.logger.debug(f"Ref. model sent {cloned}")
        self.logger.debug("aaaa")
        self.uvm_analysis_port.write(cloned)


