""" Saturation Filter Environment UVM component. """

from pyuvm import ConfigDB, uvm_env

from sat_tb_virt_sequencer import sat_tb_virt_sequencer
from uvc.ssdt import (
    uvc_ssdt_agent,
)



class sat_tb_env(uvm_env):
    def __init__(self, name="sat_tb_env", parent=None):  # NOTE: Added default values
        super().__init__(name, parent)
        self.cfg = None
        self.virtual_sequencer = None

        self.uvc_ssdt_producer = None
        self.uvc_ssdt_consumer = None

    def build_phase(self):
        super().build_phase()

        self.virtual_sequencer = sat_tb_virt_sequencer.create(
            name="virtual_sequencer", parent=self
        )

        self.cfg = ConfigDB().get(
            context=self,
            inst_name="",
            field_name="cfg",
        )
        ConfigDB().set(
            context=self,
            inst_name="virtual_sequencer",
            field_name="cfg",
            value=self.cfg,
        )

        self.uvc_ssdt_producer = uvc_ssdt_agent.create(name="uvc_ssdt_producer", parent=self)
        ConfigDB().set(
            context=self,
            inst_name="uvc_ssdt_producer",
            field_name="cfg",
            value=self.cfg.ssdt_prod_cfg,
        )

        self.uvc_ssdt_consumer = uvc_ssdt_agent.create(name="uvc_ssdt_consumer", parent=self)
        ConfigDB().set(
            context=self,
            inst_name="uvc_ssdt_consumer",
            field_name="cfg",
            value=self.cfg.ssdt_cons_cfg,
        )


    def connect_phase(self):
        self.virtual_sequencer.ssdt_producer_sequencer = self.uvc_ssdt_producer.sequencer
        self.virtual_sequencer.ssdt_consumer_sequencer = self.uvc_ssdt_consumer.sequencer

