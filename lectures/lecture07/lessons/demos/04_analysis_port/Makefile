SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES := $(PWD)/analysis_port_top.sv
COCOTB_TOPLEVEL := analysis_port_top
COCOTB_TEST_MODULES := analysis_port

include $(shell cocotb-config --makefiles)/Makefile.sim
