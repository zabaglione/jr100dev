REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
PYTHON ?= $(if $(wildcard $(REPO_ROOT)/.venv/bin/python),$(REPO_ROOT)/.venv/bin/python,python3)
export PYTHONPATH := $(REPO_ROOT)/src

all:
	$(PYTHON) ../build_game.py .

test: all
	$(PYTHON) ../tests/verify_game.py .

.PHONY: all test
