import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, Tuple


PATTERNS: Dict[str, Tuple[int, int]] = {
    "8x8": (8, 8),
    "8x16": (8, 16),
    "16x8": (16, 8),
    "16x16": (16, 16),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="JR-100 character JSON validator")
    parser.add_argument("files", type=Path, nargs="+", help="JSON file(s) exported from the character editor.")
    return parser.parse_args()


def validate_payload(data: Dict[str, object], source: Path) -> None:
    pattern = data.get("pattern")
    if pattern not in PATTERNS:
        raise ValueError(f"{source}: 未対応の pattern 値 {pattern!r}")
    expected_width, expected_height = PATTERNS[pattern]
    width = data.get("width")
    height = data.get("height")
    if width != expected_width or height != expected_height:
        raise ValueError(
            f"{source}: 幅/高さが pattern の定義と一致しません (期待 {expected_width}x{expected_height}, 実際 {width}x{height})"
        )

    hex_string = data.get("hex")
    if not isinstance(hex_string, str):
        raise ValueError(f"{source}: hex フィールドは文字列である必要があります")
    bytes_per_row = (expected_width + 7) // 8
    expected_bytes = expected_height * bytes_per_row
    if len(hex_string) != expected_bytes * 2:
        raise ValueError(
            f"{source}: hex の長さが一致しません (期待 {expected_bytes * 2} 桁, 実際 {len(hex_string)} 桁)"
        )
    try:
        blob = bytes.fromhex(hex_string)
    except ValueError as error:
        raise ValueError(f"{source}: hex が不正です: {error}") from error
    validate_bit_padding(blob, expected_width, expected_height, source)


def validate_bit_padding(blob: bytes, width: int, height: int, source: Path) -> None:
    bytes_per_row = (width + 7) // 8
    for row in range(height):
        row_slice = blob[row * bytes_per_row : (row + 1) * bytes_per_row]
        if width % 8 == 0:
            continue
        unused_bits = 8 - (width % 8)
        last_byte = row_slice[-1]
        if last_byte & ((1 << unused_bits) - 1):
            raise ValueError(f"{source}: {row} 行目の末尾にパディングビット以外の 1 が含まれています")


def load_json(path: Path) -> Dict[str, object]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError) as error:
        raise ValueError(f"{path}: JSON の読み込みに失敗しました: {error}") from error


def main() -> None:
    args = parse_args()
    for path in args.files:
        payload = load_json(path)
        validate_payload(payload, path)
        print(f"{path}: OK")


if __name__ == "__main__":
    main()
