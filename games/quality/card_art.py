"""Current card-side poses share four PCG characters during a physical flip."""

from relief import Pixels


def frames():
    result = []
    for width in (14, 8, 2, 8, 14):
        p = Pixels(contact_shadow=False)
        x = (16 - width) // 2
        p.rect(x, 1, width, 14)
        if width > 2:
            p.line(x + 1, 2, x + width - 2, 2)
            if len(result) < 2:
                for y in range(4, 13, 2):
                    p.line(x + 2, y, x + width - 3, y)
        result += [p.pack()]
    return result
