PYTHONPATH ?= $(PWD)/../../
JR100DEV := PYTHONPATH=$(PYTHONPATH) jr100dev

ASM := src/main.asm src/rng.asm src/maze_data.asm src/maze_gen.asm
OBJ := $(ASM:.asm=.json)

build/maze.prg: $(OBJ)
	$(JR100DEV) link $(OBJ) -o $@ --bin build/maze.bin --map build/maze.map

src/%.json: src/%.asm
	$(JR100DEV) assemble $< --obj $@ --bin build/$*.bin --map build/$*.map -o build/$*.prg

build:
	mkdir -p $@

clean:
	rm -rf build

.PHONY: clean build
