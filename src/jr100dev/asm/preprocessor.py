"""Preprocessing utilities for `.include` と簡易マクロ展開."""
from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence


class PreprocessError(RuntimeError):
    pass


@dataclass
class MacroDefinition:
    name: str
    params: List[str]
    lines: List[str]
    defined_at: str


_ARG_PATTERN = re.compile(r"\\([0-9@])")


def preprocess_source(
    source: str,
    *,
    filename: str,
    include_dirs: Sequence[pathlib.Path],
) -> str:
    path = pathlib.Path(filename) if filename else None
    macros: Dict[str, MacroDefinition] = {}
    counters: Dict[str, int] = {}
    include_stack: List[pathlib.Path] = []
    lines = _process_lines(
        source.splitlines(),
        current_file=path,
        macros=macros,
        counters=counters,
        include_dirs=include_dirs,
        include_stack=include_stack,
    )
    return "\n".join(lines) + ("\n" if lines and lines[-1] else "")


def _process_lines(
    lines: Iterable[str],
    *,
    current_file: pathlib.Path | None,
    macros: Dict[str, MacroDefinition],
    counters: Dict[str, int],
    include_dirs: Sequence[pathlib.Path],
    include_stack: List[pathlib.Path],
) -> List[str]:
    output: List[str] = []
    iterator = iter(enumerate(lines, start=1))
    for line_no, raw_line in iterator:
        code, comment = _split_comment(raw_line)
        if not code.strip():
            output.append(raw_line.rstrip())
            continue

        label, statement = _split_label(code)
        if not statement:
            output.append(raw_line.rstrip())
            continue

        op, operand = _split_op(statement)

        if op.upper() == "MACRO":
            if label:
                raise PreprocessError(_format_location(current_file, line_no, "MACRO 行にラベルは使用できません"))
            definition = _consume_macro(
                op_line=(line_no, operand or ""),
                iterator=iterator,
                current_file=current_file,
            )
            if definition.name in macros:
                raise PreprocessError(
                    _format_location(current_file, line_no, f"マクロ {definition.name} は既に定義されています")
                )
            macros[definition.name] = definition
            continue

        if op.startswith("."):
            directive = op.lower()
            if directive == ".include":
                if operand is None:
                    raise PreprocessError(_format_location(current_file, line_no, ".include にはパスが必要です"))
                include_path = _parse_include_path(operand)
                resolved = _resolve_include(include_path, current_file, include_dirs)
                if resolved in include_stack:
                    chain = " -> ".join(str(item) for item in include_stack + [resolved])
                    raise PreprocessError(_format_location(current_file, line_no, f".include の再帰参照: {chain}"))
                include_stack.append(resolved)
                included_source = resolved.read_text(encoding="utf-8")
                included_lines = _process_lines(
                    included_source.splitlines(),
                    current_file=resolved,
                    macros=macros,
                    counters=counters,
                    include_dirs=include_dirs,
                    include_stack=include_stack,
                )
                output.extend(included_lines)
                include_stack.pop()
                if comment:
                    output.append(f";{comment}")
                continue

            output.append(_recompose_line(label, statement, comment))
            continue

        macro = macros.get(op.upper())
        if macro:
            args = _split_operands(operand) if operand is not None else []
            if len(args) != len(macro.params):
                expected = len(macro.params)
                raise PreprocessError(
                    _format_location(
                        current_file,
                        line_no,
                        f"マクロ {macro.name} の引数数が一致しません (期待 {expected} / 実際 {len(args)})",
                    )
                )
            counters[macro.name] = counters.get(macro.name, 0) + 1
            unique = f"__{macro.name}_{counters[macro.name]:04d}"
            expanded = _expand_macro(macro, args, unique)
            expanded = _apply_invocation_label(label, expanded)
            output.extend(expanded)
            if comment:
                output.append(f";{comment}")
            continue

        output.append(_recompose_line(label, statement, comment))
    return output


def _consume_macro(op_line: tuple[int, str], iterator, current_file: pathlib.Path | None) -> MacroDefinition:
    line_no, operand_text = op_line
    tokens = operand_text.strip().split(None, 1) if operand_text else []
    if not tokens:
        raise PreprocessError(_format_location(current_file, line_no, "MACRO 名が指定されていません"))
    name = tokens[0].upper()
    param_text = tokens[1] if len(tokens) > 1 else ""
    if param_text:
        raw_params = [segment for segment in param_text.replace(',', ' ').split() if segment]
        params = [param.upper() for param in raw_params]
    else:
        params = []
    body: List[str] = []
    for next_line_no, raw_line in iterator:
        code, comment = _split_comment(raw_line)
        stripped = code.strip()
        if stripped.upper() == "ENDM":
            if comment:
                body.append(f";{comment}")
            break
        body.append(raw_line.rstrip())
    else:
        raise PreprocessError(_format_location(current_file, line_no, f"マクロ {name} は ENDM で閉じられていません"))
    return MacroDefinition(name=name, params=params, lines=body, defined_at=_format_file(current_file, line_no))


