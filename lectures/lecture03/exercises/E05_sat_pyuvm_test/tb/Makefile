# This is the makefile for running cocotb tests for the Saturation Filter

PWD=$(shell pwd)

TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES = $(PWD)/../rtl/sat_filter.sv

# Defines toplevel RTL
COCOTB_TOPLEVEL := sat_filter

# Defines cocotb test files
# !!! new tests must be added without spaces, e.g.,
# COCOTB_TEST_MODULES := sat_default_test,another_test,another_test !!!
COCOTB_TEST_MODULES := sat_default_test,sat_random_test,sat_interface_test

# Set build folder
SIM_BUILD = $(PWD)/sim_build

include $(shell cocotb-config --makefiles)/Makefile.sim

clean::
	@$(MAKE) local-clean -C $(PWD)

.PHONY: local-clean
local-clean:
	@echo -e "\n------------------ Internal cleanup --------------------\n"
	# Remove all __pycache__ folders
	@rm -fvr $(shell find $(ROOT_DIR) -type d \( -iname '__pycache__' \);)
	# Remove results.xml
	@rm -fr $(shell find $(ROOT_DIR) -name results.xml)
