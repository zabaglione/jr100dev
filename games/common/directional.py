"""Original 16x16 actors. Only the current pose occupies four PCG characters."""

from art import emit

# Hex rows are authored monochrome silhouettes: N/S/E; W mirrors E.
POSES = {
    "explorer": (
        "03c0 07e0 07e0 0660 07e0 03c0 07e0 0ff0 1bd8 1998 0990 07e0 0660 0660 0c30 0000",
        "03c0 07e0 07e0 05a0 0660 03c0 07e0 0db0 1998 1bd8 0990 07e0 0660 0660 0c30 0000",
        "03c0 07e0 07f0 05b0 07e0 03c0 0fc0 1ee0 16f0 1e50 0ec0 07c0 06c0 0460 0c60 0000",
    ),
    "robot": (
        "0180 0ff0 0ff0 0990 0ff0 0660 0ff0 1bd8 1998 1bd8 0ff0 0660 0660 0e70 0e70 0000",
        "0180 0ff0 0ff0 0810 0a50 0660 0ff0 1bd8 1bd8 1998 0ff0 0660 0660 0e70 0e70 0000",
        "0180 07e0 07e0 0430 05f0 0360 07c0 0fc0 0bfe 0a52 07de 0360 0360 0730 0730 0000",
    ),
    "guard": (
        "03c0 07e0 0ff0 07e0 0660 03c0 07e0 0ff0 1bd8 1bd8 0990 07e0 0660 0660 0e70 0000",
        "03c0 07e0 0ff0 0420 0660 03c0 0ff0 1bb8 1998 1998 0990 07e0 0660 0660 0e70 0000",
        "03c0 07e0 07f8 0420 0660 03c0 07c0 0fe0 1bf0 1950 09c0 07c0 0660 0660 0e70 0000",
    ),
}

ACTORS = {
    "iron-script": {2: "robot"},
    "quiet-route": {2: "explorer", 5: "guard"},
    "magnet-vault": {2: "robot"},
    "frost-steps": {2: "explorer"},
    "glyph-shift": {2: "explorer"},
    "compass-rose": {2: "explorer"},
    "mirror-relic": {2: "explorer"},
    "ribbon-snake": {2: "snake"},
}


def frames(kind):
    if kind == "snake":
        rows = [
            int(v, 16)
            for v in [
                "0000",
                "07e0",
                "0ff0",
                "1ff8",
                "1998",
                "1998",
                "1ff8",
                "0ff0",
                "0db0",
                "07e0",
                "03c0",
                "0180",
                "0180",
                "0000",
                "0000",
                "0000",
            ]
        ]
        north = [[(r >> (15 - x)) & 1 for x in range(16)] for r in rows]
        east = [list(row) for row in zip(*north[::-1])]
        south = [row[::-1] for row in north[::-1]]
        west = [row[::-1] for row in east]
        poses = (north, south, west, east)
    else:
        north, south, east = (
            [
                [(int(row, 16) >> (15 - x)) & 1 for x in range(16)]
                for row in pose.split()
            ]
            for pose in POSES[kind]
        )
        poses = (north, south, [row[::-1] for row in east], east)
    return [
        [
            sum(p[y + dy][x + dx] << (7 - dx) for dx in range(8))
            for y in (0, 8)
            for x in (0, 8)
            for dy in range(8)
        ]
        for p in poses
    ]


def assets(game_id, bank):
    result = ""
    for slot, kind in ACTORS.get(game_id, {}).items():
        poses = frames(kind)
        bank[slot * 32 : slot * 32 + 32] = poses[1]
        result += emit(f"FACE_{slot}_FRAMES", [b for pose in poses for b in pose])
    return result
