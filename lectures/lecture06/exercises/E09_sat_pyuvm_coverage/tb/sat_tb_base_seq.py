from pyuvm import uvm_root, uvm_sequence


class sat_tb_base_seq(uvm_sequence):
    """ Base sequence for the Saturation Filter's TB.
        Gets the configuration from the sequencer
    """

    def __init__(self, name="sat_filter_base_seq"):

        super().__init__(name)

        self.cfg = None         # Declaration of configuration object handler
        self.sequencer = None   # Declaration of sequencer

    async def pre_body(self):

        if(self.sequencer is not None):
            uvm_root().logger.debug(
                f"{self.get_full_name()} retrieving config from sequencer.",
            )
            self.cfg = self.sequencer.cfg
