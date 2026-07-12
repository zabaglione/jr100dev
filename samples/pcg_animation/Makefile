include ../toolchain.mk

.PHONY: all clean

all: build/pcg_animation.prg

build/pcg_animation.prg: src/main.asm src/player_frames.inc | build
	$(JR100DEV) assemble $< -o $@ --bin build/pcg_animation.bin --obj build/pcg_animation.json --map build/pcg_animation.map

build:
	mkdir -p $@

clean:
	rm -rf build
