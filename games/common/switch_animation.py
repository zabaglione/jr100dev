"""Five edge-on switch poses, sharing one four-character PCG bank."""

from disc_animation import unpack
from relief import sprite


def frames():
    poses = []
    for kind, width in (
        ("frame", 10),
        ("frame", 6),
        ("edge", 2),
        ("switch", 6),
        ("switch", 10),
    ):
        pixels = [[0] * 16 for _ in range(16)]
        left = (16 - width) // 2
        if kind == "edge":
            for y in range(1, 14):
                pixels[y][7] = 1
                pixels[y][8] = int(y % 2 == 0)
        else:
            original = unpack(sprite(kind))
            for y in range(15):
                for x in range(width):
                    pixels[y][left + x] = original[y][x * 16 // width]
        poses.append(
            [
                sum(pixels[y + dy][x + dx] << (7 - dx) for dx in range(8))
                for y in (0, 8)
                for x in (0, 8)
                for dy in range(8)
            ]
        )
    return poses
