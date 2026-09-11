REPO_ROOT := $(abspath ../..)
PYTHON ?= $(if $(wildcard $(REPO_ROOT)/.venv/bin/python),$(REPO_ROOT)/.venv/bin/python,python3)
export PYTHONPATH := $(REPO_ROOT)/src
JR100DEV ?= $(PYTHON) -m jr100dev.cli.main
MODULES := constants.inc platform.asm main.asm map.asm terrain.asm dungeon.asm sight_rays.inc turns.asm items.asm extras.asm ui.asm assets.asm
SOURCES := $(addprefix src/,$(MODULES))

all: build/relic-dive.prg images

build/game.asm: $(SOURCES) build_source.py pack_text.py title_art.py ../native/artwork.py ../common/art.py ../common/title_styles.py text.json | build
	$(PYTHON) build_source.py

build/relic-dive.prg: build/game.asm
	$(JR100DEV) assemble $< -o $@ --bin build/relic-dive.bin --map build/relic-dive.map
	$(PYTHON) check_layout.py

build:
	mkdir -p $@

test: all
	$(PYTHON) tests/check_game.py
	$(PYTHON) tests/replay_game.py

images: build/relic-dive.prg make_manual_images.py
	$(PYTHON) make_manual_images.py

clean:
	rm -rf build

.PHONY: all test clean images
