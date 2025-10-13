"""Two-pass assembler implementation for JR-100."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from . import opcodes_mb8861h
from .eval import ExpressionError, evaluate
from .parser import ParsedLine, ParserError, parse_source


class AssemblyError(RuntimeError):
    pass


@dataclass
class OpcodeSpec:
    mnemonic: str
    addressing: str
    opcode: int
    size: int


@dataclass
class LineState:
    line: ParsedLine
    address: Optional[int]
    opcode: Optional[OpcodeSpec]
    operands: List[str]
    forced_mode: Optional[str] = None
    bss_size: int = 0


@dataclass
class AssemblyResult:
    origin: int
    entry_point: int
    machine_code: bytes
    symbols: Dict[str, int]
    emissions: List['LineEmission']
    sections: List['Section']
    source: str
    relocations: List['Relocation']
    bss_entries: List['BssAllocation']

    def to_object_dict(self) -> Dict[str, object]:
        section_payloads = []
        for section in self.sections:
            payload = {
                "name": section.name,
                "kind": section.kind,
                "address": section.address,
                "size": len(section.data) if section.kind != "bss" else section.bss_size,
                "content": ''.join(f"{byte:02X}" for byte in section.data) if section.data else "",
                "bss_size": section.bss_size,
            }
            section_payloads.append(payload)
        symbol_entries = [
            {"name": name, "value": value, "scope": "global"}
            for name, value in self.symbols.items()
        ]
        relocation_entries = [
            {
                "section": relocation.section,
                "offset": relocation.offset,
                "type": relocation.type,
                "target": relocation.target,
                "addend": relocation.addend,
            }
            for relocation in self.relocations
        ]

        return {
            "format": "jr100dev-object",
            "version": 1,
            "source": self.source,
            "origin": self.origin,
            "entry_point": self.entry_point,
            "sections": section_payloads,
            "symbols": symbol_entries,
            "relocations": relocation_entries,
        }


@dataclass
class LineEmission:
    line: ParsedLine
    address: Optional[int]
    data: List[int]


@dataclass
class Section:
    name: str
    kind: str
    address: int
    data: List[int]
    bss_size: int = 0


@dataclass
class Relocation:
    section: str
    offset: int
    type: str
    target: str
    addend: int = 0


@dataclass
class BssAllocation:
    name: str
    address: int
    size: int


class Assembler:
    def __init__(self, source: str, filename: str = "<stdin>") -> None:
        self.source = source
        self.filename = filename
        self.opcode_table = _build_opcode_table()

    def assemble(self) -> AssemblyResult:
        try:
            parsed_lines = parse_source(self.source)
        except ParserError as err:
            raise AssemblyError(str(err)) from err

        symbols: Dict[str, int] = {}
        states: List[LineState] = []
        origin: Optional[int] = None
        pc = 0

        for line in parsed_lines:
            state_bss_size = 0
            address = pc
            opcode_spec: Optional[OpcodeSpec] = None
            normalized_operands, forced_mode = _normalize_operands(line.operands)
            register_label = True
            if line.is_directive:
                directive = line.op
                if directive == '.org':
                    if origin is not None or states:
                        raise AssemblyError(_format_error(line, ".org may only appear once at the beginning"))
                    if not normalized_operands:
                        raise AssemblyError(_format_error(line, ".org requires an operand"))
                    value = self._eval(normalized_operands[0], symbols, line)
                    origin = value
                    pc = value
                    address = None
                    register_label = False
                elif directive == '.equ':
                    if line.label is None:
                        raise AssemblyError(_format_error(line, ".equ requires a label"))
                    if not normalized_operands:
                        raise AssemblyError(_format_error(line, ".equ requires an operand"))
                    value = self._eval(normalized_operands[0], symbols, line)
                    symbols[line.label] = value & 0xFFFF
                    address = None
                    register_label = False
                elif directive == '.res':
                    if origin is None:
                        raise AssemblyError(_format_error(line, ".org must appear before data"))
                    if not normalized_operands:
                        raise AssemblyError(_format_error(line, '.res requires a size operand'))
                    size = self._eval(normalized_operands[0], symbols, line)
                    if size < 0:
                        raise AssemblyError(_format_error(line, '.res size must be non-negative'))
                    address = pc
                    pc += size
                    normalized_operands = []
                    opcode_spec = None
                    state_bss_size = size
                elif directive in ('.byte', '.word', '.ascii', '.fill', '.align'):
                    if origin is None:
                        raise AssemblyError(_format_error(line, ".org must appear before data"))
                    address = pc
                    size = self._estimate_directive_size(directive, normalized_operands, symbols, line, pc)
                    pc += size
                else:
                    raise AssemblyError(_format_error(line, f"Unsupported directive {directive}"))
            else:
                if origin is None:
                    raise AssemblyError(_format_error(line, ".org must appear before code"))
                opcode_spec = self._match_opcode(line, normalized_operands, forced_mode, symbols)
                address = pc
                pc += opcode_spec.size
            if line.label and register_label:
                if line.label in symbols:
                    raise AssemblyError(_format_error(line, f"Duplicate symbol {line.label}"))
                if address is None:
                    symbols[line.label] = pc
                else:
                    symbols[line.label] = address & 0xFFFF
            state_operands = list(normalized_operands)
            states.append(
                LineState(
                    line=line,
                    address=address,
                    opcode=opcode_spec,
                    operands=state_operands,
                    forced_mode=forced_mode if not line.is_directive else None,
                    bss_size=state_bss_size,
                )
            )

        if origin is None:
            raise AssemblyError("Missing .org directive")

        self._refine_states(states, symbols, origin)
        machine, emissions, relocations, bss_entries = self._second_pass(states, symbols, origin)
        entry = origin
        ordered_symbols = dict(sorted(symbols.items()))
        sections = _build_sections(origin, machine, bss_entries)
        return AssemblyResult(
            origin=origin,
            entry_point=entry,
            machine_code=machine,
            symbols=ordered_symbols,
            emissions=emissions,
            sections=sections,
            source=self.filename,
            relocations=relocations,
            bss_entries=bss_entries,
        )

    def _eval(self, expr: str, symbols: Dict[str, int], line: ParsedLine) -> int:
        location = f"{self.filename}:{line.line_no}"
        try:
            return evaluate(expr, symbols, location)
        except ExpressionError as err:
            raise AssemblyError(str(err)) from err

    def _estimate_directive_size(
        self,
        directive: str,
        operands: List[str],
        symbols: Dict[str, int],
        line: ParsedLine,
        current_pc: int,
    ) -> int:
        if directive == '.byte':
            size = 0
            for operand in operands:
                if operand.startswith('"') and operand.endswith('"'):
                    data = _parse_string(operand, line)
                    size += len(data)
                else:
                    size += 1
            return size
        if directive == '.word':
            return 2 * len(operands)
        if directive == '.ascii':
            if len(operands) != 1:
                raise AssemblyError(_format_error(line, '.ascii requires a single string operand'))
            data = _parse_string(operands[0], line)
            return len(data)
        if directive == '.fill':
            if len(operands) not in (1, 2):
                raise AssemblyError(_format_error(line, '.fill requires count[, value]'))
            count = self._eval(operands[0], symbols, line)
            return count
        if directive == '.align':
            if len(operands) != 1:
                raise AssemblyError(_format_error(line, '.align requires a power-of-two argument'))
            boundary = self._eval(operands[0], symbols, line)
            if boundary <= 0:
                raise AssemblyError(_format_error(line, '.align argument must be positive'))
            try:
                padding = _alignment_padding(current_pc, boundary)
            except ValueError as err:
                raise AssemblyError(_format_error(line, str(err))) from err
            return padding
        raise AssemblyError(_format_error(line, f'Unsupported directive {directive}'))

    def _match_opcode(
        self,
        line: ParsedLine,
        operands: List[str],
        forced_mode: Optional[str],
        symbols: Dict[str, int],
    ) -> OpcodeSpec:
        mnemonic = line.op
        entries = self.opcode_table.get(mnemonic)
        if not entries:
            raise AssemblyError(_format_error(line, f"Unknown mnemonic {mnemonic}"))
        mode = self._select_addressing_mode(line, operands, forced_mode, entries, symbols)
        spec = entries.get(mode)
        if spec is None:
            available = ', '.join(entries.keys())
            raise AssemblyError(
                _format_error(line, f"Addressing mode {mode} not available for {mnemonic} (have {available})")
            )
        return spec

    def _refine_states(self, states: List[LineState], symbols: Dict[str, int], origin: int) -> None:
        max_iterations = 8
        for iteration in range(max_iterations):
            pc = origin
            changed = False
            for state in states:
                line = state.line
                if line.is_directive:
                    if line.op == '.org':
                        target = self._eval(state.operands[0], symbols, line)
                        if target != origin:
                            raise AssemblyError(
                                _format_error(
                                    line,
                                    ".org value must match initial origin in MVP",
                                )
                            )
                        pc = target
                        state.address = None
                    elif line.op == '.equ':
                        state.address = None
                    elif line.op == '.res':
                        state.address = pc
                        pc += state.bss_size
                    else:
                        state.address = pc
                        size = self._estimate_directive_size(line.op, state.operands, symbols, line, pc)
                        pc += size
                    continue

                state.address = pc
                new_spec = self._match_opcode(line, state.operands, state.forced_mode, symbols)
                if state.opcode != new_spec:
                    state.opcode = new_spec
                    changed = True
                pc += new_spec.size
            if not changed:
                return
        raise AssemblyError("Addressing mode resolution did not converge")

    def _select_addressing_mode(
        self,
        line: ParsedLine,
        operands: List[str],
        forced_mode: Optional[str],
        entries: Dict[str, OpcodeSpec],
        symbols: Dict[str, int],
    ) -> str:
        mnemonic = line.op
        if forced_mode:
            if forced_mode not in entries:
                available = ', '.join(entries.keys())
                raise AssemblyError(
                    _format_error(
                        line,
                        f"Forced addressing mode {forced_mode} not available for {mnemonic} (have {available})",
                    )
                )
            return forced_mode

        mode = _basic_addressing_mode(mnemonic, operands)

        if mode == 'EXT' and operands:
            if 'DIR' in entries:
                value = self._try_resolve_operand(operands[0], symbols, line)
                if value is not None and 0 <= value <= 0xFF:
                    return 'DIR'
            if 'EXT' in entries:
                return 'EXT'
            if 'DIR' in entries:
                return 'DIR'

        if mode == 'DIR' and 'DIR' not in entries and 'EXT' in entries:
            return 'EXT'

        return mode

    def _try_resolve_operand(self, expr: str, symbols: Dict[str, int], line: ParsedLine) -> Optional[int]:
        try:
            return evaluate(expr, symbols, f"{self.filename}:{line.line_no}")
        except ExpressionError:
            return None

    def _resolve_value(
        self,
        expr: str,
        symbols: Dict[str, int],
        line: ParsedLine,
        *,
        allow_relocation: bool,
    ) -> tuple[int, Optional[str]]:
        try:
            return self._eval(expr, symbols, line), None
        except AssemblyError:
            if allow_relocation:
                target = _extract_symbol(expr)
                if target is not None:
                    return 0, target
            raise

    def _second_pass(
        self,
        states: List[LineState],
        symbols: Dict[str, int],
        origin: int,
    ) -> tuple[bytes, List['LineEmission'], List['Relocation']]:
        data = bytearray()
        pc = origin
        emissions: List[LineEmission] = []
        relocations: List[Relocation] = []
        bss_entries: List[BssAllocation] = []
        for state in states:
            line = state.line
            if line.is_directive:
                if line.op == '.org':
                    target = self._eval(state.operands[0], symbols, line)
                    if target != origin:
                        raise AssemblyError(_format_error(line, '.org value must match initial origin in MVP'))
                    pc = origin
                    emissions.append(LineEmission(line=line, address=None, data=[]))
                elif line.op == '.equ':
                    emissions.append(LineEmission(line=line, address=None, data=[]))
                    continue
                elif line.op == '.res':
                    if state.bss_size > 0:
                        bss_entries.append(
                            BssAllocation(
                                name=line.label or f"BSS_{state.address:04X}",
                                address=state.address if state.address is not None else pc,
                                size=state.bss_size,
                            )
                        )
                    emissions.append(LineEmission(line=line, address=state.address, data=[]))
                    pc += state.bss_size
                    continue
                elif line.op == '.byte':
                    for operand in state.operands:
                        start = pc
                        if operand.startswith('"') and operand.endswith('"'):
                            bytes_ = _parse_string(operand, line)
                            _append_bytes(data, origin, start, bytes_)
                            pc += len(bytes_)
                            emissions.append(LineEmission(line=line, address=start, data=bytes_))
                        else:
                            value = self._eval(operand, symbols, line)
                            if not 0 <= value <= 0xFF:
                                raise AssemblyError(_format_error(line, f"Byte value out of range: {value}"))
                            emitted = [value & 0xFF]
                            _append_bytes(data, origin, start, emitted)
                            pc += 1
                            emissions.append(LineEmission(line=line, address=start, data=emitted))
                elif line.op == '.word':
                    for operand in state.operands:
                        start = pc
                        value, target = self._resolve_value(operand, symbols, line, allow_relocation=True)
                        if target is not None:
                            emitted = [0x00, 0x00]
                            relocations.append(
                                Relocation(
                                    section="text",
                                    offset=start - origin,
                                    type="absolute16",
                                    target=target,
                                    addend=0,
                                )
                            )
                        else:
                            if not 0 <= value <= 0xFFFF:
                                raise AssemblyError(_format_error(line, f"Word value out of range: {value}"))
                            emitted = [(value >> 8) & 0xFF, value & 0xFF]
                        _append_bytes(data, origin, start, emitted)
                        pc += 2
                        emissions.append(LineEmission(line=line, address=start, data=emitted))
                elif line.op == '.ascii':
                    start = pc
                    string_bytes = _parse_string(state.operands[0], line)
                    _append_bytes(data, origin, start, string_bytes)
                    pc += len(string_bytes)
                    emissions.append(LineEmission(line=line, address=start, data=string_bytes))
                elif line.op == '.fill':
                    count = self._eval(state.operands[0], symbols, line)
                    value = 0
                    if len(state.operands) == 2:
                        value = self._eval(state.operands[1], symbols, line)
                    value &= 0xFF
                    payload = [value] * count
                    start = pc
                    _append_bytes(data, origin, start, payload)
                    pc += count
                    emissions.append(LineEmission(line=line, address=start, data=payload))
                elif line.op == '.align':
                    boundary = self._eval(state.operands[0], symbols, line)
                    if boundary <= 0:
                        raise AssemblyError(_format_error(line, '.align argument must be positive'))
                    try:
                        padding = _alignment_padding(pc, boundary)
                    except ValueError as err:
                        raise AssemblyError(_format_error(line, str(err))) from err
                    if padding:
                        payload = [0] * padding
                        start = pc
                        _append_bytes(data, origin, start, payload)
                        pc += padding
                        emissions.append(LineEmission(line=line, address=start, data=payload))
                else:
                    raise AssemblyError(_format_error(line, f"Unsupported directive {line.op}"))
                continue
            if state.opcode is None:
                raise AssemblyError(_format_error(line, "Internal error: missing opcode"))
            spec = state.opcode
            opcode_bytes = [spec.opcode]
            operand_bytes: List[int] = []
            start = pc
            if spec.addressing == 'INH':
                pass
            elif spec.addressing == 'IMM':
                operand = state.operands[0]
                value = self._eval(operand[1:] if operand.startswith('#') else operand, symbols, line)
                if not 0 <= value <= 0xFF:
                    raise AssemblyError(_format_error(line, f"Immediate value out of range: {value}"))
                operand_bytes.append(value & 0xFF)
            elif spec.addressing == 'EXT':
                operand = state.operands[0]
                value, target = self._resolve_value(operand, symbols, line, allow_relocation=True)
                operand_offset = (start - origin) + len(opcode_bytes)
                if target is not None:
                    operand_bytes.extend([0x00, 0x00])
                    relocations.append(
                        Relocation(
                            section="text",
                            offset=operand_offset,
                            type="absolute16",
                            target=target,
                            addend=0,
                        )
                    )
                else:
                    if not 0 <= value <= 0xFFFF:
                        raise AssemblyError(_format_error(line, f"Absolute value out of range: {value}"))
                    operand_bytes.extend([(value >> 8) & 0xFF, value & 0xFF])
            elif spec.addressing == 'DIR':
                operand = state.operands[0]
                value, target = self._resolve_value(operand, symbols, line, allow_relocation=True)
                operand_offset = (start - origin) + len(opcode_bytes)
                if target is not None:
                    operand_bytes.append(0x00)
                    relocations.append(
                        Relocation(
                            section="text",
                            offset=operand_offset,
                            type="absolute8",
                            target=target,
                            addend=0,
                        )
                    )
                else:
                    if not 0 <= value <= 0xFF:
                        raise AssemblyError(_format_error(line, f"Direct value out of range: {value}"))
                    operand_bytes.append(value & 0xFF)
            elif spec.addressing == 'REL':
                operand = state.operands[0]
                value, target = self._resolve_value(operand, symbols, line, allow_relocation=True)
                operand_offset = (start - origin) + len(opcode_bytes)
                if target is not None:
                    relocations.append(
                        Relocation(
                            section="text",
                            offset=operand_offset,
                            type="relative8",
                            target=target,
                            addend=-(pc + spec.size),
                        )
                    )
                    operand_bytes.append(0x00)
                else:
                    offset = value - (pc + spec.size)
                    if offset < -128 or offset > 127:
                        raise AssemblyError(_format_error(line, f"Branch target out of range ({offset})"))
                    operand_bytes.append(offset & 0xFF)
            elif spec.addressing == 'IDX':
                if len(state.operands) == 1 and state.operands[0].upper() == 'X':
                    operand_bytes.append(0)
                elif len(state.operands) == 2 and state.operands[1].upper() == 'X':
                    value = self._eval(state.operands[0], symbols, line)
                    if not 0 <= value <= 0xFF:
                        raise AssemblyError(_format_error(line, f"Indexed offset out of range: {value}"))
                    operand_bytes.append(value & 0xFF)
                else:
                    raise AssemblyError(_format_error(line, "Invalid indexed operand"))
            else:
                raise AssemblyError(_format_error(line, f"Unsupported addressing mode {spec.addressing}"))
            combined = opcode_bytes + operand_bytes
            start = pc
            _append_bytes(data, origin, start, combined)
            pc += len(combined)
            emissions.append(LineEmission(line=line, address=start, data=combined))
        return bytes(data), emissions, relocations, bss_entries


def _append_bytes(buffer: bytearray, origin: int, pc: int, values: List[int]) -> None:
    offset = pc - origin
    if offset < 0:
        raise AssemblyError(f"Program counter {pc:#04x} lower than origin {origin:#04x}")
    if len(buffer) < offset:
        buffer.extend([0] * (offset - len(buffer)))
    buffer.extend(values)


def _format_error(line: ParsedLine, message: str) -> str:
    return f"Line {line.line_no}: {message} | {line.text.strip()}"


def _build_opcode_table() -> Dict[str, Dict[str, OpcodeSpec]]:
    table: Dict[str, Dict[str, OpcodeSpec]] = {}
    for item in opcodes_mb8861h.OPCODES:
        spec = OpcodeSpec(
            mnemonic=item['mnemonic'],
            addressing=item['addressing'],
            opcode=item['opcode'],
            size=item['size'],
        )
        table.setdefault(spec.mnemonic, {})[spec.addressing] = spec
    return table


def _build_sections(origin: int, machine: bytes, bss_entries: List[BssAllocation]) -> List[Section]:
    sections: List[Section] = []
    if machine:
        sections.append(Section(name="text", kind="code", address=origin, data=list(machine), bss_size=0))
    for index, entry in enumerate(bss_entries):
        name = entry.name or f"BSS_{index}"
        sections.append(
            Section(name=name, kind="bss", address=entry.address, data=[], bss_size=entry.size)
        )
    return sections


def _normalize_operands(raw_operands: List[str]) -> Tuple[List[str], Optional[str]]:
    if not raw_operands:
        return [], None
    operands: List[str] = []
    forced_mode: Optional[str] = None
    for index, operand in enumerate(raw_operands):
        text = operand.strip()
        if index == 0:
            forced_mode, text = _extract_address_hint(text)
        operands.append(text)
    return operands, forced_mode


def _extract_address_hint(operand: str) -> Tuple[Optional[str], str]:
    if not operand:
        return None, operand
    if operand.startswith('#'):
        return None, operand
    if operand.startswith('<'):
        return 'DIR', operand[1:].lstrip()
    if operand.startswith('>'):
        return 'EXT', operand[1:].lstrip()
    return None, operand


def _basic_addressing_mode(mnemonic: str, operands: List[str]) -> str:
    if not operands:
        return 'INH'
    first = operands[0]
    if first.startswith('#'):
        return 'IMM'
    if len(operands) == 1 and operands[0].upper() == 'X':
        return 'IDX'
    if len(operands) == 2 and operands[1].upper() == 'X':
        return 'IDX'
    if mnemonic in _RELATIVE_MNEMONICS and len(operands) == 1:
        return 'REL'
    return 'EXT'


_RELATIVE_MNEMONICS = {spec['mnemonic'] for spec in opcodes_mb8861h.OPCODES if spec['addressing'] == 'REL'}


def _parse_string(value: str, line: ParsedLine) -> List[int]:
    if not value.startswith('"') or not value.endswith('"'):
        raise AssemblyError(_format_error(line, f"Expected string literal, got {value}"))
    inner = value[1:-1]
    result: List[int] = []
    i = 0
    while i < len(inner):
        ch = inner[i]
        if ch == '\\':
            i += 1
            if i >= len(inner):
                raise AssemblyError(_format_error(line, 'Unterminated string escape'))
            escape = inner[i]
            mapping = {
                'n': '\n',
                'r': '\r',
                't': '\t',
                '\\': '\\',
                '"': '"',
                '0': '\0',
            }
            if escape not in mapping:
                raise AssemblyError(_format_error(line, f"Unsupported escape \\{escape}"))
            result.append(ord(mapping[escape]))
            i += 1
            continue
        result.append(ord(ch))
        i += 1
    return result


def _alignment_padding(current: int, boundary: int) -> int:
    if boundary == 0:
        return 0
    mask = boundary - 1
    if boundary & mask:
        raise ValueError("Alignment boundary must be a power of two")
    remainder = current & mask
    if remainder == 0:
        return 0
    return boundary - remainder


def _extract_symbol(expr: str) -> Optional[str]:
    token = expr.strip()
    if not token:
        return None
    if token.startswith('<') or token.startswith('>'):
        token = token[1:].strip()
    if token.startswith('#'):
        token = token[1:].strip()
    if token.isidentifier():
        return token.upper()
    return None
