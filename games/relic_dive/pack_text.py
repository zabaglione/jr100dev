"""Deterministic byte-pair text encoding; dictionary children precede parents."""

from collections import Counter


def pack(strings):
    encoded = {name: text.encode("ascii") for name, text in strings.items()}
    assert all(all(32 <= byte < 128 for byte in text) for text in encoded.values())
    pairs = []
    for token in range(128, 256):
        counts = Counter(
            pair for text in encoded.values() for pair in zip(text, text[1:])
        )
        if not counts:
            break
        pair = max(
            counts,
            key=lambda pair: (
                sum(text.count(bytes(pair)) for text in encoded.values()),
                tuple(-byte for byte in pair),
            ),
        )
        if sum(text.count(bytes(pair)) for text in encoded.values()) <= 2:
            break
        pairs.append(pair)
        encoded = {
            name: text.replace(bytes(pair), bytes([token]))
            for name, text in encoded.items()
        }
    lines = ["TEXT_PAIRS:"]
    lines.extend("    .BYTE " + ",".join(map(str, pair)) for pair in pairs)
    for name, text in encoded.items():
        lines.append(name + ": .BYTE " + ",".join(map(str, text + b"\0")))
    report = {
        "original_bytes": sum(len(text) + 1 for text in strings.values()),
        "packed_bytes": sum(len(text) + 1 for text in encoded.values())
        + 2 * len(pairs),
        "pairs": len(pairs),
    }
    return "\n".join(lines), report
