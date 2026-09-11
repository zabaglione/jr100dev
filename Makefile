PYTHON ?= python3
PYTHONPATH := $(CURDIR)/src
GAMES := $(shell $(PYTHON) -c 'import json; print(" ".join(json.load(open("games/collection.json"))["games"]))')
SAMPLES := hello counter io_demo key_display multi pcg_clock pcg_animation sound_demo maze

.PHONY: samples games test games-test clean

samples:
	@for sample in $(SAMPLES); do \
		$(MAKE) -C samples/$$sample || exit $$?; \
	done

games:
	@for game in $(GAMES); do $(MAKE) -C games/$$game || exit $$?; done

games-test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) games/native/check_compiler.py
	@for game in $(GAMES); do $(MAKE) -C games/$$game test || exit $$?; done
	$(PYTHON) games/tests/check_motion.py
	$(PYTHON) games/tests/check_feedback.py

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest tests

clean:
	@for sample in $(SAMPLES); do \
		$(MAKE) -C samples/$$sample clean || exit $$?; \
	done
