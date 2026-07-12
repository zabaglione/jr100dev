"""Expression evaluation for the JR-100 assembler DSL."""
from __future__ import annotations

import math
from typing import Dict


class ExpressionError(RuntimeError):
    pass


_ESCAPE_MAP = {
    'n': '\n',
    'r': '\r',
    't': '\t',
    '0': '\0',
    '\\': '\\',
    "'": "'",
    '"': '"',
}


def evaluate(expr: str, symbols: Dict[str, int], location: str) -> int:
    translated = _translate(expr, location)
    try:
        value = eval(translated, {"__builtins__": {}}, symbols)
    except NameError as err:
        raise ExpressionError(f"Undefined symbol {err} at {location}") from err
    except ZeroDivisionError as err:
        raise ExpressionError(f"Division by zero at {location}") from err
    except Exception as err:
        raise ExpressionError(f"Invalid expression '{expr}' at {location}: {err}") from err
    if not isinstance(value, int):
        raise ExpressionError(f"Expression '{expr}' at {location} did not evaluate to integer")
    return value & 0xFFFF


def _translate(expr: str, location: str) -> str:
    result: list[str] = []
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch in ' \t':
            result.append(ch)
            i += 1
            continue
        if ch == '$':
            j = i + 1
            while j < len(expr) and expr[j].isalnum():
                j += 1
            if j == i + 1:
                raise ExpressionError(f"Invalid hex literal at {location}")
            digits = expr[i + 1:j]
            result.append(f"0x{digits}")
            i = j
            continue
        if ch == '%':
            j = i + 1
            while j < len(expr) and expr[j] in '01':
                j += 1
            if j == i + 1:
                raise ExpressionError(f"Invalid binary literal at {location}")
            digits = expr[i + 1:j]
            result.append(f"0b{digits}")
            i = j
            continue
        if ch == "'":
            literal, length = _parse_char(expr[i:], location)
            result.append(str(literal))
            i += length
            continue
        result.append(ch)
        i += 1
    return ''.join(result)


def _parse_char(fragment: str, location: str) -> tuple[int, int]:
    if len(fragment) < 2 or fragment[0] != "'":
        raise ExpressionError(f"Invalid char literal at {location}")
    if len(fragment) >= 4 and fragment[1] == '\\':
        escape = fragment[2]
        if escape not in _ESCAPE_MAP:
            raise ExpressionError(f"Unsupported escape '\\{escape}' at {location}")
        closing = fragment[3] if len(fragment) > 3 else ''
        if closing != "'":
            raise ExpressionError(f"Unterminated char literal at {location}")
        value = ord(_ESCAPE_MAP[escape])
        return value, 4
    if len(fragment) < 3 or fragment[2] != "'":
        raise ExpressionError(f"Unterminated char literal at {location}")
    value = ord(fragment[1])
    return value, 3
