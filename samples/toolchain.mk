SAMPLES_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
REPO_ROOT := $(abspath $(SAMPLES_DIR)/..)
PYTHONPATH ?= $(REPO_ROOT)/src
PYTHON ?= $(if $(wildcard $(REPO_ROOT)/.venv/bin/python),$(REPO_ROOT)/.venv/bin/python,python3)
JR100DEV ?= PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m jr100dev.cli.main
