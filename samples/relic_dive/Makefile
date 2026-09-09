include ../toolchain.mk
MODULES := constants.inc platform.asm main.asm map.asm terrain.asm dungeon.asm sight_rays.inc turns.asm items.asm extras.asm ui.asm assets.asm
SOURCES := $(addprefix src/,$(MODULES))

all: build/relic_dive.prg images

build/game.asm: $(SOURCES) | build
	$(PYTHON) build_source.py

build/relic_dive.prg: build/game.asm
	$(JR100DEV) assemble $< -o $@ --bin build/relic_dive.bin --map build/relic_dive.map
	$(PYTHON) check_layout.py

build:
	mkdir -p $@

test: all
	$(PYTHON) tests/check_game.py
	$(PYTHON) tests/replay_game.py

images: build/relic_dive.prg make_manual_images.py
	$(PYTHON) make_manual_images.py

clean:
	rm -rf build

.PHONY: all test clean images
