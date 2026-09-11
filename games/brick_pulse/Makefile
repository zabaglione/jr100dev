include ../toolchain.mk

test: held-test feature-test

feature-test: all
	$(PYTHON) check_features.py

held-test: all
	$(PYTHON) check_held.py

.PHONY: held-test feature-test
