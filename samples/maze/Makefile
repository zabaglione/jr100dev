include ../toolchain.mk
STD_DIR := ../../src/jr100dev/std

ASM := src/main.asm src/maze_data.asm src/maze_gen.asm
OBJ := $(patsubst src/%.asm,build/%.json,$(ASM))
COMMON_INC := src/common.inc
GEN_INC := $(COMMON_INC) src/maze_helpers.inc $(STD_DIR)/macro.inc $(STD_DIR)/ctl.inc $(STD_DIR)/scroll.inc

all: build/maze.prg

build/maze.prg: $(OBJ) | build
	$(JR100DEV) link $(OBJ) -o $@ --bin build/maze.bin --map build/maze.map --bss-base 0x3000

build/%.json: src/%.asm | build
	$(JR100DEV) assemble $< --obj $@ --bin build/$*.bin --map build/$*.map -o build/$*.prg

build/maze_data.json: $(COMMON_INC)
build/maze_gen.json: $(GEN_INC)

build:
	mkdir -p $@

clean:
	rm -rf build

test:
	$(MAKE) -C tests check

.PHONY: all clean build test
