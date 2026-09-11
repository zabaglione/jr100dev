PYTHON ?= python3
PYTHONPATH := $(CURDIR)/src
GAMES := chrono_breach sigil_deck abyss_signal trace_blade dice_relic loop_ten
SAMPLES := hello counter io_demo key_display multi pcg_clock pcg_animation sound_demo maze relic_dive

.PHONY: samples games test games-test clean

samples:
	@for sample in $(SAMPLES); do \
		$(MAKE) -C samples/$$sample || exit $$?; \
	done

games:
	@for game in $(GAMES); do $(MAKE) -C games/$$game || exit $$?; done

games-test:
	@for game in $(GAMES); do $(MAKE) -C games/$$game test || exit $$?; done

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest tests

clean:
	@for sample in $(SAMPLES); do \
		$(MAKE) -C samples/$$sample clean || exit $$?; \
	done
