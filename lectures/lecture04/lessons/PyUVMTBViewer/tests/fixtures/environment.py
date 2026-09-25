from agent import DemoAgent
from pyuvm import uvm_env


class DemoEnvironment(uvm_env):
    def build_phase(self):
        super().build_phase()
        self.producer = DemoAgent.create("producer", self)
        self.consumer = DemoAgent.create("consumer", self)

    def connect_phase(self):
        super().connect_phase()
        self.producer.analysis_port.connect(self.consumer.analysis_export)
