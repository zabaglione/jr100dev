"""Compile a small, explicit unsigned-byte Python subset to MB8861H code.

Rules remain editable per game. No interpreter or Python runs on the JR-100.
All arithmetic wraps at eight bits; arrays contain 128 bytes. No recursion.
held() reads the most recently scanned input (0 released; directions 1-4),
without manufacturing repeat events or changing the physics update cadence.
"""

import ast
from pathlib import Path


class Compiler:
    def __init__(self, source):
        self.tree = ast.parse(source)
        self.out = []
        self.slots = {"s.mode": "MODE", "s.level": "LEVEL", "s.action": "ACTION"}
        self.labels = 0
        self.scope = ""
        self.strings = []
        self.funcs = {
            n.name: n for n in self.tree.body if isinstance(n, ast.FunctionDef)
        }

    def emit(self, text):
        self.out.append(text)

    def label(self):
        self.labels += 1
        return f"N_{self.labels}"

    def slot(self, n):
        key = "s." + n.attr if isinstance(n, ast.Attribute) else self.scope + "." + n.id
        if key not in self.slots:
            self.slots[key] = f"V_{len(self.slots)}"
        return self.slots[key]

    def load(self, n):
        if isinstance(n, ast.Constant):
            self.emit(f"    LDAA #{int(n.value) & 255}")
        elif isinstance(n, (ast.Name, ast.Attribute)):
            self.emit(f"    LDAA {self.slot(n)}")
        elif isinstance(n, ast.Subscript):
            self.load(n.slice)
            self.emit(
                f"    LDX #{n.value.id.upper()}_ARRAY\n    JSR N_INDEX\n    LDAA 0,X"
            )
        elif isinstance(n, ast.BinOp):
            self.load(n.left)
            self.emit("    PSHA")
            self.load(n.right)
            self.emit("    TAB\n    PULA")
            op = type(n.op)
            if op in (ast.Add, ast.Sub):
                self.emit("    ABA" if op is ast.Add else "    SBA")
            elif op in (ast.BitAnd, ast.BitOr, ast.BitXor):
                self.emit("    STAB N_TMP")
                self.emit(
                    "    "
                    + {ast.BitAnd: "ANDA", ast.BitOr: "ORAA", ast.BitXor: "EORA"}[op]
                    + " N_TMP"
                )
            else:
                self.emit(
                    "    JSR "
                    + {
                        ast.Mult: "N_MUL",
                        ast.FloorDiv: "N_DIV",
                        ast.Mod: "N_MOD",
                        ast.LShift: "N_SHL",
                        ast.RShift: "N_SHR",
                    }[op]
                )
        elif isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.Invert)):
            self.load(n.operand)
            self.emit("    NEGA" if isinstance(n.op, ast.USub) else "    COMA")
        elif isinstance(n, ast.IfExp):
            no, end = self.label(), self.label()
            self.branch(n.test, no, False)
            self.load(n.body)
            self.emit(f"    JMP {end}\n{no}:")
            self.load(n.orelse)
            self.emit(end + ":")
        elif isinstance(n, (ast.Compare, ast.BoolOp, ast.UnaryOp)):
            yes, end = self.label(), self.label()
            self.branch(n, yes, True)
            self.emit(f"    CLRA\n    JMP {end}\n{yes}:\n    LDAA #1\n{end}:")
        elif isinstance(n, ast.Call):
            self.call(n)
        else:
            raise TypeError(ast.dump(n))

    def branch(self, n, target, truth):
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not):
            self.branch(n.operand, target, not truth)
        elif isinstance(n, ast.BoolOp):
            direct = isinstance(n.op, ast.Or) == truth
            end = self.label()
            for value in n.values[:-1]:
                self.branch(
                    value, target if direct else end, truth if direct else not truth
                )
            self.branch(n.values[-1], target, truth)
            self.emit(end + ":")
        elif isinstance(n, ast.Compare):
            assert len(n.ops) == 1, "Use explicit and instead of chained comparisons"
            self.load(n.left)
            self.emit("    PSHA")
            self.load(n.comparators[0])
            self.emit("    TAB\n    PULA\n    CBA")
            branches = {
                ast.Eq: ("BEQ", "BNE"),
                ast.NotEq: ("BNE", "BEQ"),
                ast.Lt: ("BCS", "BCC"),
                ast.LtE: ("BLS", "BHI"),
                ast.Gt: ("BHI", "BLS"),
                ast.GtE: ("BCC", "BCS"),
            }
            self.emit(
                "    " + branches[type(n.ops[0])][0 if truth else 1] + " " + target
            )
        else:
            self.load(n)
            self.emit("    TSTA\n    " + ("BNE" if truth else "BEQ") + " " + target)

    def save(self, n):
        if isinstance(n, ast.Subscript):
            self.emit("    PSHA")
            self.load(n.slice)
            self.emit(
                f"    LDX #{n.value.id.upper()}_ARRAY\n    JSR N_INDEX\n    PULA\n    STAA 0,X"
            )
        else:
            self.emit(f"    STAA {self.slot(n)}")

    def call(self, n):
        name = n.func.id
        if name == "text":
            assert isinstance(n.args[2], ast.Constant)
            value = n.args[2].value
            label = f"N_STRING_{len(self.strings)}"
            self.strings.append((label, value))
            for i, arg in enumerate(n.args[:2]):
                self.load(arg)
                self.emit(f"    STAA N_ARG{i}")
            self.emit(f"    LDX #{label}\n    STX TEXT_PTR\n    JSR N_TEXT")
        elif name == "held":
            assert not n.args, "held() takes no arguments"
            self.emit("    LDAA KEY_LAST")
        elif name in ("animate", "hold"):
            assert len(n.args) == 1
            self.load(n.args[0])
            self.emit("    JSR N_" + name.upper())
        elif name == "flip":
            assert len(n.args) == 1
            self.load(n.args[0])
            self.emit("    LDAB #6\n    LDX #FLIP_FRAMES\n    JSR N_FACE")
        elif name == "face":
            assert len(n.args) == 2 and isinstance(n.args[0], ast.Constant)
            slot = n.args[0].value
            assert 0 <= slot < 8
            self.load(n.args[1])
            self.emit(f"    LDAB #{slot}\n    LDX #FACE_{slot}_FRAMES\n    JSR N_FACE")
        elif name in (
            "tile",
            "stamp",
            "number",
            "letter",
            "sound",
            "impact",
            "vanish",
            "mover",
        ):
            for i, arg in enumerate(n.args):
                self.load(arg)
                self.emit(f"    STAA N_ARG{i}")
            self.emit("    JSR N_" + name.upper())
        elif name in ("win", "lose"):
            if n.args:
                assert name == "lose" and len(n.args) == 1
                assert isinstance(n.args[0], ast.Constant) and isinstance(
                    n.args[0].value, str
                )
                label = f"N_STRING_{len(self.strings)}"
                self.strings.append((label, n.args[0].value))
                self.emit(f"    LDX #{label}\n    STX LOSS_MESSAGE")
            self.emit("    JSR N_" + name.upper())
        elif name in ("min", "max"):
            self.load(n.args[0])
            self.emit("    PSHA")
            self.load(n.args[1])
            self.emit("    TAB\n    PULA\n    CBA")
            end = self.label()
            self.emit(f"    {'BLS' if name == 'min' else 'BCC'} {end}\n    TBA\n{end}:")
        elif name in self.funcs:
            fn = self.funcs[name]
            assert len(fn.args.args) == len(n.args)
            for param, arg in zip(fn.args.args, n.args):
                self.load(arg)
                old = self.scope
                self.scope = name
                slot = self.slot(ast.Name(id=param.arg))
                self.scope = old
                self.emit("    STAA " + slot)
            self.emit("    JSR FN_" + name.upper())
        else:
            raise ValueError(name)

    def statements(self, nodes):
        for n in nodes:
            if isinstance(n, ast.Assign):
                assert len(n.targets) == 1
                self.load(n.value)
                self.save(n.targets[0])
            elif isinstance(n, ast.AugAssign):
                self.load(ast.BinOp(left=n.target, op=n.op, right=n.value))
                self.save(n.target)
            elif isinstance(n, ast.If):
                no, end = self.label(), self.label()
                self.branch(n.test, no, False)
                self.statements(n.body)
                self.emit(f"    JMP {end}\n{no}:")
                self.statements(n.orelse)
                self.emit(end + ":")
            elif isinstance(n, ast.For):
                assert n.iter.func.id == "range" and len(n.iter.args) == 1
                self.load(ast.Constant(value=0))
                self.save(n.target)
                loop, end = self.label(), self.label()
                self.emit(loop + ":")
                self.branch(
                    ast.Compare(
                        left=n.target, ops=[ast.GtE()], comparators=n.iter.args
                    ),
                    end,
                    True,
                )
                self.statements(n.body)
                self.emit("    JSR CLOCK_SERVICE")
                self.emit(
                    "    INC " + self.slot(n.target) + f"\n    JMP {loop}\n{end}:"
                )
            elif isinstance(n, ast.Return):
                if n.value:
                    self.load(n.value)
                self.emit("    RTS")
            elif isinstance(n, ast.Expr):
                if not isinstance(n.value, ast.Constant):
                    self.load(n.value)
            elif isinstance(n, ast.Pass):
                pass
            else:
                raise TypeError(ast.dump(n))

    def compile(self):
        reachable = {"init", "act", "tick", "draw"}
        pending = list(reachable)
        while pending:
            name = pending.pop()
            for node in ast.walk(self.funcs[name]):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    target = node.func.id
                    if target in self.funcs and target not in reachable:
                        reachable.add(target)
                        pending.append(target)
        for name, fn in self.funcs.items():
            if name not in reachable:
                continue
            self.scope = name
            self.emit("FN_" + name.upper() + ":")
            self.statements(fn.body)
            self.emit("    RTS")
        assert len(self.slots) < 256, "Too many state/local bytes"
        declarations = []
        for i, (key, slot) in enumerate(self.slots.items()):
            if slot.startswith("V_"):
                declarations.append(f"{slot}: .equ ${0x3400 + i:04X}")
        from art import emit

        return (
            "\n".join(declarations + self.out)
            + "\n"
            + "".join(
                emit(label, [*value.encode("ascii"), 0])
                for label, value in self.strings
            )
        )


def compile_file(path):
    compiler = Compiler(
        Path(__file__).with_name("support.py").read_text()
        + "\n"
        + Path(path).read_text()
    )
    return compiler.compile(), compiler.slots
