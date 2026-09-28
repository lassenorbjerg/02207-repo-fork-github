from pyuvm import uvm_active_passive_enum, uvm_object

from uvc.ssdt import uvc_ssdt_config, uvc_ssdt_type_enum



class sat_tb_config(uvm_object):
    def __init__(self, name="sat_tb_config"):  # NOTE: default name
        super().__init__(name)

        self.ssdt_prod_cfg = uvc_ssdt_config.create(name="ssdt_prod_cfg")
        self.ssdt_cons_cfg = uvc_ssdt_config.create(name="ssdt_cons_cfg")
        # self.input_if = self.ssdt_prod_cfg.vif
        # self.output_if = self.ssdt_cons_cfg.vif

        self.ssdt_prod_cfg.is_active = uvm_active_passive_enum.UVM_ACTIVE
        self.ssdt_prod_cfg.driver_type = uvc_ssdt_type_enum.PRODUCER
        self.ssdt_cons_cfg.is_active = uvm_active_passive_enum.UVM_ACTIVE
        self.ssdt_cons_cfg.driver_type = uvc_ssdt_type_enum.CONSUMER





