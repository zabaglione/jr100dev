PYTHONPATH ?= $(abspath ../../../../)
JR100DEV := PYTHONPATH=$(PYTHONPATH) python -m jr100dev.cli.main

TARGETS := maze_init_test maze_step_test maze_stack_test maze_neighbors_test maze_wall_mark_test maze_carve_test maze_scroll_test
BUILD_DIR := build

$(BUILD_DIR)/%.prg: %.asm | $(BUILD_DIR)
	$(JR100DEV) assemble $< -o $@ --bin $(BUILD_DIR)/$*.bin --obj $(BUILD_DIR)/$*.json --map $(BUILD_DIR)/$*.map

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

.PHONY: clean all check
all: $(addprefix $(BUILD_DIR)/,$(addsuffix .prg,$(TARGETS)))

check: all
	PYTHONPATH=$(PYTHONPATH) python run_debug_checks.py

clean:
	rm -rf $(BUILD_DIR)
