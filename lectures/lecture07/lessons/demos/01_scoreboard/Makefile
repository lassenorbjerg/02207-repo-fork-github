SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES := $(PWD)/scoreboard_top.sv
COCOTB_TOPLEVEL := scoreboard_top
COCOTB_TEST_MODULES := Scoreboard

include $(shell cocotb-config --makefiles)/Makefile.sim
