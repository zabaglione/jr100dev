"""Opcode synchronization tool for JR-100 MB8861H CPU."""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class OpcodeEntry:
    mnemonic: str
    addressing: str
    opcode: int
    size: int


def load_cpu_spec(emulator_root: pathlib.Path) -> List[OpcodeEntry]:
    """Extract opcode data from the pyjr100emu source tree."""
    cpu_path = emulator_root / "src" / "jr100emu" / "cpu" / "cpu.py"
    if not cpu_path.exists():
        raise FileNotFoundError(f"cpu.py not found: {cpu_path}")

    source = cpu_path.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(cpu_path))

    collector = _OpcodeCollector()
    collector.visit(module)

    entries: List[OpcodeEntry] = []
    for name, opcode in collector.constants.items():
        mnemonic, raw_mode = _split_opcode_name(name)
        addressing = _ADDRESSING_MAP.get(raw_mode)
        if addressing is None:
            raise ValueError(f"Unknown addressing mode suffix {raw_mode!r} in {name}")

        handler_name = collector.handlers.get(name)
        size = collector.operand_sizes.get(handler_name) if handler_name else None
        if size is None:
            size = _fallback_size(addressing)

        entries.append(
            OpcodeEntry(
                mnemonic=mnemonic,
                addressing=addressing,
                opcode=opcode,
                size=size,
            )
        )

    entries.sort(key=lambda entry: entry.opcode)
    return entries


def emit_python(entries: Iterable[OpcodeEntry], target: pathlib.Path) -> None:
    """Write the synchronized opcode table as a Python module."""
    rows = list(entries)
    lines: List[str] = []
    lines.append('"""Auto-generated MB8861H opcode table. Do not edit manually."""')
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("OPCODES = [")
    for entry in rows:
        lines.append(
            f"    {{'mnemonic': {entry.mnemonic!r}, 'addressing': {entry.addressing!r}, "
            f"'opcode': 0x{entry.opcode:02X}, 'size': {entry.size}}},"
        )
    lines.append("]")
    lines.append("")
    target.write_text("\n".join(lines), encoding="utf-8")


def emit_manifest(entries: Iterable[OpcodeEntry], target: pathlib.Path) -> None:
    """Write the opcode manifest as JSON for debugging."""
    payload = [
        {
            "mnemonic": entry.mnemonic,
            "addressing": entry.addressing,
            "opcode": entry.opcode,
            "size": entry.size,
        }
        for entry in entries
    ]
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synchronize opcode tables with pyjr100emu")
    parser.add_argument(
        "--emu-root",
        type=pathlib.Path,
        required=True,
        help="Path to the pyjr100emu source tree",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("jr100dev/asm/opcodes_mb8861h.py"),
        help="Target Python module path",
    )
    parser.add_argument(
        "--json",
        type=pathlib.Path,
        help="Optional path to emit JSON manifest",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    entries = load_cpu_spec(args.emu_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    emit_python(entries, args.output)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        emit_manifest(entries, args.json)
    return 0


class _OpcodeCollector(ast.NodeVisitor):
    """AST visitor that extracts opcode metadata from MB8861."""

    TARGET_CLASS = "MB8861"

    def __init__(self) -> None:
        self.constants: Dict[str, int] = {}
        self.handlers: Dict[str, str] = {}
        self.operand_sizes: Dict[str, int] = {}
        self._current_class: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        previous = self._current_class
        self._current_class = node.name
        try:
            if node.name == self.TARGET_CLASS:
                self._collect_class(node)
        finally:
            self._current_class = previous

    def _collect_class(self, node: ast.ClassDef) -> None:
        function_map: Dict[str, ast.FunctionDef] = {}
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                self._collect_constant(stmt)
            elif isinstance(stmt, ast.FunctionDef):
                function_map[stmt.name] = stmt
        init_table = function_map.get("_init_opcode_table")
        if init_table is not None:
            self._collect_registrations(init_table)
        for name, func in function_map.items():
            self.operand_sizes[name] = _estimate_operand_size(func)

    def _collect_constant(self, stmt: ast.Assign) -> None:
        if not stmt.targets:
            return
        target = stmt.targets[0]
        if isinstance(target, ast.Name) and target.id.startswith("OP_"):
            value = ast.literal_eval(stmt.value)
            if not isinstance(value, int):
                raise TypeError(f"Opcode value must be integer: {target.id}")
            self.constants[target.id] = value & 0xFF

    def _collect_registrations(self, func: ast.FunctionDef) -> None:
        for node in ast.walk(func):
            if isinstance(node, ast.Call):
                attr = node.func
                if not isinstance(attr, ast.Attribute):
                    continue
                if not (isinstance(attr.value, ast.Name) and attr.value.id == "self"):
                    continue
                if attr.attr != "_register_opcode":
                    continue
                if len(node.args) < 2:
                    continue
                opcode_arg = node.args[0]
                handler_arg = node.args[1]
                if not isinstance(opcode_arg, ast.Attribute):
                    continue
                if not isinstance(handler_arg, ast.Attribute):
                    continue
                if not (
                    isinstance(opcode_arg.value, ast.Name)
                    and opcode_arg.value.id == "self"
                    and isinstance(handler_arg.value, ast.Name)
                    and handler_arg.value.id == "self"
                ):
                    continue
                opcode_name = opcode_arg.attr
                handler_name = handler_arg.attr
                self.handlers[opcode_name] = handler_name


def _split_opcode_name(name: str) -> Tuple[str, str]:
    body = name.removeprefix("OP_")
    parts = body.split("_")
    if len(parts) < 2:
        raise ValueError(f"Unexpected opcode constant name: {name}")
    mnemonic = "_".join(parts[:-1])
    mode = parts[-1]
    return mnemonic, mode


def _fallback_size(addressing: str) -> int:
    if addressing == "INH":
        return 1
    if addressing in {"IMM", "DIR", "IDX"}:
        return 2
    if addressing == "EXT":
        return 3
    if addressing == "REL":
        return 2
    raise ValueError(f"No fallback length for addressing mode {addressing}")


def _estimate_operand_size(func: ast.FunctionDef) -> int:
    count8 = 0
    count16 = 0
    for node in ast.walk(func):
        if not isinstance(node, ast.Call):
            continue
        attr = node.func
        if not isinstance(attr, ast.Attribute):
            continue
        if not isinstance(attr.value, ast.Name) or attr.value.id != "self":
            continue
        if attr.attr == "_fetch_operand8":
            count8 += 1
        elif attr.attr == "_fetch_operand16":
            count16 += 1
    return 1 + count8 + (count16 * 2)


_ADDRESSING_MAP = {
    "IMP": "INH",
    "IMM": "IMM",
    "DIR": "DIR",
    "IND": "IDX",
    "EXT": "EXT",
    "REL": "REL",
}


if __name__ == "__main__":
    raise SystemExit(main())
