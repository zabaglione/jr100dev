"""Visible line selection and a four-character walking/celebrating actor."""

from art import emit
from directional import frames
from relief import Pixels


def prepare(bank):
    bank[32:64] = [byte ^ 255 for byte in bank[0:32]]
    bank[128:160] = [byte ^ 255 for byte in bank[96:128]]
    poses = frames("explorer")
    bank[64:96] = poses[1]
    for raised in (True, False):
        pixels = Pixels(contact_shadow=False)
        for y in range(16):
            for x in range(16):
                byte = poses[1][(y // 8 * 2 + x // 8) * 8 + y % 8]
                pixels.dot(x, y, byte >> (7 - x % 8) & 1)
        for y in range(6, 12):
            for x in (0, 1, 2, 3, 12, 13, 14, 15):
                pixels.dot(x, y, 0)
        pixels.line(3, 7, 0, 3 if raised else 7)
        pixels.line(12, 7, 15, 3 if raised else 7)
        poses.append(pixels.pack())
    return emit("FACE_2_FRAMES", [byte for pose in poses for byte in pose])
