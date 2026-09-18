"""Verify compressed text on the CPU and independent title/bank transitions."""

import json

from machine import ROOT, SYMS, Machine, lib


def display(text):
    return bytes(64 if char == " " else ord(char) - 32 for char in text)


def check():
    strings = json.loads((ROOT / "text.json").read_text())
    art = json.loads((ROOT / "build/title-art.json").read_text())
    m = Machine()
    try:
        # Compare every emitted message with the original, uncompressed text.
        lib.reset_min_sp()
        for name, text in strings.items():
            for offset in range(768):
                m.set(SYMS["FRAMEBUFFER"] + offset, 0x55)
            _, b, _, _ = m.call("TEXT", 0x30, 0, SYMS[name])
            assert m.read("FRAMEBUFFER", len(text)) == display(text), name
            assert m.get(SYMS["FRAMEBUFFER"] + len(text)) == 0x55, name
            assert b == 0, "TEXT changed caller B"
        text_stack = 0x3FFF - lib.min_sp()
        assert text_stack < 64
        # A long expansion at the last column must not overwrite game state.
        guard = m.read("STATE_BEGIN", 32)
        text = strings["HELP_LINES_0"]
        m.call("TEXT", 0x32, 0xFC, SYMS["HELP_LINES_0"])
        assert m.read(0x32FC, 4) == display(text[:4])
        assert m.read("STATE_BEGIN", 32) == guard

        # The mural comes from authored pixels; menu/text are checked separately.
        for difficulty in range(3):
            m.set("G_MODE", 0)
            m.set("G_DIFFICULTY", difficulty)
            m.call("RENDER_SCREEN")
            expected = bytearray(art["screen"])
            goal = display(strings["S_GOAL"])
            expected[549 : 549 + len(goal)] = goal
            for index in range(3):
                offset = (9 + index) * 64
                label = display(strings[f"DIFFICULTY_NAMES_{index}"])
                expected[offset + 3 : offset + 3 + len(label)] = label
                if difficulty == index:
                    expected[offset] = ord(">") - 32
            expected[736:] = display(strings["S_KEYS"])
            assert len(expected) == 768
            assert m.read(0xC100, 768) == expected
            assert m.read(0xC000, len(art["pcg"])) == bytes(art["pcg"])

        # Shimmer touches the sparkle slot only; title inputs remain edge driven.
        before = m.read(0xC000, 256)
        vram = m.read(0xC100, 768)
        for phase in (1, 0):
            m.setw("G_SEED", phase << 8)
            m.call("TITLE_SHIMMER")
            after = m.read(0xC000, 256)
            offset = SYMS["TITLE_SPARK_ADDRESS"] - 0xC000
            assert (
                after[:offset] == before[:offset]
                and after[offset + 8 :] == before[offset + 8 :]
            )
            assert m.read(0xC100, 768) == vram
            assert m.word("G_SEED") == phase << 8
            assert after[offset : offset + 8] != before[offset : offset + 8]
            before = after
        # Simulate a completed game, then return to title and start again via keys.
        game_tiles = m.read("TILES", SYMS["TILES_END"] - SYMS["TILES"])
        for end_mode in (8, 9):
            m.set("G_MODE", end_mode)
            m.call("RENDER_SCREEN")
            assert m.read(0xC000, len(game_tiles)) == game_tiles
            m.resume()
            m.action(5)
            assert m.get("G_MODE") == 0
            assert m.read(0xC000, len(art["pcg"])) == bytes(art["pcg"])
            m.action(5)
            assert m.get("G_MODE") == 1
            assert m.read(0xC000, len(game_tiles)) == game_tiles
    finally:
        m.close()
    return {
        "status": "passed",
        "text_strings": len(strings),
        "text_stack_bytes": text_stack,
        "title_modes": 3,
    }


if __name__ == "__main__":
    print(check())
