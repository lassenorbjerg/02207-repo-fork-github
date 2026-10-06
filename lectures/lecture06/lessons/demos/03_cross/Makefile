PYTHON ?= python
PYUCIS_VIEWER ?= pyucis-viewer

.PHONY: all run view clean

all: run

run:
	$(PYTHON) cross.py

view: run
	$(PYUCIS_VIEWER) coverage.xml

clean:
	$(RM) coverage.xml coverage_report.txt
