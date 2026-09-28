# Setting the Simulator
SIM ?= icarus
# Setting the RTL Language
TOPLEVEL_LANG ?= verilog

# Defining path
PWD=$(shell pwd)

# Adding the reference model to the python path
export PYTHONPATH := $(PWD)/../ref_model:$(PYTHONPATH)

# Adding all Verilog sources
VERILOG_SOURCES = $(PWD)/../rtl/adder.sv

# COCOTB_TOPLEVEL is the name of the toplevel module in the Verilog file(s)
COCOTB_TOPLEVEL := adder
#
# COCOTB_TEST_MODULES are all Python test files to run
COCOTB_TEST_MODULES   := test_adder

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

# Clean target to remove all generated simulation files
clean::
	@$(MAKE) local-clean -C $(PWD)

.PHONY: local-clean
local-clean:
	@echo -e "\n------------------ Internal cleanup --------------------\n"
	# Remove all __pycache__ folders
	@rm -fvr $(shell find $(ROOT_DIR) -type d \( -iname '__pycache__' \);)
	@rm -rf $(PWD)/../ref_model/__pycache__
# Remove results.xml
	@rm -fr $(shell find $(ROOT_DIR) -name results.xml)
