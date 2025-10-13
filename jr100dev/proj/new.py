"""Project scaffolding helpers for `jr100dev new`."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


class ProjectGenerationError(RuntimeError):
    """Raised when project scaffolding fails."""


@dataclass
class ProjectScaffoldResult:
    root: Path
    created: List[Path]


def create_project(target: Path, *, force: bool = False) -> ProjectScaffoldResult:
    """Create a new project skeleton under `target`.

    The structure includes:
      - `jr100.toml` configuration
      - `src/main.asm` sample program that uses standard macros
      - `std/macro.inc` (copied from the packaged standard macros)
      - `.gitignore` ignoring build artefacts
      - empty `build/` directory
    """

    target = target.expanduser().resolve()
    if target.exists():
        if not target.is_dir():
            raise ProjectGenerationError(f"{target} はディレクトリではありません")
        if not force and any(target.iterdir()):
            raise ProjectGenerationError(f"{target} は既に存在し、空ではありません (--force で上書き可)")
    else:
        target.mkdir(parents=True)

    created: List[Path] = []

    def ensure_dir(path: Path) -> None:
        if not path.exists():
            path.mkdir(parents=True)
            created.append(path)
        elif not path.is_dir():
            raise ProjectGenerationError(f"{path} はディレクトリではありません")

    ensure_dir(target / "src")
    ensure_dir(target / "std")
    ensure_dir(target / "build")

    _write_file(target / "jr100.toml", _config_template_path(), force, created)
    _write_file(target / "src" / "main.asm", _main_template_path(), force, created)
    _write_file(target / "std" / "macro.inc", _macro_template_path(), force, created)
    _write_file(target / ".gitignore", _gitignore_template_path(), force, created)

    return ProjectScaffoldResult(root=target, created=created)


def _write_file(dest: Path, source: Path, force: bool, created: List[Path]) -> None:
    if dest.exists() and not force:
        raise ProjectGenerationError(f"{dest} は既に存在します (--force で上書き可)")
    dest.parent.mkdir(parents=True, exist_ok=True)
    content = source.read_text(encoding="utf-8")
    dest.write_text(content, encoding="utf-8")
    created.append(dest)


def _module_path(relative: Iterable[str]) -> Path:
    base = Path(__file__).resolve().parent
    for part in relative:
        base = base / part
    return base


def _config_template_path() -> Path:
    return _module_path(["jr100.toml"])


def _main_template_path() -> Path:
    return _module_path(["templates", "main.asm"])


def _macro_template_path() -> Path:
    std_dir = Path(__file__).resolve().parent.parent / "std" / "macro.inc"
    return std_dir


def _gitignore_template_path() -> Path:
    return _module_path(["templates", "gitignore"])
