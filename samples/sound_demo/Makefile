include ../toolchain.mk

.PHONY: all clean

all: build/sound_demo.prg

build/sound_demo.prg: src/main.asm src/sound_assets.inc | build
	$(JR100DEV) assemble $< -o $@ --bin build/sound_demo.bin --obj build/sound_demo.json --map build/sound_demo.map

build:
	mkdir -p $@

clean:
	rm -rf build
