# This is the makefile for running cocotb tests for the Saturation Filter

PWD=$(shell pwd)

TOPLEVEL_LANG ?= verilog

export PYTHONWARNINGS=ignore

VERILOG_SOURCES = $(PWD)/../rtl/sat_filter.sv

# Defines toplevel RTL
COCOTB_TOPLEVEL := sat_filter

# Defines cocotb test files
# !!! new tests must be added without spaces, e.g.,
# COCOTB_TEST_MODULES := sat_default_test,another_test,another_test !!!
COCOTB_TEST_MODULES := tests.sat_tb_default_test
COCOTB_TEST_MODULES := tests.sat_tb_around_threshold_test,tests.sat_tb_default_test,tests.sat_tb_less_than_threshold_test,tests.sat_tb_over_threshold_test,tests.sat_tb_random_test,tests.sat_tb_rand_n_seq_test,tests.sat_tb_min_rand_n_seq_test

# Set build folder
SIM_BUILD = $(PWD)/sim_build

include $(shell cocotb-config --makefiles)/Makefile.sim

# -------------------------------------------------------------------------------
# Because of PyVSC and coverage
# -------------------------------------------------------------------------------

# PyVSC (help debug)
export VSC_SOLVEFAIL_DEBUG = 0
export VSC_CAPTURE_SRCINFO = 0
export VSC_DEBUG = 0

SIM_BUILD = $(PWD)/sim_build
COV_FILES = $(shell find $(SIM_BUILD) -type f \( -iname "sat_tb*cov.xml" \))

# https://pyucis.readthedocs.io/en/latest/commands.html
.PHONY: coverage-merge
coverage-merge:
	@echo ""
	@echo "======================================================"
	@echo "Merging coverage files..."
	@echo $(SIM_BUILD)
	@echo $(COV_FILES)
	@echo "======================================================"
	@echo ""
	@$(VIRTUAL_ENV)/bin/pyucis merge --out $(SIM_BUILD)/merge_cov.xml $(COV_FILES)

.PHONY: coverage-view-merge
coverage-view-merge: coverage-merge
	@echo ""
	@echo "======================================================"
	@echo "Opening PyUCIS-viewer"
	@echo "======================================================"
	@echo ""
	@$(VIRTUAL_ENV)/bin/pyucis-viewer $(SIM_BUILD)/merge_cov.xml

.PHONY: coverage
coverage: coverage-view-merge

#
clean::
	@$(MAKE) local-clean -C $(PWD)

.PHONY: local-clean
local-clean:
	@echo -e "\n------------------ Internal cleanup --------------------\n"
	# Remove all __pycache__ folders
	@rm -fvr $(shell find $(ROOT_DIR) -type d \( -iname '__pycache__' \);)
	# Remove results.xml
	@rm -fr $(shell find $(ROOT_DIR) -name results.xml)
