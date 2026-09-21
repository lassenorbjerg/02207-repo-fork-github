from pyuvm import uvm_object

class sat_tb_config(uvm_object):
    def __init__(self, name="config"):
        super().__init__(name)
        self.input_if = None
        self.output_if = None



