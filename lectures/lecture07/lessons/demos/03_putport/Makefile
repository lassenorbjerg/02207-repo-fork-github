SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES := $(PWD)/putport_top.sv
COCOTB_TOPLEVEL := putport_top
COCOTB_TEST_MODULES := putport

include $(shell cocotb-config --makefiles)/Makefile.sim
