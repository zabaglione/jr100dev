"""Create an editable project without altering the public game collection."""

import json
import re
from pathlib import Path

from devkit.project import ROOT, require


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def make_art():
    # Original SDK sprites: floor, wall, explorer, crystal, crate, spikes, gate, frame.
    def rows(kind):
        result = []
        for y in range(16):
            line = ""
            for x in range(16):
                on = False
                if kind == 0:
                    on = x == 7 and y == 15
                elif kind == 1:
                    on = y in (0, 7, 15) or x in (0, 15) or (y < 7 and x == 7) or (y > 7 and x == 4)
                elif kind == 2:
                    on = (4 <= x <= 10 and 2 <= y <= 6) or (5 <= x <= 9 and 7 <= y <= 11) or (y >= 11 and (x == 4 or x == 10)) or (y == 8 and 2 <= x <= 12)
                    if (x, y) in ((8, 4), (9, 4)):
                        on = False
                elif kind == 3:
                    on = abs(x-7) + abs(y-7) <= 6 and (x <= 7 or y <= 7 or abs(x-7)+abs(y-7) >= 5)
                elif kind == 4:
                    on = x in (2, 13) and 2 <= y <= 13 or y in (2, 13) and 2 <= x <= 13 or x == y and 2 <= x <= 13
                elif kind == 5:
                    on = y in (13, 14) and 1 <= x <= 14 or 5 <= y < 13 and abs(x % 5 - 2) <= (y-5)//3
                elif kind == 6:
                    on = (x in (2, 3, 12, 13) and 3 <= y <= 14) or (y in (2, 3) and 3 <= x <= 12) or (x == 8 and 5 <= y <= 14)
                elif kind == 7:
                    on = x in (0, 15) or y in (0, 15)
                line += "#" if on else "."
            result.append(line)
        return result
    return {"logo": ["CRYSTAL", "TRAIL"], "tagline": "TWO CRYSTALS. ONE WAY OUT.", "sprites": [rows(i) for i in range(8)],
            "music": [18, 18, 25, 9, 30, 9, 25, 18, 0, 6, 22, 18, 29, 9, 34, 9, 29, 18, 0, 6, 255],
            "effects": {"SFX_MOVE": [1, 1, 18, 1], "SFX_USE": [2, 2, 25, 2, 32, 3], "SFX_WIN": [4, 3, 18, 4, 25, 4, 37, 12], "SFX_LOSE": [4, 3, 20, 4, 13, 6, 6, 10]}}


def replay():
    return {"schemaVersion": 1, "demo": "campaign", "scenarios": [
        {"name": "campaign", "steps": [
            {"expect": {"s.mode": 1, "s.player": 9, "s.gems": 0}, "capture": "play"},
            {"press": "D", "repeat": 5, "expect": {"s.mode": 2, "s.player": 14, "s.gems": 2}, "capture": "clear"},
            {"press": "RETURN", "expect": {"s.mode": 1, "s.level": 1}},
            {"press": "S", "repeat": 2},
            {"press": "D", "repeat": 5, "expect": {"s.mode": 2, "s.gems": 2}},
            {"press": "RETURN", "expect": {"s.mode": 4}, "capture": "ending"}]},
        {"name": "failure-retry", "steps": [
            {"press": "S", "expect": {"s.mode": 3}},
            {"press": "RETURN", "confirm": True, "expect": {"s.mode": 1, "s.player": 9, "s.steps": 12}}]},
        {"name": "reset-and-boundary", "steps": [
            {"press": "W", "expect": {"s.player": 9, "s.steps": 12}},
            {"press": "D", "expect": {"s.player": 10}},
            {"press": "SPACE", "confirm": False, "expect": {"s.player": 10}},
            {"press": "SPACE", "confirm": True, "expect": {"s.player": 9, "s.steps": 12}},
            {"ticks": 2, "expect": {"s.player": 9, "s.phase": 0}}]}
    ]}


