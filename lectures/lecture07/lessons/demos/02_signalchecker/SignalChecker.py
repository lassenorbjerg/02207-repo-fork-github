"""Check sig_b five clocks after sig_a starts an event."""

from cocotb.triggers import ReadOnly, RisingEdge
from pyuvm import ConfigDB, uvm_component, uvm_error

class SignalChecker(uvm_component):
    CHECK_DELAY_CYCLES = 5

    def build_phase(self):
        super().build_phase()
        self.clk = ConfigDB().get(self, "", "clk")
        self.sig_a = ConfigDB().get(self, "", "sig_a")
        self.sig_b = ConfigDB().get(self, "", "sig_b")
        self.start_check = False
        self.clk_count = 0

    async def run_phase(self):
        while True:
            await RisingEdge(self.clk)
            await ReadOnly()

            if not self.start_check:
                if int(self.sig_a.value) == 1:
                    self.start_check = True
                    self.clk_count = 0
                continue

            self.clk_count += 1
            if self.clk_count >= self.CHECK_DELAY_CYCLES:
                if int(self.sig_b.value) == 1:
                    self.logger.info("Assertion passed")
                else:
                    uvm_error("SignalChecker: ", "Assertion failed")

                # Allow the checker to start another independent observation.
                self.start_check = False
                self.clk_count = 0
