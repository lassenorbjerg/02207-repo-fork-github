#__RELEASE_REMOVE_BEGIN__
# ruff: noqa: I001
import random

#__RELEASE_REMOVE_END__
import cocotb
from cocotb.clock import Clock
#__RELEASE_REPLACE_BEGIN__
from cocotb.triggers import ClockCycles, ReadOnly, RisingEdge, Timer
# ruff: noqa: ERA001
#__RELEASE_REPLACE_WITH__
# from cocotb.triggers import RisingEdge
#__RELEASE_REPLACE_END__[COMMENT_STRING="# "]


@cocotb.test()
async def mux_basic_test(dut):
  """Test for out=A[1]"""

  # Start the clock as the mux RTL is clocked
  # NOTE: NO reset signal in the RTL
  clk = Clock(signal=dut.clk, period=2, unit="ns")
  clk.start()

#__RELEASE_REMOVE_BEGIN__

  # Set A to 11
  # And sel to 1, selecting bit number 1 in A
  # for output
  A   = 11
  sel = 1

  # Drive A and sel
  dut.A.value   = A
  dut.sel.value = sel

  # Await the CLK to let the RTL update state
  await RisingEdge(dut.clk)
  # Wait an extra clock and for the ReadOnly region
  # So RTL has settled
  await RisingEdge(dut.clk)
  await ReadOnly()

  # Check that the MUX is working correctly
  assert dut.out.value == 1, "Mux result is incorrect"

  # Testing different triggers
  await Timer(2, 'ns')
  await ClockCycles(dut.clk, 2)
  await RisingEdge(dut.clk)
#__RELEASE_REMOVE_END__

@cocotb.test()
async def mux_randomized_test(dut):
  """Test for randomizing out=A[sel]"""

  # Start the clock as the mux RTL is clocked
  # NOTE: NO reset signal in the RTL
  clk = Clock(signal=dut.clk, period=2, unit="ns")
  clk.start()

#__RELEASE_REMOVE_BEGIN__
  dut.A.value   = 0
  dut.sel.value = 0

  # Sample reset values into DUT
  await RisingEdge(dut.clk)

  # Do 10 random transaction, one per clk.
  for _ in range(10):
    # Randomize input stimuli
    A   = random.randint(0, 15)
    sel = random.randint(0,  3)

    # Drive A and sel
    dut.A.value   = A
    dut.sel.value = sel

    # Await the CLK to let the RTL update state
    await RisingEdge(dut.clk)
    # Wait for all delta cycles to settle
    await ReadOnly()

    # Compute expected result
    expected_result = (A >> sel) & 1

    await RisingEdge(dut.clk)

    assert dut.out.value == expected_result, "Mux result is incorrect"
#__RELEASE_REMOVE_END__
