#!/usr/bin/env python3
"""One entry point for new Python DSL game projects (see --help)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from devkit.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
