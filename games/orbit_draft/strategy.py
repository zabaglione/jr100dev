"""Independent sixteen-cell rules and a player that reads only five visible cards."""

from dataclasses import dataclass
from functools import lru_cache

EMPTY = 255
LINES = tuple(
    (row * 4 + col, (row + dy) * 4 + col + dx, (row + 2 * dy) * 4 + col + 2 * dx)
    for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1))
    for row in range(4)
    for col in range(4)
    if 0 <= row + 2 * dy < 4 and 0 <= col + 2 * dx < 4
)


@dataclass(frozen=True)
class View:
    board: tuple
    hand: tuple
    forecast: tuple
    spins: int


def matches(board):
    lines = [
        line
        for line in LINES
        if board[line[0]] != EMPTY and len({board[i] for i in line}) == 1
    ]
    return lines, frozenset(i for line in lines for i in line)


def gravity(board):
    result = [EMPTY] * 16
    for col in range(4):
        cards = [
            board[row * 4 + col] for row in range(4) if board[row * 4 + col] != EMPTY
        ]
        for row, card in enumerate(cards, 4 - len(cards)):
            result[row * 4 + col] = card
    return tuple(result)


@lru_cache(maxsize=8192)
def resolve(board):
    waves = []
    while True:
        lines, marked = matches(board)
        if not lines:
            board = gravity(board)
            lines, marked = matches(board)
        if not lines:
            return board, tuple(waves)
        chain = len(waves) + 1
        points = len(marked) * 2 * chain + (len(lines) - 1) * 2
        waves.append((len(marked), len(lines), points))
        board = gravity(
            tuple(EMPTY if i in marked else value for i, value in enumerate(board))
        )


def play(view, choice):
    """Return a visible-state result without peeking at the unseen random deck."""
    kind, pick, target = choice
    board = list(view.board)
    hand, forecast, spins = list(view.hand), view.forecast, view.spins
    if kind == "drop":
        if hand[pick] == EMPTY:
            return None
        holes = [
            row * 4 + target for row in range(4) if board[row * 4 + target] == EMPTY
        ]
        if not holes:
            return None
        board[max(holes)] = hand[pick]
        hand[pick] = forecast[0] if forecast else EMPTY
        forecast = forecast[1:]
    else:
        if spins == 0:
            return None
        cells = (
            tuple(target * 4 + col for col in range(4))
            if pick == 0
            else tuple(row * 4 + target for row in range(4))
        )
        if len({board[pos] for pos in cells}) == 1:
            return None
        for source, dest in zip(cells, cells[1:] + cells[:1]):
            board[dest] = view.board[source]
        spins -= 1
    board, waves = resolve(tuple(board))
    spins = min(4, spins + len(waves))
    points = sum(wave[2] for wave in waves)
    if kind == "spin" and board == view.board and not points:
        return None
    return View(board, tuple(hand), forecast, spins), points, waves


def options(view):
    for offer in range(2):
        for col in range(4):
            choice = ("drop", offer, col)
            result = play(view, choice)
            if result:
                yield choice, result
    for axis, length in ((0, 4), (1, 4)):
        for line in range(length):
            choice = ("spin", axis, line)
            result = play(view, choice)
            if result:
                yield choice, result


def potential(view):
    pairs = sum(
        1
        for line in LINES
        if sum(view.board[i] == EMPTY for i in line) == 1
        and len({view.board[i] for i in line if view.board[i] != EMPTY}) == 1
    )
    # Keep headroom in every column; a single full column restricts the draft.
    blocked = sum(view.board[col] != EMPTY for col in range(4))
    return view.board.count(EMPTY) * 2 + pairs * 4 + view.spins * 3 - blocked * 9


def choose(view, remaining, depth=4):
    """A bounded look-ahead over the two offers and three previewed cards."""
    frontier = [(view, 0, ())]
    candidates = []
    for _ in range(depth):
        next_frontier = []
        seen = set()
        for state, points, path in frontier:
            for choice, (future, gain, waves) in options(state):
                route = path + (choice,)
                total = points + gain
                if EMPTY not in future.board and future.spins == 0:
                    continue
                # Prefer simultaneous/chain gains, while minimizing needless spins.
                value = total * 12 + potential(future) - len(route) * 2
                candidate = (value, total, route, future)
                candidates.append(candidate)
                key = (future, total)
                if key not in seen:
                    seen.add(key)
                    next_frontier.append((future, total, route))
        winning = [v for v in candidates if v[1] >= remaining]
        if winning:
            best = max(
                winning, key=lambda v: (v[0], -sum(c[0] == "spin" for c in v[2]))
            )
            return best[2][0]
        next_frontier.sort(key=lambda v: v[1] * 12 + potential(v[0]), reverse=True)
        frontier = next_frontier[:48]
        if not frontier:
            break
    assert candidates, "No playable move remains"
    return max(candidates, key=lambda v: v[0])[2][0]
