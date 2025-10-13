"""Command-line interface for the jr100dev toolchain."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Iterable


from ..asm.encoder import Assembler, AssemblyError
from ..asm.encoder import LineEmission
from ..link import LinkError, ObjectFormatError, link_objects, load_object, pack_prg
from ..proj import ProjectGenerationError, create_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jr100dev", description="JR-100 development utilities")
    sub = parser.add_subparsers(dest="command")

    assemble = sub.add_parser("assemble", help="Assemble a DSL source file")
    assemble.add_argument("source", type=pathlib.Path, help="Path to the source file")
    assemble.add_argument("-o", "--output", type=pathlib.Path, required=True, help="PRG output path")
    assemble.add_argument("--bin", type=pathlib.Path, help="Raw binary output path")
    assemble.add_argument("--obj", type=pathlib.Path, help="Intermediate object (JSON) output path")
    assemble.add_argument("--map", type=pathlib.Path, help="Symbol map output path")
    assemble.add_argument("--lst", type=pathlib.Path, help="Listing file output path")
    assemble.add_argument("--entry", type=lambda v: int(v, 0), help="Entry address override")
    assemble.add_argument("--name", type=str, help="Program name stored in the PROG header")
    assemble.add_argument("--comment", type=str, help="Optional program comment")

    link_cmd = sub.add_parser("link", help="Link JSON objects into a JR-100 binary")
    link_cmd.add_argument("objects", type=pathlib.Path, nargs="+", help="Object files to link")
    link_cmd.add_argument("-o", "--output", type=pathlib.Path, required=True, help="PRG output path")
    link_cmd.add_argument("--bin", type=pathlib.Path, help="Raw binary output path")
    link_cmd.add_argument("--map", type=pathlib.Path, help="Symbol map output path")
    link_cmd.add_argument("--entry", type=lambda v: int(v, 0), help="Entry address override")
    link_cmd.add_argument("--name", type=str, help="Program name stored in the PROG header")
    link_cmd.add_argument("--comment", type=str, help="Optional program comment")
    link_cmd.add_argument("--text-base", type=lambda v: int(v, 0), help="Override code section base address")
    link_cmd.add_argument("--data-base", type=lambda v: int(v, 0), help="Override data section base address")
    link_cmd.add_argument("--bss-base", type=lambda v: int(v, 0), help="Override bss section base address")

    new_cmd = sub.add_parser("new", help="Create a new JR-100 project skeleton")
    new_cmd.add_argument("path", type=pathlib.Path, help="Directory to create the project in")
    new_cmd.add_argument("--force", action="store_true", help="Overwrite existing files if present")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "assemble":
        return run_assemble(args)
    if args.command == "link":
        return run_link(args)
    if args.command == "new":
        return run_new(args)
    parser.error(f"Unknown command {args.command}")
    return 1


def run_assemble(args: argparse.Namespace) -> int:
    source_path: pathlib.Path = args.source
    if not source_path.exists():
        print(f"Source file not found: {source_path}", file=sys.stderr)
        return 1
    source_text = source_path.read_text(encoding="utf-8")
    assembler = Assembler(source_text, filename=str(source_path))
    try:
        result = assembler.assemble()
    except AssemblyError as err:
        print(f"Assembly failed: {err}", file=sys.stderr)
        return 1

    entry_point = args.entry if args.entry is not None else result.entry_point
    program_name = (args.name or source_path.stem).upper()[:32]
    comment = args.comment or ""

    bin_path: pathlib.Path
    if args.bin:
        bin_path = args.bin
    else:
        bin_path = args.output.with_suffix(".bin")
    bin_path.parent.mkdir(parents=True, exist_ok=True)
    bin_path.write_bytes(result.machine_code)

    prg_bytes = pack_prg(
        result.origin,
        result.machine_code,
        entry_point,
        program_name=program_name,
        comment=comment,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(prg_bytes)

    if args.obj:
        args.obj.parent.mkdir(parents=True, exist_ok=True)
        obj_payload = result.to_object_dict()
        args.obj.write_text(json.dumps(obj_payload, indent=2), encoding="utf-8")

    if args.map:
        args.map.parent.mkdir(parents=True, exist_ok=True)
        _write_map(args.map, result.symbols.items())
    if args.lst:
        args.lst.parent.mkdir(parents=True, exist_ok=True)
        _write_listing(args.lst, result.emissions)

    return 0


def run_link(args: argparse.Namespace) -> int:
    try:
        objects = [load_object(path) for path in args.objects]
    except ObjectFormatError as err:
        print(f"Failed to read object: {err}", file=sys.stderr)
        return 1

    try:
        result = link_objects(
            objects,
            entry_override=args.entry,
            text_base=getattr(args, "text_base", None),
            data_base=getattr(args, "data_base", None),
            bss_base=getattr(args, "bss_base", None),
        )
    except LinkError as err:
        print(f"Link failed: {err}", file=sys.stderr)
        return 1

    bin_path: pathlib.Path
    if args.bin:
        bin_path = args.bin
    else:
        bin_path = args.output.with_suffix(".bin")
    bin_path.parent.mkdir(parents=True, exist_ok=True)
    bin_path.write_bytes(result.image)

    program_name = (args.name or args.output.stem).upper()[:32]
    comment = args.comment or ""
    segment_payloads = [(segment.address, segment.data) for segment in result.segments] or None
    prg_bytes = pack_prg(
        result.origin,
        result.image,
        result.entry_point,
        program_name=program_name,
        comment=comment,
        segments=segment_payloads,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(prg_bytes)

    if args.map:
        args.map.parent.mkdir(parents=True, exist_ok=True)
        _write_map(args.map, result.symbols.items())

    return 0


def run_new(args: argparse.Namespace) -> int:
    target: pathlib.Path = args.path
    try:
        result = create_project(target, force=args.force)
    except ProjectGenerationError as err:
        print(f"Project generation failed: {err}", file=sys.stderr)
        return 1

    print(f"Created project at {result.root}")
    print("Generated files:")
    for path in result.created:
        rel = path.relative_to(result.root)
        print(f"  {rel}")
    print()
    print("Next steps:")
    print("  1. cd" , result.root)
    print("  2. jr100dev assemble src/main.asm -o build/main.prg")
    return 0


def _write_map(path: pathlib.Path, symbols: Iterable[tuple[str, int]]) -> None:
    lines = [f"{name} = ${value:04X}" for name, value in symbols]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_listing(path: pathlib.Path, emissions: Iterable[LineEmission]) -> None:
    rows = []
    for emission in emissions:
        if emission.address is None:
            rows.append(f"{emission.line.line_no:04} ....    {emission.line.text.rstrip()}")
            continue
        bytes_repr = ' '.join(f"{byte:02X}" for byte in emission.data)
        rows.append(
            f"{emission.line.line_no:04} {emission.address:04X}  {bytes_repr:<12} {emission.line.text.rstrip()}"
        )
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
