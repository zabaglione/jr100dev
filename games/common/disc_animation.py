"""Five rotating disc poses, sharing one four-character PCG bank."""

from relief import sprite


def unpack(bank):
    return [
        [
            (bank[((y // 8) * 2 + x // 8) * 8 + y % 8] >> (7 - x % 8)) & 1
            for x in range(16)
        ]
        for y in range(16)
    ]


def frames():
    poses = []
    for kind, width in (
        ("token-white", 10),
        ("token-white", 6),
        ("edge", 2),
        ("token-black", 6),
        ("token-black", 10),
    ):
        pixels = [[0] * 16 for _ in range(16)]
        left = (16 - width) // 2
        if kind == "edge":
            for y in range(2, 14):
                pixels[y][7] = 1
                pixels[y][8] = int(y % 2 == 0)
        else:
            original = unpack(sprite(kind))
            for y in range(15):
                for x in range(width):
                    pixels[y][left + x] = original[y][min(15, x * 16 // width)]
        # The contact shadow stays on the board while the disc turns above it.
        for x in range(3, 14, 2):
            pixels[15][x] = 1
        poses.append(
            [
                sum(pixels[y + dy][x + dx] << (7 - dx) for dx in range(8))
                for y in (0, 8)
                for x in (0, 8)
                for dy in range(8)
            ]
        )
    return poses
