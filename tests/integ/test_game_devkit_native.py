"""Exercise a newly scaffolded game through the public CLI and native CPU."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
EMU = Path(os.environ.get("JR100EMU_ROOT", str(Path.home() / "jr100emu")))
pytestmark = pytest.mark.skipif(not shutil.which("c++") or not (EMU / "cpp/src/core.cpp").is_file(), reason="Requires C++20 and JR100EMU_ROOT; run dev.py doctor")


def cli(*args):
    result = subprocess.run([sys.executable, str(ROOT / "games/dev.py"), "--json", *map(str, args)], capture_output=True, text=True, cwd=ROOT, timeout=120)
    return result.returncode, json.loads(result.stdout)


def test_scaffold_failure_fix_native_replay_and_byte_model(tmp_path):
    project = tmp_path / "unrelated-folder-name"
    code, report = cli("init", project, "--id", "native-devkit-test")
    assert code == 0 and report["status"] == "passed"
    source = project / "src/rules.py"
    original = source.read_text()
    # The public command must fail before build/capture/deployment, with a line.
    source.write_text(original.replace("s.gems = 0", "s.gems = 300"))
    code, report = cli("release", project, "--web-root", tmp_path / "web")
    assert code == 1 and report["stage"] == "check"
    assert report["error"]["line"] == 11
    assert not (tmp_path / "web").exists()
    # Independent expected results catch normal-Python vs byte-DSL differences.
    source.write_text(original.replace("s.gems = 0", "s.gems = 0\n    s.wrap = (255 + 1) // 2\n    s.borrow = (0 - 1) > 5\n    local = 255\n    local += 2\n    s.local = local\n    s.truth = 7 or 0"))
    replay_path = project / "tests/replay.json"
    replay = json.loads(replay_path.read_text())
    replay["scenarios"][0]["steps"][0]["expect"].update({"s.wrap": 0, "s.borrow": 1, "s.local": 1, "s.truth": 1})
    replay_path.write_text(json.dumps(replay))
    code, report = cli("test", project)
    assert code == 0, report
    evidence = json.loads((project / "build/devkit/test.json").read_text())
    assert len(evidence["scenarios"]) == 6 and evidence["mixed_inputs"] == 160
    assert all(x["pass"] for x in evidence["scenarios"])
    assert (project / "build/native-devkit-test.prg").read_bytes().startswith(b"PROG")
    # An incorrect expected success must fail, not just agree with the model.
    replay["scenarios"][0]["steps"][1]["expect"]["s.gems"] = 1
    replay_path.write_text(json.dumps(replay))
    code, report = cli("test", project)
    assert code == 1 and report["error"]["code"] == "REPLAY"
    assert "expected 1, actual 2" in report["error"]["message"]
    assert not (project / "build/devkit/test.json").exists()
