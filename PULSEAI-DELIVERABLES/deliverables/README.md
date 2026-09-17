# ValveGuard

Hackathon research prototype for bioprosthetic aortic-valve **surveillance
decision support**. It is **not** a clinically validated SaMD. It does not
diagnose SVD. It never recommends an intervention.

A consumer laptop can run the browser UI and the PulseAI engine on CPU.
Inference does **not** need a GPU, Tailscale, or a second machine.

## Judge deliverables

| File | What it is |
|---|---|
| [`README.md`](README.md) | This file: product map and laptop deploy |
| [`data.md`](data.md) | Data contract, labels, missingness, governance |
| [`approach.md`](approach.md) | Five-tier model, I/O, validation, limits |
| [`notebooks/`](notebooks/) | Deploy the demo and run the **same** Python engine |
| [`deliverables/presentation-ValveGuard.pptx`](deliverables/presentation-ValveGuard.pptx) | Team presentation deck |

## Presentation laptop (browser app)

1. Install [Python 3.11–3.13](https://www.python.org/downloads/) for Windows.
   Tick **Add python.exe to PATH**.
2. On a network, clone and create an isolated environment (PyTorch CPU is the
   large download, often 150–250 MB):

```powershell
git clone https://github.com/hatjipapask-lab/ValveGuard.git
cd ValveGuard
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r backend\requirements.txt
```

3. Start both local servers from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-demo.ps1
```

From the notebooks folder the same launcher is:

```powershell
powershell -ExecutionPolicy Bypass -File .\notebooks\start_demo.ps1
```

Or in two terminals:

```powershell
python -m backend
python -m http.server 4173 --directory valveguard-client
```

4. Open **http://127.0.0.1:4173** (use `127.0.0.1`, not `localhost`).
5. Sign in with `clinician@valveguard.demo` / `1234`.
6. Choose one of the four synthetic showcases, then **Run five-tier inference**.

The sidebar should read **Inference API ready** with artifact
`20260917T121953Z`.

If PowerShell blocks scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Jupyter is optional. To walk the engine in notebooks after the venv exists:

```powershell
python -m pip install -r notebooks\requirements.txt
jupyter notebook notebooks
```

## What the product actually is

Five Python subengines, one FastAPI process, one static browser client:

| Piece | Program | Role |
|---|---|---|
| Thin client | `valveguard-client/` | Collects the study chart; packs `EngineInput` (`pulseai.engine-input/1.2`) |
| API | `backend/app.py` | Loopback `:8000`; `POST /v1/inference` |
| Runtime | `backend/runtime.py` | Loads hashed checkpoints; withholds unsupported heads |
| Tier 1 | `model/tier1_varc3_rules.py` | VARC-3 **candidate** HVD (not SVD) |
| Tier 2 | `model/tier2_dynamic_competing_risk.py` | Dynamic-DeepHit GRU: SVD-related BVF vs death vs NSVD |
| Tier 3 | `model/tier3_longitudinal_progression.py` | Echo trajectory GRU; progression withheld (no labels) |
| Tier 4 | `model/tier4_calibration_safety.py` | Isotonic calibration + abstention |
| Tier 5 | `model/tier5_surveillance_policy.py` | Draft policy; `intervention_recommendation` is always `null` |
| Diagram | `backend/trajectory.py` | Reshapes Tier 2/4 curves for the client |

The deterioration tensor is **26 static** + **12 per visit**. STS-PROM and
EuroSCORE II stay on the study record. Omitted alternative-cause flags stay
unknown (`null`), not `false`. Twelve-month follow-up is **study inclusion**,
not a landmark gate.

Prototype labels: **1,408** eligible synthetic patients; **126 Stage-3
hemodynamic templates** on the BVF clock (**not CEC BVF**); NSVD is
structurally unsupported. Metrics in the artifact bundle are internal
synthetic checks, not clinical performance.

## Why this architecture

| Piece | Where it runs | Why |
|---|---|---|
| Thin client | Browser at `:4173` | Static HTML/CSS/JS. No Node, no GPU. |
| FastAPI orchestrator | Python at `:8000` | Loads checkpoints once, serves `/v1/inference`. |
| PulseAI Tiers 1–5 | Same Python process, CPU | Compact Torch GRU. Laptop RAM ~2–4 GB while loaded. |

Do not bind the API to `0.0.0.0` for this demo. Loopback keeps the
prototype off the cellular interface.

## Repository map

- `valveguard-client/` — browser UI
- `backend/` — FastAPI, training, artifacts
- `backend/artifacts/synthetic-poc-v1/` — fitted demo bundle (format v3)
- `model/` — five-tier engine
- `data.md` / `approach.md` — judge data and model documents
- `notebooks/` — laptop deploy + engine walkthrough
- `data/` — workbooks are gitignored; `data_plan.md` mirrors `data.md`

## Retrain (optional)

Not required for the talk. If `data/notes_expanded.xlsx` is present:

```powershell
python -m backend.train --overwrite
```

## Tests (optional)

```powershell
python -m unittest discover -s backend/tests -v
```
