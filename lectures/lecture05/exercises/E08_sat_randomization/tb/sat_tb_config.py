from pyuvm import uvm_active_passive_enum, uvm_object

# Import the SSDT UVC configuration and producer/consumer driver types.
from uvc.ssdt import uvc_ssdt_config, uvc_ssdt_type_enum


class sat_tb_config(uvm_object):

    def __init__(self, name="cl_sdt_tb_config"):

        super().__init__(name)

        # Create separate UVC configuration objects for the producer and
        # consumer agents using the factory.
        self.ssdt_prod_cfg = uvc_ssdt_config.create("ssdt_prod_cfg")
        self.ssdt_cons_cfg = uvc_ssdt_config.create("ssdt_cons_cfg")

        # Configure the producer agent as active with a producer driver.
        self.ssdt_prod_cfg.is_active         = uvm_active_passive_enum.UVM_ACTIVE
        self.ssdt_prod_cfg.driver_type       = uvc_ssdt_type_enum.PRODUCER

        # Configure the consumer agent as active with a consumer driver.
        self.ssdt_cons_cfg.is_active         = uvm_active_passive_enum.UVM_ACTIVE
        self.ssdt_cons_cfg.driver_type       = uvc_ssdt_type_enum.CONSUMER

