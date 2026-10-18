"""A small PyUVM analysis-port and scoreboard example."""

import pyuvm
from pyuvm import (
    uvm_analysis_port,
    uvm_env,
    uvm_error,
    uvm_sequence_item,
    uvm_subscriber,
    uvm_test,
)


class BusItem(uvm_sequence_item):
    """A transaction with an 8-bit address and an 8-bit data field."""

    def __init__(self, name, address, data):
        super().__init__(name)
        self.address = self._check_byte("address", address)
        self.data = self._check_byte("data", data)

    @staticmethod
    def _check_byte(field_name, value):
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 0xFF:
            raise ValueError(f"{field_name} must be an 8-bit integer, got {value!r}")
        return value

    def __eq__(self, other):
        return (
            isinstance(other, BusItem)
            and self.address == other.address
            and self.data == other.data
        )

    def __str__(self):
        return f"{self.get_name()}(address=0x{self.address:02X}, data=0x{self.data:02X})"


class Scoreboard(uvm_subscriber):
    """Compare each received item against the next expected item."""

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.expected_data = []
        self.matches = 0
        self.mismatches = 0

    def write(self, item):
        if not self.expected_data:
            self.mismatches += 1
            uvm_error("Scoreboard", f": Unexpected item received: {item}")
            return

        expected_item = self.expected_data.pop(0)
        if item == expected_item:
            self.matches += 1
            self.logger.info(f"Matched: {item}")
        else:
            self.mismatches += 1
            uvm_error(
                "Scoreboard",
                f": Mismatch: received {item}, expected {expected_item}",
            )

    def add_expected_data(self, item):
        self.expected_data.append(item)

    def check_phase(self):
        super().check_phase()
        if self.expected_data:
            uvm_error(
                "Scoreboard",
                f"{len(self.expected_data)} expected item(s) were not received",
            )


class ScoreboardEnv(uvm_env):
    """Environment containing the scoreboard."""

    def build_phase(self):
        super().build_phase()
        self.scoreboard = Scoreboard.create("scoreboard", self)


@pyuvm.test()
class ScoreboardTest(uvm_test):
    """Send two matching transactions and one intentional mismatch."""

    def build_phase(self):
        super().build_phase()
        self.analysis_port = uvm_analysis_port("analysis_port", self)
        self.env = ScoreboardEnv.create("env", self)

    def connect_phase(self):
        super().connect_phase()
        self.analysis_port.connect(self.env.scoreboard.analysis_export)

    async def run_phase(self):
        self.raise_objection()

        expected = [
            BusItem("expected_1", 0x10, 0xA1),
            BusItem("expected_2", 0x20, 0xB2),
            BusItem("expected_3", 0x30, 0xC3),
        ]
        for item in expected:
            self.env.scoreboard.add_expected_data(item)

        received = [
            BusItem("received_1", 0x10, 0xA1),
            BusItem("received_2", 0x20, 0xB2),
            # Deliberately wrong data value to show a scoreboard mismatch.
            BusItem("received_3", 0x30, 0xFF),
        ]
        for item in received:
            self.analysis_port.write(item)

        self.drop_objection()
