import pyuvm
from base_test import DemoBaseTest


@pyuvm.test()
class DemoTest(DemoBaseTest):
    async def run_phase(self):
        self.raise_objection()
        await super().run_phase()
        self.drop_objection()
