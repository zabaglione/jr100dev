PYTHON ?= python3
PYTHONPATH := $(CURDIR)/src
SAMPLES := hello counter io_demo key_display multi pcg_clock pcg_animation maze

.PHONY: samples test clean

samples:
	@for sample in $(SAMPLES); do \
		$(MAKE) -C samples/$$sample || exit $$?; \
	done

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest tests

clean:
	@for sample in $(SAMPLES); do \
		$(MAKE) -C samples/$$sample clean || exit $$?; \
	done
