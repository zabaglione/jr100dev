"""Source-located diagnostics for the byte-oriented Python subset."""

import ast
from pathlib import Path

from devkit.project import Problem

API = {"tile": 3, "text": 3, "letter": 3, "number": 3, "sound": 1,
       "win": 0, "lose": (0, 1), "held": 0,
       "reschedule": 0, "animate": 1, "hold": 1, "glide": 1, "min": 2, "max": 2}
VALUE_API = {"held", "min", "max"}
VALUE_HELPERS = {"move", "rand", "distance", "ringx", "ringy", "ray"}
BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod, ast.LShift, ast.RShift, ast.BitAnd, ast.BitOr, ast.BitXor)
COMPARISONS = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)


class Validator:
    def __init__(self, path, tables):
        self.path = path
        self.tables = {"b": 128, "c": 128, "d": 128, **{k: len(v) for k, v in tables.items()}}
        self.source = path.read_text(encoding="utf-8")
        try:
            self.tree = ast.parse(self.source, filename=str(path))
        except SyntaxError as exc:
            raise Problem("SYNTAX", exc.msg, "Fix Python indentation or syntax at this line.", path, exc.lineno) from exc
        support = ast.parse(Path(__file__).resolve().parents[1].joinpath("native/support.py").read_text())
        self.helpers = {n.name: len(n.args.args) for n in support.body if isinstance(n, ast.FunctionDef)}
        self.reserved_helpers = set(self.helpers)
        self.helpers = {k: v for k, v in self.helpers.items() if k in {
            "move", "grid", "pointer", "box", "rand", "distance", "ringx", "ringy", "ray", "digits"
        }}
        self.functions = {}
        self.calls = {}
        if set(tables) & (self.reserved_helpers | set(API) | {"range", "init", "act", "tick", "draw"}):
            self.fail(self.tree, "A data table name conflicts with a function.")

    def fail(self, node, message, hint="Use the supported syntax in docs/python-games/language.md.", code="LANGUAGE"):
        raise Problem(code, message, hint, self.path, getattr(node, "lineno", 1))

    def check(self):
        for n in self.tree.body:
            if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
                continue
            if not isinstance(n, ast.FunctionDef):
                self.fail(n, "Only function definitions are allowed at module scope.", "Move initialization to init(); use s.name for persistent state.")
            if n.name in self.functions or n.name in self.reserved_helpers or n.name in API or n.name in self.tables:
                self.fail(n, f"Duplicate or reserved function: {n.name}")
            if not n.name.isascii() or not n.name.isidentifier() or n.name.startswith("_"):
                self.fail(n, "Use ASCII identifiers.")
            args = n.args
            if n.decorator_list or n.returns or args.posonlyargs or args.kwonlyargs or args.vararg or args.kwarg or args.defaults or any(a.annotation for a in args.args):
                self.fail(n, "Decorators, annotations, defaults and special parameters are unsupported.")
            self.functions[n.name] = n
        for name in ("init", "act", "tick", "draw"):
            if name not in self.functions:
                self.fail(self.tree, f"Missing entry function: {name}()", f"Add def {name}(): with a body (pass is allowed).", "ENTRY")
            if self.functions[name].args.args:
                self.fail(self.functions[name], f"{name}() takes no parameters.")
        # Assembly symbols are case-insensitive.
        if len({n.upper() for n in self.functions}) != len(self.functions):
            self.fail(self.tree, "Function names must differ beyond letter case.")
        for fn in self.functions.values():
            names = [arg.arg for arg in fn.args.args]
            if len(names) != len(set(names)):
                self.fail(fn, "Duplicate parameter names.")
            for arg in fn.args.args:
                self.target(ast.copy_location(ast.Name(id=arg.arg, ctx=ast.Store()), fn), set())
        self.fields = {"mode", "level", "action"}
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
                self.fields.add(n.attr)
        for name, fn in self.functions.items():
            self.scope = name
            self.calls[name] = set()
            self.statements(fn.body, {a.arg for a in fn.args.args})
        visited = set()
        def visit(name, active):
            if name in active:
                self.fail(self.functions[name], "Recursive calls are unsupported.", "Replace recursion with a bounded for loop.", "RECURSION")
            if name in visited:
                return
            for called in self.calls[name]:
                visit(called, active | {name})
            visited.add(name)
        for name in self.functions:
            visit(name, set())
        # Animation calls render draw() again; they cannot be reached from draw.
        pending, seen = ["draw"], set()
        while pending:
            name = pending.pop()
            if name in seen:
                continue
            seen.add(name)
            for n in ast.walk(self.functions[name]):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("animate", "hold", "glide"):
                    self.fail(n, "Animation inside draw() would re-enter draw().", "Call animation from act() or tick().", "RECURSION")
                if isinstance(n, (ast.Attribute, ast.Subscript)) and isinstance(n.ctx, ast.Store):
                    self.fail(n, "draw() must not change state or arrays.", "Update state in init(), act() or tick(); draw() only renders.")
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {"win", "lose", "sound", "reschedule", "rand", "box"}:
                    self.fail(n, f"draw() cannot call state-changing {n.func.id}().")
            pending += list(self.calls[name])

    def target(self, n, defined):
        if isinstance(n, ast.Name):
            if n.id in {"s", *self.tables, *API, *self.helpers, *self.functions} or not n.id.isascii() or n.id.startswith("_"):
                self.fail(n, f"Reserved or invalid local name: {n.id}")
            return {n.id}
        self.expr(n, defined, writing=True)
        return set()

    def statements(self, nodes, defined):
        defined = set(defined)
        for n in nodes:
            if isinstance(n, ast.Assign) and len(n.targets) == 1:
                self.expr(n.value, defined)
                defined |= self.target(n.targets[0], defined)
            elif isinstance(n, ast.AugAssign) and isinstance(n.op, BINOPS):
                self.expr(n.target, defined)
                self.expr(n.value, defined)
                defined |= self.target(n.target, defined)
            elif isinstance(n, ast.If):
                self.expr(n.test, defined)
                defined |= self.statements(n.body, defined) & self.statements(n.orelse, defined)
            elif isinstance(n, ast.For):
                if n.orelse or not isinstance(n.target, ast.Name) or not isinstance(n.iter, ast.Call) or not isinstance(n.iter.func, ast.Name) or n.iter.func.id != "range" or len(n.iter.args) != 1 or n.iter.keywords:
                    self.fail(n, "Use for i in range(count), without else.")
                self.expr(n.iter.args[0], defined)
                if any(isinstance(x, ast.Call) or isinstance(x, ast.Name) and x.id == n.target.id for x in ast.walk(n.iter.args[0])):
                    self.fail(n, "Compute a stable loop bound before range().", "Do not call a function or use the loop index in its bound.", "LOOP")
                if any(isinstance(x, ast.Name) and isinstance(x.ctx, ast.Store) and x.id == n.target.id for statement_node in n.body for x in ast.walk(statement_node)):
                    self.fail(n, "Do not modify or reuse the active loop index.", "Use a different variable for inner loops and calculations.", "LOOP")
                loop_defined = defined | self.target(n.target, defined)
                self.statements(n.body, loop_defined)
                defined.discard(n.target.id)
            elif isinstance(n, ast.Return):
                if n.value:
                    self.expr(n.value, defined)
            elif isinstance(n, ast.Expr):
                if isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
                    continue
                if not isinstance(n.value, ast.Call):
                    self.fail(n, "An expression statement must call a function.")
                self.expr(n.value, defined, statement=True)
            elif not isinstance(n, ast.Pass):
                self.fail(n, f"Unsupported statement: {type(n).__name__}")
        return defined

    def expr(self, n, defined, writing=False, statement=False):
        if isinstance(n, ast.Constant):
            if type(n.value) not in (int, bool) or not 0 <= n.value <= 255:
                self.fail(n, "Numeric literals must be bytes (0-255).", "Split larger values into bytes; text() and lose() accept literal strings.")
        elif isinstance(n, ast.Name):
            if n.id not in defined:
                self.fail(n, f"Local '{n.id}' is read before definite assignment.", "Initialize it on every branch, or use s.name for persistent state.", "UNINITIALIZED")
        elif isinstance(n, ast.Attribute):
            if not isinstance(n.value, ast.Name) or n.value.id != "s" or not n.attr.isascii():
                self.fail(n, "Only s.name attributes are supported.")
            if not writing and n.attr not in self.fields:
                self.fail(n, f"Unknown state field: s.{n.attr}", "Initialize this field in init() and check for spelling errors.", "STATE")
            if writing and n.attr in ("mode", "level", "action"):
                self.fail(n, f"s.{n.attr} is owned by the runtime.", "Read it as input; use win() or lose() to change game outcome.")
        elif isinstance(n, ast.Subscript):
            if not isinstance(n.value, ast.Name) or n.value.id not in self.tables:
                self.fail(n, "Use b[index], c[index], d[index] or a declared data table.")
            if writing and n.value.id not in ("b", "c", "d"):
                self.fail(n, "dataTables are read-only.")
            self.expr(n.slice, defined)
            if isinstance(n.slice, ast.Constant) and n.slice.value >= self.tables[n.value.id]:
                self.fail(n, "Array index is outside the declared array.", "Use 0-127 for b/c/d, or the actual data table length.", "BOUNDS")
            if isinstance(n.slice, ast.UnaryOp) and isinstance(n.slice.op, ast.USub) and isinstance(n.slice.operand, ast.Constant) and n.slice.operand.value != 0:
                self.fail(n, "Negative array indexes wrap to unsigned bytes.", "Use a nonnegative index within the actual array length.", "BOUNDS")
        elif isinstance(n, ast.BinOp) and isinstance(n.op, BINOPS):
            self.expr(n.left, defined)
            self.expr(n.right, defined)
            if isinstance(n.op, (ast.FloorDiv, ast.Mod)) and isinstance(n.right, ast.Constant) and n.right.value == 0:
                self.fail(n, "Division by zero.", "Guard the divisor before division.", "DIVZERO")
        elif isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.Not, ast.USub, ast.Invert)):
            self.expr(n.operand, defined)
        elif isinstance(n, ast.Compare) and len(n.ops) == 1 and isinstance(n.ops[0], COMPARISONS):
            self.expr(n.left, defined)
            self.expr(n.comparators[0], defined)
        elif isinstance(n, ast.BoolOp):
            for value in n.values:
                self.expr(value, defined)
        elif isinstance(n, ast.IfExp):
            for value in (n.test, n.body, n.orelse):
                self.expr(value, defined)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            name = n.func.id
            arity = {**self.helpers, **API, **{k: len(v.args.args) for k, v in self.functions.items()}}.get(name)
            if arity is None or n.keywords or len(n.args) not in (arity if isinstance(arity, tuple) else (arity,)):
                self.fail(n, f"Unknown function or wrong positional arguments: {name}", "Check the API reference; keyword arguments are unsupported.", "CALL")
            if not statement and name in API and name not in VALUE_API:
                self.fail(n, f"{name}() does not return a value.")
            if not statement and name in self.helpers and name not in VALUE_HELPERS:
                self.fail(n, f"{name}() does not return a value.")
            if not statement and name in self.functions and not returns_value(self.functions[name].body):
                self.fail(n, f"{name}() must return a byte on every path when used as a value.")
            if name in self.functions:
                self.calls[self.scope].add(name)
            for i, arg in enumerate(n.args):
                if any(isinstance(v, ast.Call) for v in ast.walk(arg)):
                    self.fail(arg, "Nested calls in arguments are unsupported by this backend.", "Compute each inner call into a local variable before the outer call.", "NESTED_CALL")
                if name == "text" and i == 2 or name == "lose":
                    from devkit.project import ascii_text
                    if not isinstance(arg, ast.Constant) or not ascii_text(arg.value, 31 if name == "lose" else 32):
                        self.fail(arg, "Use a literal uppercase ASCII string fitting one row.")
                else:
                    self.expr(arg, defined)
        else:
            self.fail(n, f"Unsupported expression: {type(n).__name__}")


