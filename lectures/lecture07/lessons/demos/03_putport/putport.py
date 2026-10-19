import random

import cocotb
import pyuvm
from cocotb.triggers import Timer as _CocotbTimer
from pyuvm import (
    uvm_component,
    uvm_env,
    uvm_put_export,
    uvm_put_port,
    uvm_test,
)

def Timer(time, units):
    """Accept the uppercase time unit used by this original demo."""
    return _CocotbTimer(time, unit=units.lower())
class simple_seq_item:
    """Small transaction object passed through the put port."""

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
        self.put_port = uvm_put_port("put_port", self)

    async def run_phase(self):
        await super().run_phase()
        self.raise_objection()
        try:
            for _ in range(10):
                trans = simple_seq_item()
                trans.randomize()
                self.logger.info("Producing transaction: %s", trans)
                await self.put_port.put(trans)
                await Timer(10, "NS")
        finally:
            self.drop_objection()

class Consumer(uvm_put_export):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.num_received = 0

    async def put(self, transaction):
        self._consume(transaction)

    def try_put(self, transaction):
        self._consume(transaction)
        return True

    def can_put(self):
        return True

    def _consume(self, transaction):
        self.num_received += 1
        self.logger.info("Consuming transaction: %s", transaction)

class TopEnv(uvm_env):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        super().build_phase()
        self.logger.info("Creating ports")
        self.producer = Producer("producer", self)
        self.consumer = Consumer("consumer", self)

    def connect_phase(self):
        super().connect_phase()
        self.logger.info("Connecting ports")
        self.producer.put_port.connect(self.consumer)


@pyuvm.test()
class PutPortTest(uvm_test):
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
        assert self.env.consumer.num_received == 10, (
            f"Expected 10 transactions, received {self.env.consumer.num_received}"
        )
