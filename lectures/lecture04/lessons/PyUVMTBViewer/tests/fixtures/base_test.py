from environment import DemoEnvironment
from pyuvm import uvm_test


class DemoBaseTest(uvm_test):
    def build_phase(self):
        super().build_phase()
        self.environment = DemoEnvironment.create("environment", self)

    def connect_phase(self):
        super().connect_phase()