def validate_source(path, tables=None):
    Validator(Path(path), tables or {}).check()


def returns_value(nodes):
    if any(isinstance(n, ast.Return) and n.value is None for node in nodes for n in ast.walk(node)):
        return False
    for node in nodes:
        if isinstance(node, ast.Return):
            return node.value is not None
        if isinstance(node, ast.If) and returns_value(node.body) and returns_value(node.orelse):
            return True
    return False


class ByteExpressions(ast.NodeTransformer):
    """Make the host oracle match the compiler's byte intermediates."""
    def visit_BinOp(self, node):
        self.generic_visit(node)
        return ast.copy_location(ast.Call(func=ast.Name(id="_byte", ctx=ast.Load()), args=[node], keywords=[]), node)

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        return ast.copy_location(ast.Call(func=ast.Name(id="_byte", ctx=ast.Load()), args=[node], keywords=[]), node)

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        return ast.copy_location(ast.Call(func=ast.Name(id="_truth", ctx=ast.Load()), args=[node], keywords=[]), node)

    def visit_AugAssign(self, node):
        import copy

        target = copy.deepcopy(node.target)
        target.ctx = ast.Load()
        value = self.visit(ast.copy_location(ast.BinOp(left=target, op=node.op, right=node.value), node))
        return ast.copy_location(ast.Assign(targets=[node.target], value=value), node)


def model_code(source, path):
    return compile(ast.fix_missing_locations(ByteExpressions().visit(ast.parse(source, filename=str(path)))), str(path), "exec")
