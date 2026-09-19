"""Failure-oriented tests for the new game authoring contract and release gate."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "games"))
from devkit.cli import main
from devkit.language import model_code, validate_source
from devkit.project import Problem, fingerprint, validate
from devkit.release import deploy, package
from devkit.scaffold import create, write_json
from devkit.verify import load_replay


@pytest.fixture
def project(tmp_path):
    path = tmp_path / "my_game"
    create(path, "sdk-test-game", "CRYSTAL TRAIL")
    return path


def source(tmp_path, statement, functions=""):
    path = tmp_path / "rules.py"
    path.write_text("def init():\n    s.x = 0\ndef act():\n" + "".join("    " + line + "\n" for line in statement.splitlines()) + "def tick(): pass\ndef draw(): pass\n" + functions)
    return path


@pytest.mark.parametrize("statement,code", [
    ("while True:\n    pass", "LANGUAGE"),
    ("s.x = 256", "LANGUAGE"),
    ("s.x = 0.5", "LANGUAGE"),
    ("s.x = [1, 2]", "LANGUAGE"),
    ("s.x = s.typo", "STATE"),
    ("s.x = typo", "UNINITIALIZED"),
    ("s.x = 0 < s.x < 8", "LANGUAGE"),
    ("sound(value=1)", "CALL"),
    ("text(0, 0)", "CALL"),
    ("text(0, 0, '日本語')", "LANGUAGE"),
    ("text(0, 0, 'lowercase')", "LANGUAGE"),
    ("s.x = print(1)", "CALL"),
    ("s.x = 1 // 0", "DIVZERO"),
    ("b[128] = 1", "BOUNDS"),
    ("s.x = b[-1]", "BOUNDS"),
    ("s.x = max(min(1, 2), 3)", "NESTED_CALL"),
    ("s.mode = 2", "LANGUAGE"),
    ("for i in range(0):\n    pass\ns.x = i", "UNINITIALIZED"),
    ("if s.x:\n    n = 2\ns.x = n", "UNINITIALIZED"),
    ("s.x = sound(0)", "LANGUAGE"),
    ("s.x = grid(8, 8, 0, 1)", "LANGUAGE"),
    ("for i in range(4):\n    i = 0", "LOOP"),
    ("for i in range(rand()):\n    pass", "LOOP"),
])
def test_diagnostics_point_at_authored_line(tmp_path, statement, code):
    path = source(tmp_path, statement)
    with pytest.raises(Problem) as error:
        validate_source(path)
    assert error.value.detail["code"] == code
    assert error.value.detail["file"] == str(path)
    assert error.value.detail["line"] >= 4
    assert error.value.detail["hint"]


def test_call_cycles_and_missing_return(tmp_path):
    path = source(tmp_path, "f()", "def f():\n    f()\n")
    with pytest.raises(Problem, match="Recursive"):
        validate_source(path)
    path = source(tmp_path, "s.x = f()", "def f():\n    if s.x:\n        return 1\n")
    with pytest.raises(Problem, match="every path"):
        validate_source(path)


def test_draw_reentry_and_mutation(tmp_path):
    path = source(tmp_path, "pass")
    path.write_text(path.read_text().replace("def draw(): pass", "def draw():\n    f()\ndef f():\n    animate(3)"))
    with pytest.raises(Problem, match="re-enter"):
        validate_source(path)
    path.write_text(path.read_text().replace("animate(3)", "s.x += 1"))
    with pytest.raises(Problem, match="must not change"):
        validate_source(path)


def test_oracle_byte_intermediates_and_short_circuit():
    env = {"_byte": lambda n: int(n) & 255, "_truth": lambda n: int(bool(n))}
    exec(model_code("a=(255+1)//2\nb=(0-1)>5\nc=7 or 0\nd=255\nd+=2\ne=(1-2)%3\nf=(0 and (1//0))", "rules.py"), env)
    assert [env[x] for x in "abcdef"] == [0, True, 1, 1, 0, 0]


def test_project_validation_and_no_overwrite(project):
    validate(project)
    with pytest.raises(Problem, match="already exists"):
        create(project, "sdk-test-game", "OTHER")
    data = json.loads((project / "game.json").read_text())
    data["rulesSource"] = "../outside.py"
    write_json(project / "game.json", data)
    with pytest.raises(Problem, match="inside"):
        validate(project)


def test_level_pointer_index_must_fit_a_byte(project):
    meta = json.loads((project / "game.json").read_text())
    meta["levels"] = 129
    write_json(project / "game.json", meta)
    with pytest.raises(Problem, match="levels must be 1-128"):
        validate(project)


@pytest.mark.parametrize("mutation", [
    lambda art: art["sprites"][0].pop(),
    lambda art: art.update(music=[48, 5, 255]),
    lambda art: art.update(music=[18, 0, 255]),
    lambda art: art["effects"].update(SFX_MOVE=[1, 2, 18, 1]),
])
def test_bad_art_is_rejected_before_assembly(project, mutation):
    art = json.loads((project / "art.json").read_text())
    mutation(art)
    write_json(project / "art.json", art)
    with pytest.raises(Problem):
        validate(project)


def test_replay_requires_real_assertions_and_safe_capture_names(project):
    data = load_replay(project)
    data["scenarios"][0]["steps"] = [{"press": "D"}]
    write_json(project / "tests/replay.json", data)
    with pytest.raises(Problem, match="independent"):
        load_replay(project)
    data["scenarios"][0]["steps"] = [{"expect": {"s.mode": 1}, "capture": "../../outside"}]
    write_json(project / "tests/replay.json", data)
    with pytest.raises(Problem, match="capture"):
        load_replay(project)


def test_failed_build_invalidates_old_test_receipt(project, capsys):
    receipt = project / "build/devkit/test.json"
    write_json(receipt, {"status": "passed"})
    (project / "src/rules.py").write_text("import os\n")
    assert main(["--json", "release", str(project)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["stage"] == "check" and result["error"]["code"] == "LANGUAGE"
    assert not receipt.exists()
    assert not (project / "build/release").exists()


def test_fingerprint_includes_rules_assets_and_replay(project):
    hashes = [fingerprint(project)]
    for name in ("src/rules.py", "art.json", "tests/replay.json"):
        with (project / name).open("a") as stream:
            stream.write("\n")
        hashes.append(fingerprint(project))
    assert len(set(hashes)) == 4


def test_package_rejects_stale_prg(project):
    build = project / "build"
    write_json(build / "devkit/test.json", {"status": "passed", "fingerprint": fingerprint(project), "prg_sha256": "old"})
    write_json(build / "devkit/capture.json", {"status": "passed", "fingerprint": fingerprint(project), "prg_sha256": "old"})
    (build / "sdk-test-game.prg").write_bytes(b"changed")
    with pytest.raises(Problem, match="stale"):
        package(project)


def test_deploy_preserves_other_games_and_rejects_bad_catalog(tmp_path):
    bundle, web = tmp_path / "bundle", tmp_path / "web"
    for catalog in ("games/catalog.json", "game-media/catalog.json"):
        write_json(bundle / catalog, {"schemaVersion": 1, "games": [{"id": "new-game"}]})
        write_json(web / catalog, {"schemaVersion": 1, "games": [{"id": "other-game"}]})
    (bundle / "game-media/new-game").mkdir()
    (bundle / "game-media/new-game/play.mp4").write_bytes(b"example")
    deploy(bundle, web)
    assert [g["id"] for g in json.loads((web / "games/catalog.json").read_text())["games"]] == ["other-game", "new-game"]
    (web / "games/catalog.json").write_text("broken")
    before = (web / "game-media/new-game/play.mp4").read_bytes()
    (bundle / "game-media/new-game/play.mp4").write_bytes(b"new")
    with pytest.raises(Problem):
        deploy(bundle, web)
    assert (web / "game-media/new-game/play.mp4").read_bytes() == before


def test_deploy_rejects_symlink_escape(tmp_path):
    bundle, web, outside = tmp_path / "bundle", tmp_path / "web", tmp_path / "outside"
    outside.mkdir()
    web.mkdir()
    for catalog in ("games/catalog.json", "game-media/catalog.json"):
        write_json(bundle / catalog, {"schemaVersion": 1, "games": [{"id": "new-game"}]})
    (web / "games").symlink_to(outside, target_is_directory=True)
    with pytest.raises(Problem, match="escapes"):
        deploy(bundle, web)
    assert list(outside.iterdir()) == []


def test_deploy_rolls_back_file_failure(tmp_path, monkeypatch):
    bundle, web = tmp_path / "bundle", tmp_path / "web"
    for catalog in ("games/catalog.json", "game-media/catalog.json"):
        write_json(bundle / catalog, {"schemaVersion": 1, "games": [{"id": "new-game"}]})
        write_json(web / catalog, {"schemaVersion": 1, "games": [{"id": "other-game"}]})
    (bundle / "image.png").write_bytes(b"new")
    (web / "image.png").write_bytes(b"old")
    before = {str(p.relative_to(web)): p.read_bytes() for p in web.rglob("*") if p.is_file()}
    replace = Path.replace
    def fail(self, target):
        if str(target).endswith("games/catalog.json"):
            raise OSError("Injected write failure")
        return replace(self, target)
    monkeypatch.setattr(Path, "replace", fail)
    with pytest.raises(OSError, match="Injected"):
        deploy(bundle, web)
    assert {str(p.relative_to(web)): p.read_bytes() for p in web.rglob("*") if p.is_file()} == before


def test_public_http_hash_check_detects_changed_artifact(project):
    from functools import partial
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    import threading
    from devkit.project import digest
    from devkit.published import verify

    bundle = project / "build/release"
    artifact = bundle / "game-media/sdk-test-game/play.mp4"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"verified example media")
    write_json(artifact.parent / "manifest.json", {"fingerprint": fingerprint(project), "files": {"game-media/sdk-test-game/play.mp4": digest(artifact)}})
    web = project / "build/web"
    import shutil
    shutil.copytree(bundle, web)
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(web)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/"
        assert verify(project, url)["verified_files"] == 1
        (web / "game-media/sdk-test-game/play.mp4").write_bytes(b"changed")
        with pytest.raises(Problem, match="Published hash differs"):
            verify(project, url)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
