""" Saturation Filter Environment UVM component. """

from pyuvm import ConfigDB, uvm_env

from sat_ref_model import sat_ref_model
from sat_tb_scoreboard import sat_tb_scoreboard
from sat_tb_virt_sequencer import sat_tb_virt_sequencer
from uvc.ssdt import (
    uvc_ssdt_agent,
)


class sat_tb_env(uvm_env):
    """ UVM Environment component for the Saturation Filter TB. """

    def __init__(self, name, parent=None):

        super().__init__(name, parent)

        self.cfg = None
        self.virtual_sequencer = None

        self.ref_model = None


        # Create empty handles for the producer and consumer agents.
        self.uvc_ssdt_producer = None
        self.uvc_ssdt_consumer = None

    def build_phase(self):
        self.logger.debug("Start build_phase() -> SAT environment")
        super().build_phase()

        # Get the configuration object
        self.cfg = ConfigDB().get(
            context    = self,
            inst_name  = "",
            field_name = "cfg",
        )

        # Instantiate Virtual Sequencer
        self.virtual_sequencer = sat_tb_virt_sequencer.create(
            name   = "sat_tb_top_seqr",
            parent = self,
        )
        # Propagate config to vseqr
        ConfigDB().set(
            context     = self,
            inst_name   = "sat_tb_top_seqr",
            field_name  = "cfg",
            value       = self.cfg,
        )
        self.logger.debug(f"Virtual Sequencer < {self.virtual_sequencer} > created")


        # Instantiate Reference Model
        self.logger.debug("Creating Reference Model...")
        self.ref_model = sat_ref_model.create(
            name = "sat_filter_ref_model",
            parent = self,
        )
        self.logger.debug(f"Reference Model < {self.ref_model} > created")

        # Instantiate the SSDT UVC agents and provide their configurations.
        self.logger.debug("Creating ssdt uvcs agents")

        # ----- Producer ------
        # Create the producer agent using the factory.
        self.uvc_ssdt_producer = uvc_ssdt_agent.create("uvc_ssdt_producer", self)

        # Store the producer configuration in ConfigDB for the producer agent.
        ConfigDB().set(
            context     = self,
            inst_name   = "uvc_ssdt_producer",
            field_name  = "cfg",
            value       = self.cfg.ssdt_prod_cfg,
        )

        self.logger.debug(f"\nAgent < {self.uvc_ssdt_producer} > created with the following configs {self.uvc_ssdt_producer.cfg}\n")

        # ----- Consumer ------
        # Create the consumer agent using the factory.
        self.uvc_ssdt_consumer = uvc_ssdt_agent.create("uvc_ssdt_consumer", self)

        # Store the consumer configuration in ConfigDB for the consumer agent.
        ConfigDB().set(
            context     = self,
            inst_name   = "uvc_ssdt_consumer",
            field_name  = "cfg",
            value       = self.cfg.ssdt_cons_cfg,
        )

        self.logger.debug( f"\nAgent < {self.uvc_ssdt_consumer} > created with the following configs {self.uvc_ssdt_consumer.cfg}\n")
        self.logger.debug("End build_phase() -> SAT environment")

    def connect_phase(self):
        self.logger.debug("Start connect_phase() -> SAT environment")
        super().connect_phase()

        # Connect the producer agent's sequencer to the corresponding virtual
        # sequencer handle.
        self.virtual_sequencer.ssdt_producer_sequencer = self.uvc_ssdt_producer.sequencer
        # Connect the consumer agent's sequencer to the corresponding virtual
        # sequencer handle.
        self.virtual_sequencer.ssdt_consumer_sequencer = self.uvc_ssdt_consumer.sequencer


        # Connect producer agent analysis port with ref. model
        self.uvc_ssdt_producer.analysis_port.connect(self.ref_model.analysis_export)


        self.logger.debug("End connect_phase() -> SAT environment")
