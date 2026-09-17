"""Resolve the ValveGuard repository root from a notebook or script."""

from __future__ import annotations

import sys
from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent,
        Path.cwd(),
        Path.cwd().parent,
        here,
    ]
    for path in candidates:
        if (path / "model" / "pulseai_engine.py").is_file():
            resolved = path.resolve()
            if str(resolved) not in sys.path:
                sys.path.insert(0, str(resolved))
            return resolved
    raise RuntimeError(
        "Could not find model/pulseai_engine.py. Open the notebook from the "
        "ValveGuard repository (root or notebooks/)."
    )


ROOT = repo_root()
ARTIFACT_DIR = ROOT / "backend" / "artifacts" / "synthetic-poc-v1"
CLIENT_DIR = ROOT / "valveguard-client"
NOTES_WORKBOOK = ROOT / "data" / "notes_expanded.xlsx"
LABS_WORKBOOK = ROOT / "data" / "labs_expanded.xlsx"
