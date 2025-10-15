"""Lightweight line parser for the JR-100 assembler DSL."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


class ParserError(RuntimeError):
    pass


@dataclass
class ParsedLine:
    line_no: int
    text: str
    label: Optional[str]
    op: str
    operands: List[str]
    is_directive: bool


def parse_source(source: str) -> List[ParsedLine]:
    lines: List[ParsedLine] = []
    for idx, raw in enumerate(source.splitlines(), start=1):
        text = raw.split(';', 1)[0].strip()
        if not text:
            continue
        label: Optional[str] = None
        rest = text
        if ':' in text:
            label_part, rest_part = text.split(':', 1)
            if not label_part.strip():
                raise ParserError(f"Empty label at line {idx}")
            label = label_part.strip().upper()
            rest = rest_part.strip()
            if not rest:
                lines.append(
                    ParsedLine(
                        line_no=idx,
                        text=raw.rstrip(),
                        label=label,
                        op='.label',
                        operands=[],
                        is_directive=True,
                    )
                )
                continue
        if not rest:
            raise ParserError(f"Missing statement after label at line {idx}")
        if rest.startswith('.'):
            op, operand_str = _split_op_operands(rest)
            directive = op.lower()
            operands = _split_operands(operand_str) if operand_str is not None else []
            lines.append(
                ParsedLine(
                    line_no=idx,
                    text=raw.rstrip(),
                    label=label,
                    op=directive,
                    operands=operands,
                    is_directive=True,
                )
            )
            continue
        op, operand_str = _split_op_operands(rest)
        mnemonic = op.upper()
        operands = _split_operands(operand_str) if operand_str is not None else []
        lines.append(
            ParsedLine(
                line_no=idx,
                text=raw.rstrip(),
                label=label,
                op=mnemonic,
                operands=operands,
                is_directive=False,
            )
        )
    return lines


def _split_op_operands(statement: str) -> tuple[str, Optional[str]]:
    parts = statement.strip().split(None, 1)
    if not parts:
        raise ParserError("Empty statement")
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1].strip()


def _split_operands(operand_str: str) -> List[str]:
    values: List[str] = []
    current: List[str] = []
    in_string = False
    in_char = False
    escaped = False
    for ch in operand_str:
        if in_string:
            current.append(ch)
            if escaped:
                escaped = False
                continue
            if ch == '\\':
                escaped = True
                continue
            if ch == '"':
                in_string = False
            continue
        if in_char:
            current.append(ch)
            if escaped:
                escaped = False
                continue
            if ch == '\\':
                escaped = True
                continue
            if ch == '\'':
                in_char = False
            continue
        if ch == '"':
            in_string = True
            current.append(ch)
            continue
        if ch == '\'':
            in_char = True
            current.append(ch)
            continue
        if ch == ',':
            values.append(''.join(current).strip())
            current = []
            continue
        current.append(ch)
    if current:
        values.append(''.join(current).strip())
    cleaned = [value for value in values if value]
    return cleaned
