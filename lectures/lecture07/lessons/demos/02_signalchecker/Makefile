SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES := $(PWD)/signal_checker_top.sv
COCOTB_TOPLEVEL := signal_checker_top
COCOTB_TEST_MODULES := SignalCheckerTest

include $(shell cocotb-config --makefiles)/Makefile.sim
