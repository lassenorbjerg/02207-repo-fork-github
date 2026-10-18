""" Saturation Filter Reference Model
"""

from pyuvm import uvm_analysis_port, uvm_subscriber


class sat_ref_model(uvm_subscriber):
    """ Handler for Reference Model."""

    def __init__(self, name="sat_ref_model", parent=None):
        super().__init__(name, parent)





    def write(self, item):
        # This is the write function of the analysis export from the uvm_subscriber
        self.logger.info(f"Ref. model recieved {item}")


