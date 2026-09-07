IVERILOG ?= iverilog
VVP      ?= vvp

SOURCES := 01_race_demo.v 02_feedback_race.v 03_reset_release_race.v
TARGETS := $(SOURCES:.v=.vvp)
WAVES   := $(SOURCES:.v=.fst)

.PHONY: all run clean
.PHONY: 01_race_demo clean_01_race_demo
.PHONY: 02_feedback_race clean_02_feedback_race
.PHONY: 03_reset_release_race clean_03_reset_release_race

all: 01_race_demo 02_feedback_race 03_reset_release_race

run: all

%.vvp: %.v
	$(IVERILOG) -g2012 -o $@ $<

%.fst: %.vvp
	$(VVP) $< -fst

01_race_demo: 01_race_demo.fst

clean_01_race_demo:
	rm -f 01_race_demo.vvp 01_race_demo.fst

02_feedback_race: 02_feedback_race.fst

clean_02_feedback_race:
	rm -f 02_feedback_race.vvp 02_feedback_race.fst

03_reset_release_race: 03_reset_release_race.fst

clean_03_reset_release_race:
	rm -f 03_reset_release_race.vvp 03_reset_release_race.fst

clean: clean_01_race_demo clean_02_feedback_race clean_03_reset_release_race
