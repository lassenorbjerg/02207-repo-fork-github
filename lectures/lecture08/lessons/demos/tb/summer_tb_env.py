""" Summer Environment UVM component. """

from pyuvm import ConfigDB, uvm_env

from summer_coverage import summer_coverage
from summer_ref_model import summer_ref_model
from summer_tb_scoreboard import summer_tb_scoreboard
from summer_tb_virt_sequencer import summer_tb_virt_sequencer
from uvc.ssdt import (
    uvc_ssdt_agent,
)


class summer_tb_env(uvm_env):
    """ UVM Environment component for the Summer TB. """

    def __init__(self, name, parent=None):

        super().__init__(name, parent)

        self.cfg = None
        self.virtual_sequencer = None

        self.ref_model = None
        self.scoreboard = None
        self.coverage = None
 
        # Create empty handles for the producer and consumer agents.
        self.uvc_ssdt_producer = None
        self.uvc_ssdt_consumer = None

    def build_phase(self):
        self.logger.debug("Start build_phase() -> SUMMER environment")
        super().build_phase()

        # Get the configuration object
        self.cfg = ConfigDB().get(
            context    = self,
            inst_name  = "",
            field_name = "cfg",
        )

        # Instantiate Virtual Sequencer
        self.virtual_sequencer = summer_tb_virt_sequencer.create(
            name   = "summer_tb_top_seqr",
            parent = self,
        )
        # Propagate config to vseqr
        ConfigDB().set(
            context     = self,
            inst_name   = "summer_tb_top_seqr",
            field_name  = "cfg",
            value       = self.cfg,
        )
        self.logger.debug(f"Virtual Sequencer < {self.virtual_sequencer} > created")

        self.logger.debug("Creating Scoreboard...")
        self.scoreboard = summer_tb_scoreboard.create(
            name = "summer_tb_scoreboard",
            parent = self,
        )
        self.logger.debug(f"Scoreboard < {self.scoreboard} > created")

        self.logger.debug("Creating Coverage Collector...")
        self.coverage = summer_coverage.create(
            name = "summer_coverage",
            parent = self,
        )
        self.logger.debug(f"Coverage Collector < {self.coverage} > created")

        # Instantiate Reference Model
        self.logger.debug("Creating Reference Model...")
        self.ref_model = summer_ref_model.create(
            name = "summer_ref_model",
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
        self.logger.debug("End build_phase() -> SUMMER environment")

    def connect_phase(self):
        self.logger.debug("Start connect_phase() -> SUMMER environment")
        super().connect_phase()

        # Connect the producer agent's sequencer to the corresponding virtual
        # sequencer handle.
        self.virtual_sequencer.ssdt_producer_sequencer = self.uvc_ssdt_producer.sequencer
        # Connect the consumer agent's sequencer to the corresponding virtual
        # sequencer handle.
        self.virtual_sequencer.ssdt_consumer_sequencer = self.uvc_ssdt_consumer.sequencer

        # Connect consumer agents analysis port with scoreboard
        self.uvc_ssdt_consumer.analysis_port.connect(
            self.scoreboard.uvc_ssdt_consumer_fifo.analysis_export,
        )
 
        # Connect producer agent analysis port with ref. model
        self.uvc_ssdt_producer.analysis_port.connect(self.ref_model.analysis_export)
        # Connect producer agent analysis port with coverage collector
        self.uvc_ssdt_producer.analysis_port.connect(self.coverage.analysis_export)
        # Connect ref model handler analysis port to the scoreboard
        self.ref_model.analysis_port.connect(
            self.scoreboard.ref_model_fifo.analysis_export,
        )


        self.logger.debug("End connect_phase() -> SUMMER environment")
