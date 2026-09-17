"""Index of the Python programs the notebooks actually call.

These are the product files, not copies. Changing a notebook must not fork
a second engine.
"""

from __future__ import annotations

import sys
from pathlib import Path

_NOTEBOOKS = Path(__file__).resolve().parent
if str(_NOTEBOOKS) not in sys.path:
    sys.path.insert(0, str(_NOTEBOOKS))

from _paths import ROOT


ENGINE_PROGRAMS: tuple[tuple[str, str], ...] = (
    ("model/tier1_varc3_rules.py", "Tier 1 VARC-3 candidate rules (exclusive thresholds, tri-state flags)"),
    ("model/tier2_dynamic_competing_risk.py", "Tier 2 Dynamic-DeepHit GRU, 26 static + 12 visit slots, format v3"),
    ("model/tier3_longitudinal_progression.py", "Tier 3 trajectory GRU; progression head withheld without labels"),
    ("model/tier4_calibration_safety.py", "Tier 4 isotonic calibration and abstention gates"),
    ("model/tier5_surveillance_policy.py", "Tier 5 draft surveillance policy; never recommends intervention"),
    ("model/pulseai_engine.py", "Wires Tiers 1-5 into one EngineInput / EngineResult call"),
)

JUDGE_PROGRAMS: tuple[tuple[str, str], ...] = (
    ("backend/runtime.py", "Loads hashed artifacts, withholds unsupported NSVD/LVEF/progression heads"),
    ("backend/trajectory.py", "Builds the Tier 2/4 risk-trajectory diagram for the browser"),
    ("backend/data_pipeline.py", "Synthetic parser, NSVD audit, lab-join refusal, sample construction"),
    ("backend/train.py", "Optional retrain/package of synthetic-poc-v1"),
    ("backend/app.py", "FastAPI loopback API used by the thin client"),
    ("valveguard-client/contract.js", "Browser packer for pulseai.engine-input/1.2"),
    ("start-demo.ps1", "Laptop dual-server launcher"),
    ("notebooks/launch_demo.py", "Cross-platform loopback launcher used by 00_deploy_demo.ipynb"),
)


def listed_paths() -> list[Path]:
    return [ROOT / relative for relative, _ in ENGINE_PROGRAMS + JUDGE_PROGRAMS]


def missing() -> list[str]:
    return [str(path) for path in listed_paths() if not path.is_file()]


if __name__ == "__main__":
    print("Engine programs")
    for relative, role in ENGINE_PROGRAMS:
        print(f"  {relative:42} {role}")
    print("Programs judges also use")
    for relative, role in JUDGE_PROGRAMS:
        print(f"  {relative:42} {role}")
    absent = missing()
    if absent:
        raise SystemExit("missing: " + "; ".join(absent))
    print("all listed files exist")