def create(directory, game_id, title):
    directory = Path(directory).resolve()
    require(not directory.exists(), "Destination already exists.", directory, "Choose a new directory; init never overwrites a project.")
    require(re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", game_id) and len(game_id) <= 64, "Invalid id; use a lowercase hyphenated name of at most 64 characters.")
    from devkit.project import ascii_text, read_json
    require(game_id not in {g["id"] for g in read_json(ROOT / "library.json")["games"]}, "This id is already used by a library game.")
    require(ascii_text(title, 24) and title, "title must be 1-24 uppercase ASCII characters.")
    directory.mkdir(parents=True)
    (directory / "src").mkdir()
    (directory / "src/rules.py").write_text((ROOT / "devkit/templates/collect/rules.py").read_text())
    metadata = {"devkit": 1, "id": game_id, "title": title, "version": "0.1.0", "ramKiB": 16, "entry": 768, "modules": [], "nativeRules": True, "rulesSource": "src/rules.py", "artSource": "art.json", "levels": 2, "rate": 255, "hud": [],
                "help": ["WASD / PAD: MOVE", "COLLECT BOTH CRYSTALS.", "REACH THE GATE BEFORE STEPS=0.", "SPIKES END THE ATTEMPT.", "WALLS DO NOT USE A STEP.", "RETURN / BUTTON: CONTINUE", "SPACE: CONFIRM RESTART"]}
    write_json(directory / "game.json", metadata)
    art = make_art()
    words = title.split()
    if 1 <= len(words) <= 3 and all(re.fullmatch(r"[A-Z0-9]{1,10}", w) for w in words):
        art["logo"] = words
    else:
        letters = re.sub(r"[^A-Z0-9]", "", title) or "NEWGAME"
        art["logo"] = [letters[i:i+10] for i in range(0, len(letters), 10)]
    write_json(directory / "art.json", art)
    levels = []
    for second in (False, True):
        board = [1 if x % 8 in (0, 7) or x < 8 or x >= 56 else 0 for x in range(64)]
        for i in ((25, 27) if second else (11, 13)):
            board[i] = 3
        board[30 if second else 14] = 6
        board[10 if second else 17] = 5
        for i in (35, 36, 43):
            board[i] = 1
        levels.append(board + [9, 14 if second else 12])
    write_json(directory / "levels.json", levels)
    write_json(directory / "tests/replay.json", replay())
    (directory / ".gitignore").write_text("build/\n__pycache__/\n.jr100dev.local.json\n")
    (directory / "Makefile").write_text('JR100DEV_ROOT ?= ../..\nPYTHON ?= $(JR100DEV_ROOT)/.venv/bin/python\nDEV = "$(PYTHON)" "$(JR100DEV_ROOT)/games/dev.py"\n.PHONY: all check test release\nall:\n\t$(DEV) build .\ncheck:\n\t$(DEV) check .\ntest:\n\t$(DEV) test .\nrelease:\n\t$(DEV) release . $(if $(ROM),--rom "$(ROM)",)\n')
    (directory / "README.md").write_text(f'''# {title}

Python DSL から JR-100 の機械語を作る開発用雛形です。Python インタープリターは実機で動きません。

SDK ルートで `python games/dev.py test <このフォルダー>` を実行します。SDK 外からは dev.py の絶対パスを指定します。
Makefile を使う場合は `make JR100DEV_ROOT=/path/to/jr100dev test` と指定できます。

- `src/rules.py`: init / act / tick / draw とゲームのルール
- `game.json`: タイトル、速度、ヘルプ、バージョン
- `levels.json`: 2 面のデータ（各面の末尾は開始位置・歩数）
- `art.json`: 8 個の 16×16 スプライト、タイトル、単音 BGM・効果音
- `tests/replay.json`: 入力列と独立した期待値、撮影地点
- `GAME_DESIGN.md`: 企画・品質確認

操作は WASD / パッド。宝石を 2 個集めて門に着くとクリア、棘または歩数切れで失敗します。
RETURN / ボタンで開始・次へ。SPACE でリセット確認。CTRL+C で BASIC に戻ります。

制作の手順と AI 向け指示書は SDK の `docs/python-games/README.md` を参照してください。
公開前に企画、素材、ルール、テストを自分の作品として仕上げてください。
''', encoding="utf-8")
    (directory / "GAME_DESIGN.md").write_text('''# ゲームの設計

## 一文の遊び
残り歩数を見ながら、棘を避け、宝石を集めて門に向かう。

## 書き換える項目
- プレイヤーが毎回判断すること:
- 成功・失敗条件:
- 一手への画面と音の反応:
- 最初の面で教えること:
- 次の面で増やす判断:
- 成功の入力列 / 失敗の入力列:

## 出荷前の確認
- [ ] 初見で目的・自分・危険・残量が分かる
- [ ] キーを離した後の挙動、壁、残量 0 を確認した
- [ ] 全面クリア、失敗、再挑戦、リセットのテストがある
- [ ] 実 ROM で撮影した画像を開き、動画を再生して操作と音を確認した
- [ ] 画面に制作上の都合やデバッグ値が残っていない
- [ ] 標準 16 KB 内。実機未確認ならその旨を記載した
''', encoding="utf-8")
    (directory / "AGENTS.md").write_text('''# Python game project

Read the SDK docs/python-games/README.md, language.md and ai-workflow.md first.
Keep sources in src/rules.py and authored assets/tests inside this project.
Do not edit generated build/ files or unrelated library games.
Runtime strings must be uppercase ASCII. This is an unsigned-byte DSL, not general Python.
After each rule change, update independent replay expectations and run dev.py test.
Do not weaken assertions to hide a defect. Inspect the diagnostic, fix the source, rerun.
For a release run dev.py release with a user-owned ROM, then inspect all images and play the video.
Never publish a ROM or claim physical-hardware verification from an emulator result.
''')
    return {"project": str(directory), "id": game_id, "next": "test"}