def _expand_macro(definition: MacroDefinition, args: Sequence[str], unique: str) -> List[str]:
    expanded: List[str] = []
    for raw_line in definition.lines:
        if not raw_line:
            expanded.append(raw_line)
            continue
        code, comment = _split_comment(raw_line)
        replaced = _replace_arguments(code, definition.params, args, unique)
        if comment:
            replaced = _recompose_line(None, replaced, comment)
        expanded.append(replaced.rstrip())
    return expanded


def _apply_invocation_label(label: str | None, lines: List[str]) -> List[str]:
    if not label:
        return lines
    for index, text in enumerate(lines):
        stripped = text.strip()
        if not stripped or stripped.startswith(";"):
            continue
        lines[index] = f"{label}: {stripped}"
        break
    else:
        lines.append(f"{label}:")
    return lines


def _replace_arguments(code: str, params: List[str], args: Sequence[str], unique: str) -> str:
    def _substitute(match: re.Match[str]) -> str:
        token = match.group(1)
        if token == "@":
            return unique
        if token.isdigit():
            index = int(token) - 1
            if index < 0 or index >= len(args):
                return match.group(0)
            return args[index]
        return match.group(0)

    replaced = _ARG_PATTERN.sub(_substitute, code)
    for name, value in zip(params, args):
        replaced = replaced.replace(f"\\{name}", value)
    return replaced


def _split_comment(line: str) -> tuple[str, str]:
    if ";" not in line:
        return line, ""
    code, comment = line.split(";", 1)
    return code.rstrip(), comment.strip()


def _split_label(code: str) -> tuple[str | None, str]:
    if ":" not in code:
        return None, code.strip()
    label_part, rest = code.split(":", 1)
    label = label_part.strip()
    return (label.upper(), rest.strip())


def _split_op(statement: str) -> tuple[str, str | None]:
    parts = statement.strip().split(None, 1)
    if not parts:
        return "", None
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1]


def _split_operands(operand: str) -> List[str]:
    values: List[str] = []
    current: List[str] = []
    in_string = False
    in_char = False
    escaped = False
    for ch in operand:
        if in_string:
            current.append(ch)
            if escaped:
                escaped = False
                continue
            if ch == "\\":
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
            if ch == "\\":
                escaped = True
                continue
            if ch == "'":
                in_char = False
            continue
        if ch == '"':
            in_string = True
            current.append(ch)
            continue
        if ch == "'":
            in_char = True
            current.append(ch)
            continue
        if ch == ",":
            value = "".join(current).strip()
            if value:
                values.append(value)
            current = []
            continue
        current.append(ch)
    value = "".join(current).strip()
    if value:
        values.append(value)
    return values


def _recompose_line(label: str | None, statement: str, comment: str) -> str:
    prefix = f"{label}: " if label else ""
    suffix = f" ;{comment}" if comment else ""
    return f"{prefix}{statement.strip()}{suffix}".rstrip()


def _parse_include_path(token: str) -> str:
    token = token.strip()
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1]
    if token.startswith("'") and token.endswith("'"):
        return token[1:-1]
    return token


def _resolve_include(path_str: str, current_file: pathlib.Path | None, include_dirs: Sequence[pathlib.Path]) -> pathlib.Path:
    candidate = pathlib.Path(path_str)
    search_paths: List[pathlib.Path] = []
    if current_file is not None and current_file.parent:
        search_paths.append(current_file.parent)
    search_paths.extend(include_dirs)
    if candidate.is_absolute():
        return candidate
    for base in search_paths:
        resolved = (base / candidate).resolve()
        if resolved.exists():
            return resolved
    raise PreprocessError(f"Include ファイルが見つかりません: {path_str}")


def _format_location(current_file: pathlib.Path | None, line_no: int, message: str) -> str:
    return f"{_format_file(current_file, line_no)}: {message}"


def _format_file(current_file: pathlib.Path | None, line_no: int) -> str:
    if current_file is None:
        return f"<input>:{line_no}"
    return f"{current_file}:{line_no}"
