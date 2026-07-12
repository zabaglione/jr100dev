include ../toolchain.mk

SRC := src/main.asm src/message.asm
OBJ := $(patsubst src/%.asm,build/%.json,$(SRC))

.PHONY: all clean

all: build/multi.prg

build/multi.prg: $(OBJ) | build
	$(JR100DEV) link $(OBJ) -o $@ --bin build/multi.bin --map build/multi.map --entry 0x0300 --data-base 0x0500 --bss-base 0x0600

build/%.json: src/%.asm | build
	$(JR100DEV) assemble $< --obj $@ --bin build/$*.bin --map build/$*.map -o build/$*.prg

build:
	mkdir -p $@

clean:
	rm -rf build
