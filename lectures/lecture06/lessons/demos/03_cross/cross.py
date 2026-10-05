"""Small PyVSC covergroup example: sample all state/mode combinations."""

from pathlib import Path
import vsc


@vsc.covergroup
class MyCovergroup:
    def __init__(self, state: callable, mode: callable):
        self.cp_state = vsc.coverpoint(
            state,
            bins={
                "s1": vsc.bin(0),
                "s2": vsc.bin(1),
                "s3": vsc.bin(2),
            },
        )
        self.cp_mode = vsc.coverpoint(
            mode,
            bins={
                "a": vsc.bin(0),
                "b": vsc.bin(1),
                "c": vsc.bin(2),
            },
        )

        self.cr_state_mode = vsc.cross([self.cp_state, self.cp_mode])

# Each list has five values. Repetition deliberately exercises bin hit counts.
cp_state_values = [0, 1, 2, 0, 1]
cp_mode_values = [0, 1, 2, 1, 0]

# The callables supply each sampled value to the coverpoints.
current = {"state": 0, "mode": 0}
cg = MyCovergroup(lambda: current["state"], lambda: current["mode"])

# Sample 5 x 5 = 25 state/mode combinations.
for state in cp_state_values:
    for mode in cp_mode_values:
        current["state"] = state
        current["mode"] = mode
        cg.sample()

# Save the human-readable report as text, and the portable coverage database
# as UCIS XML. PyVSC's report API accepts a text stream.
report_path = Path("coverage_report.txt")
report_path.write_text(vsc.get_coverage_report(details=True), encoding="utf-8")
vsc.write_coverage_db("coverage.xml")

print(f"Text report saved to: {report_path.resolve()}")
print("UCIS coverage database saved to: coverage.xml")
print(report_path.read_text(encoding="utf-8"))
