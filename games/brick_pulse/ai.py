"""QA paddle planner; simulation predicts rebounds, inputs still move the paddle."""

from pathlib import Path

from checks import Model, State

CODE = compile(Path(__file__).with_name("rules.py").read_text(), "brick-rules", "exec")


def clone(model):
    copy = object.__new__(Model)
    copy.s = State()
    copy.s.__dict__.update(model.s.__dict__)
    copy.b, copy.c, copy.d = bytearray(model.b), bytearray(model.c), bytearray(model.d)
    copy.held = 0
    copy.env = {
        "s": copy.s,
        "b": copy.b,
        "c": copy.c,
        "d": copy.d,
        "sound": lambda *a: None,
        "impact": lambda *a: None,
        "vanish": lambda *a: None,
        "held": lambda: 0,
        "win": lambda: setattr(copy.s, "mode", 2),
        "lose": lambda: setattr(copy.s, "mode", 3),
    }
    exec(CODE, copy.env)  # noqa: S102 - Only the project-owned rules file.
    return copy


def incoming(model):
    f = clone(model)
    for _ in range(300):
        if f.s.mode != 1:
            return f
        if f.s.dy and f.s.y == 15 and (not f.s.slow or (f.s.clock + 1) % 2 == 0):
            return f
        f.tick()
    return f


def target(model):
    initial = sum(model.b) + model.s.enemy * 3

    def choose(state, depth):
        f = incoming(state)
        if f.s.mode != 1:
            return (10000 if f.s.mode == 2 else -10000), state.s.paddle
        x = f.s.x
        if not f.s.steep or (f.s.steps + 1) % 2 == 0:
            x += 1 if f.s.dx or x == 0 else -1
            if f.s.x == 29:
                x = 28
        best = (-100000, state.s.paddle)
        for pos in range(0, 31 - f.s.width, 2):
            if not pos <= x < pos + f.s.width:
                continue
            nxt = clone(f)
            nxt.s.paddle = pos
            nxt.tick()
            later = incoming(nxt)
            score = (initial - sum(later.b) - later.s.enemy * 3) * 100
            score += (later.s.hp - model.s.hp) * 2000 + later.s.caught * 8
            if later.s.mode == 2:
                score += 10000
            elif depth:
                score = choose(nxt, depth - 1)[0]
            # Prefer reachable, central catches when damage and safety agree.
            score -= abs(pos - state.s.paddle) * 0.01
            if score > best[0]:
                best = score, pos
        return best

    return choose(model, 2)[1]
