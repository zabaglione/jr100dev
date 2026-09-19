"""Validate self-contained projects before emitting machine code."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Problem(Exception):
    def __init__(self, code, message, hint, path=None, line=None):
        super().__init__(message)
        self.detail = {"code": code, "message": message, "hint": hint}
        if path is not None:
            self.detail["file"] = str(path)
        if line is not None:
            self.detail["line"] = line


def require(ok, message, path=None, hint="Check the documented project format."):
    if not ok:
        raise Problem("PROJECT", message, hint, path)


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Problem("JSON", str(exc), "Create or repair this JSON file.", path) from exc


def local_file(directory, name):
    require(isinstance(name, str), "Source path must be a string.")
    require(not Path(name).is_absolute() and ".." not in Path(name).parts and "\\" not in name,
            "Source path must stay inside the project using a portable relative path.", name)
    target = (directory / name).resolve()
    require(target.is_relative_to(directory.resolve()), "Source must stay inside the project.", name)
    require(target.is_file(), "Required file is missing.", target)
    return target


def rules_path(directory, metadata):
    return local_file(Path(directory), metadata.get("rulesSource", "rules.py"))


def ascii_text(value, limit=32):
    return isinstance(value, str) and len(value) <= limit and all(32 <= ord(c) <= 95 for c in value)


def byte_list(value, maximum=128):
    return isinstance(value, list) and len(value) <= maximum and all(type(v) is int and 0 <= v <= 255 for v in value)


def validate(directory):
    directory = Path(directory).resolve()
    meta = read_json(directory / "game.json")
    require(isinstance(meta, dict), "game.json must contain an object.")
    require(meta.get("devkit") == 1 and meta.get("nativeRules") is True,
            "This command requires a devkit 1 Python project.", directory / "game.json",
            "Use 'init' for a new project. Existing library games keep their Makefile workflow.")
    require(isinstance(meta.get("id"), str) and re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", meta["id"]), "id must be a lowercase hyphenated name.")
    require(len(meta["id"]) <= 64, "id must contain at most 64 characters.")
    require(ascii_text(meta.get("title"), 24) and meta["title"], "title must be 1-24 uppercase ASCII characters.")
    require(isinstance(meta.get("version"), str) and re.fullmatch(r"\d+\.\d+\.\d+", meta["version"]), "version must be MAJOR.MINOR.PATCH.")
    library = read_json(ROOT / "library.json")
    require(meta["id"] not in {g["id"] for g in library["games"]}, "Choose an id distinct from the existing library games.")
    require(meta.get("ramKiB") == 16 and meta.get("entry") == 768, "Use 16 KiB RAM and entry 768 ($0300).")
    require(meta.get("modules") == [], "Devkit projects use the shared runtime; modules must be [].")
    require(isinstance(meta.get("rulesSource"), str) and isinstance(meta.get("artSource"), str), "Specify rulesSource and artSource as project-local paths.")
    if "sourceUrl" in meta:
        require(isinstance(meta["sourceUrl"], str) and re.fullmatch(r"https://github\.com/zabaglione/jr100dev/tree/[A-Za-z0-9._~/%-]+", meta["sourceUrl"]), "The current public emulator requires a sourceUrl under https://github.com/zabaglione/jr100dev/tree/.", hint="Omit sourceUrl for a standalone release with a source ZIP and manual PRG loading. Add the actual project URL when publishing into the shared catalog.")
    # Advanced library extensions require their own assets and replay adapters.
    for key in ("endless", "carryCampaign", "rankedCampaign", "seededDeck", "packedLevelTail", "sceneEffects", "disableSpaceReset"):
        require(not meta.get(key), f"{key} is not part of the devkit 1 contract.")
    require(meta.get("directions", 4) == 4, "Devkit 1 supports four directions.")
    for key, maximum in (("levels", 128), ("rate", 255)):
        require(type(meta.get(key)) is int and 1 <= meta[key] <= maximum, f"{key} must be 1-{maximum}.")
    help_lines = meta.get("help")
    require(isinstance(help_lines, list) and len(help_lines) <= 8 and all(ascii_text(x, 30) for x in help_lines), "help must contain at most eight 30-character lines.")
    hud = meta.get("hud")
    require(isinstance(hud, list), "hud must be an array of [row, column, text].")
    for row in hud:
        require(isinstance(row, list) and len(row) == 3, "Invalid HUD row.")
        y, x, value = row
        require(type(x) is int and type(y) is int and 0 <= x < 32 and 1 <= y <= 20 and ascii_text(value, 32-x), "HUD text must fit rows 1-20 and columns 0-31.")
    levels = read_json(local_file(directory, "levels.json"))
    require(isinstance(levels, list) and len(levels) == meta["levels"] and all(byte_list(x) for x in levels), "levels.json must match levels; each stage contains at most 128 bytes.")
    tables = meta.get("dataTables", {})
    require(isinstance(tables, dict), "dataTables must be an object.")
    for key, value in tables.items():
        require(re.fullmatch(r"[a-z][a-z0-9_]*", key) and key not in ("s", "b", "c", "d"), "Invalid data table name.")
        require(byte_list(value) and value, f"dataTables.{key} must contain 1-128 bytes.")
    art = read_json(local_file(directory, meta.get("artSource", "art.json")))
    require(isinstance(art, dict), "art.json must contain an object.")
    sprites = art.get("sprites")
    require(isinstance(sprites, list) and len(sprites) == 8 and all(isinstance(p, list) and len(p) == 16 and all(isinstance(row, str) and len(row) == 16 and set(row) <= {'.', '#'} for row in p) for p in sprites), "art.sprites must contain eight 16x16 patterns using '.' and '#'.")
    logo = art.get("logo")
    require(isinstance(logo, list) and 1 <= len(logo) <= 3 and all(isinstance(x, str) and 1 <= len(x) <= 10 and re.fullmatch(r"[A-Z0-9 ]+", x) for x in logo), "art.logo needs 1-3 lines of 1-10 uppercase letters, digits or spaces.")
    require(ascii_text(art.get("tagline"), 30), "art.tagline must fit 30 characters.")
    music = art.get("music")
    require(byte_list(music, 1025) and len(music) >= 3 and len(music) % 2 == 1 and music[-1] == 255 and all(0 <= music[i] <= 47 and 1 <= music[i+1] <= 255 for i in range(0, len(music)-1, 2)), "music must contain pitch (0-47)/duration (1-255) pairs and end with 255.")
    effects = art.get("effects")
    require(isinstance(effects, dict) and set(effects) == {"SFX_MOVE", "SFX_USE", "SFX_WIN", "SFX_LOSE"}, "effects must define SFX_MOVE, SFX_USE, SFX_WIN and SFX_LOSE.")
    for name, values in effects.items():
        require(byte_list(values, 512) and len(values) >= 4 and values[0] > 0 and values[1] > 0 and len(values) == 2 + 2*values[1] and all(0 <= values[i] <= 47 and values[i+1] > 0 for i in range(2, len(values), 2)), f"Invalid priority/count/pitch/duration data in {name}.")
    from devkit.language import validate_source
    validate_source(rules_path(directory, meta), tables)
    return meta


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(directory):
    """Bind results to authored files AND the compiler/runtime/test toolchain."""
    directory = Path(directory)
    meta = read_json(directory / "game.json")
    inputs = [directory / x for x in ("game.json", "levels.json", "tests/replay.json", "README.md", "GAME_DESIGN.md", "Makefile", "AGENTS.md")]
    inputs += [rules_path(directory, meta), local_file(directory, meta.get("artSource", "art.json"))]
    files = [("project/" + str(p.relative_to(directory)), p) for p in inputs]
    for folder in ("native", "common", "devkit", "tests", "media"):
        files += [("sdk/" + str(p.relative_to(ROOT)), p) for p in sorted((ROOT / folder).rglob("*")) if p.suffix in (".py", ".asm", ".inc", ".cpp") and "__pycache__" not in p.parts]
    files += [("sdk/" + name, ROOT / name) for name in ("build_game.py", "dev.py", "library.json")]
    files += [("sdk/pyproject.toml", ROOT.parent / "pyproject.toml")]
    files += [("assembler/" + str(p.relative_to(ROOT.parent / "src")), p) for p in sorted((ROOT.parent / "src").rglob("*.py"))]
    return hashlib.sha256(json.dumps({name: digest(p) for name, p in files}, sort_keys=True).encode()).hexdigest()
