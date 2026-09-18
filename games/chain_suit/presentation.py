"""Four recognizable suit symbols and six shared card-border characters."""

from relief import Pixels


def prepare(bank):
    suits = []
    for kind in range(4):
        pixels = Pixels(contact_shadow=False)
        if kind == 0:  # Spade.
            pixels.poly(
                [(7, 1), (13, 7), (13, 9), (11, 11), (4, 11), (2, 9), (2, 7)], True
            )
            pixels.poly([(7, 8), (5, 14), (10, 14)], True)
        elif kind == 1:  # Heart.
            pixels.ellipse(4, 5, 3, 3, True)
            pixels.ellipse(11, 5, 3, 3, True)
            pixels.poly([(1, 6), (14, 6), (7, 14)], True)
        elif kind == 2:  # Diamond.
            pixels.poly([(7, 1), (13, 7), (7, 14), (1, 7)], True)
        else:  # Club.
            pixels.ellipse(7, 4, 3, 3, True)
            pixels.ellipse(3, 9, 3, 3, True)
            pixels.ellipse(11, 9, 3, 3, True)
            pixels.poly([(7, 8), (5, 14), (10, 14)], True)
        suits += pixels.pack()
    borders = [
        [0, 0, 0, 7, 8, 16, 16, 16],
        [0, 0, 0, 224, 16, 16, 16, 16],
        [16, 16, 8, 7, 0, 0, 0, 0],
        [16, 16, 16, 224, 0, 0, 0, 0],
        [0, 0, 0, 255, 0, 0, 0, 0],
        [16] * 8,
    ]
    bank[:176] = suits + [value for border in borders for value in border]
