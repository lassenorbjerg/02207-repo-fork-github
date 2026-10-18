import random

import pyuvm
from cocotb.triggers import Timer as _CocotbTimer
from pyuvm import (
    uvm_analysis_export,
    uvm_analysis_port,
    uvm_component,
    uvm_env,
    uvm_test,
)


def Timer(time, units):
    """Accept the uppercase time unit used by this original demo."""
    return _CocotbTimer(time, unit=units.lower())


class simple_seq_item:
    """Small transaction object passed through the analysis port."""

    def __init__(self):
        self.data = 0

    def randomize(self):
        self.data = random.randrange(256)
        return True

    def __str__(self):
        return f"simple_seq_item(data=0x{self.data:02X})"


class Producer(uvm_component):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.analysis_port = uvm_analysis_port("analysis_port", self)

    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()
        try:
            for _ in range(10):
                trans = simple_seq_item()
                trans.randomize()
                self.logger.info("Producing transaction: %s", trans)
                self.analysis_port.write(trans)
                await Timer(10, "NS")
        finally:
            self.drop_objection()


class Consumer(uvm_analysis_export):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.num_received = 0

    def write(self, trans):
        self.num_received += 1
        self.logger.info("Consuming transaction: %s", trans)


class TopEnv(uvm_env):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        super().build_phase()
        self.producer = Producer("producer", self)
        self.consumer0 = Consumer("consumer0", self)
        self.consumer1 = Consumer("consumer1", self)

    def connect_phase(self):
        super().connect_phase()
        self.logger.info("Connecting analysis ports")
        self.producer.analysis_port.connect(self.consumer0)
        self.producer.analysis_port.connect(self.consumer1)


@pyuvm.test()
class AnalysisPortTest(uvm_test):
    """Run the environment long enough to send all ten transactions."""

    def build_phase(self):
        super().build_phase()
        self.env = TopEnv("env", self)

    async def run_phase(self):
        await super().run_phase()
        self.raise_objection()
        await Timer(120, "NS")
        self.drop_objection()

    def check_phase(self):
        super().check_phase()
        for consumer in (self.env.consumer0, self.env.consumer1):
            assert consumer.num_received == 10, (
                f"{consumer.get_name()} expected 10 transactions, "
                f"received {consumer.num_received}"
            )
