SAMPLES_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
REPO_ROOT := $(abspath $(SAMPLES_DIR)/..)
PYTHONPATH ?= $(REPO_ROOT)/src
JR100DEV := PYTHONPATH=$(PYTHONPATH) python3 -m jr100dev.cli.main
