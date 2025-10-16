PYTHONPATH ?= $(abspath ../../..)
JR100DEV := PYTHONPATH=$(PYTHONPATH) python -m jr100dev.cli.main

ASM := src/main.asm src/maze_data.asm src/maze_gen.asm
OBJ := $(patsubst src/%.asm,build/%.json,$(ASM))
COMMON_INC := src/common.inc
GEN_INC := $(COMMON_INC) src/maze_helpers.inc

build/maze.prg: $(OBJ) | build
	$(JR100DEV) link $(OBJ) -o $@ --bin build/maze.bin --map build/maze.map --bss-base $$3000

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

.PHONY: clean build test
