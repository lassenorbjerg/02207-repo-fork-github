""" Summer Reference Model
"""

from pyuvm import uvm_analysis_port, uvm_subscriber


class summer_ref_model(uvm_subscriber):
    """ Handler for Reference Model."""

    def __init__(self, name="summer_ref_model", parent=None):
        super().__init__(name, parent)
        self.previous_input = 0

        # Analysis port for sending ref model item
        self.analysis_port = uvm_analysis_port(
            name = f"{self.get_name()}_analysis_port",
            parent = self,
        )

    def write(self, item):
        # This is the write function of the analysis export from the uvm_subscriber
        self.logger.info(f"Ref. model recieved {item.data}")

        def calculate_output(input_value, previous_input):
            return (input_value + previous_input) & 0xFF

        output_item = item.clone()

        input_value = int(item.data)
        out_value = calculate_output(
            input_value=input_value,
            previous_input=self.previous_input,
        )
        self.previous_input = input_value

        output_item.data = out_value

        self.logger.info(f"Ref. model sending: {output_item.data}")
        self.analysis_port.write(output_item)
