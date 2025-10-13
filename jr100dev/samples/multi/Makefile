PYTHONPATH ?= $(PWD)/../../
JR100DEV := PYTHONPATH=$(PYTHONPATH) jr100dev

SRC := src/main.asm src/message.asm
OBJ := $(SRC:.asm=.json)

build/main.prg: $(OBJ)
	$(JR100DEV) link $(OBJ) -o $@ --bin build/main.bin --map build/main.map

src/%.json: src/%.asm
	$(JR100DEV) assemble $< --obj $@ --bin build/$*.bin --map build/$*.map -o build/$*.prg

clean:
	rm -rf build

.PHONY: clean
