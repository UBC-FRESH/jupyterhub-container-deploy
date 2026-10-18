"""Make the framework scripts and the application package importable from the tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[1]
SCRIPTS: Path = ROOT / "scripts"
for _path in (SCRIPTS, ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
