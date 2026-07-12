include $(dir $(lastword $(MAKEFILE_LIST)))toolchain.mk

.PHONY: all clean

all: build/$(TARGET).prg

build/$(TARGET).prg: main.asm | build
	$(JR100DEV) assemble $< --obj build/$(TARGET).json --bin build/$(TARGET).bin --map build/$(TARGET).map -o $@

build:
	mkdir -p $@

clean:
	rm -rf build
