from pyuvm import uvm_agent, uvm_driver, uvm_monitor, uvm_sequencer


class DemoProducerDriver(uvm_driver):
    pass


class DemoConsumerDriver(uvm_driver):
    pass


class DemoMonitor(uvm_monitor):
    async def run_phase(self):
        await super().run_phase()


class DemoAgent(uvm_agent):
    def build_phase(self):
        super().build_phase()
        if self.cfg.is_producer:
            self.driver = DemoProducerDriver.create("driver", self)
        else:
            self.driver = DemoConsumerDriver.create("driver", self)
        self.sequencer = uvm_sequencer.create("sequencer", self)
        if self.cfg.coverage_enabled:
            self.monitor = DemoMonitor.create("monitor", self)

    def connect_phase(self):
        super().connect_phase()
        self.monitor.analysis_port.connect(self.analysis_port)
