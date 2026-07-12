PYTHONPATH ?= $(abspath ../../..)
JR100DEV := PYTHONPATH=$(PYTHONPATH) python3 -m jr100dev.cli.main
PCG_EDITOR := ../../../tools/pcg_editor
PCG_DATA := src/pcg_data.inc

.PHONY: all clean

all: build/pcg_clock.prg

build/pcg_clock.prg: src/main.asm $(PCG_DATA) | build
	$(JR100DEV) assemble $< -o $@ --bin build/pcg_clock.bin --obj build/pcg_clock.json --map build/pcg_clock.map

$(PCG_DATA): $(PCG_EDITOR)/core.js $(PCG_EDITOR)/scripts/generate_clock_pcg.mjs
	node $(PCG_EDITOR)/scripts/generate_clock_pcg.mjs $@

build:
	mkdir -p $@

clean:
	rm -rf build $(PCG_DATA)
