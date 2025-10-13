from pathlib import Path
from types import SimpleNamespace

import pytest

from jr100dev.cli.main import run_new


def _macro_template() -> str:
    template_path = Path(__file__).resolve().parents[2] / "std" / "macro.inc"
    return template_path.read_text(encoding="utf-8")


def test_new_project_creates_skeleton(tmp_path):
    target = tmp_path / "demo"
    args = SimpleNamespace(path=target, force=False)
    rc = run_new(args)
    assert rc == 0

    assert (target / "jr100.toml").exists()
    assert (target / "src" / "main.asm").exists()
    assert (target / "std" / "macro.inc").exists()
    assert (target / ".gitignore").exists()

    main_text = (target / "src" / "main.asm").read_text(encoding="utf-8")
    assert ".org $0246" in main_text
    assert '.include "macro.inc"' in main_text
    macro_text = (target / "std" / "macro.inc").read_text(encoding="utf-8")
    assert macro_text == _macro_template()


def test_new_project_requires_empty_dir(tmp_path, capsys):
    target = tmp_path / "demo"
    target.mkdir()
    (target / "existing.txt").write_text("keep", encoding="utf-8")

    args = SimpleNamespace(path=target, force=False)
    rc = run_new(args)
    assert rc == 1
    stderr = capsys.readouterr().err
    assert "Project generation failed" in stderr

    args_force = SimpleNamespace(path=target, force=True)
    rc_force = run_new(args_force)
    assert rc_force == 0
    assert (target / "jr100.toml").exists()
