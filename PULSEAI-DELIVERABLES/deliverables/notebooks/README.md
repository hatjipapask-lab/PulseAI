# notebooks — judge walkthrough of the **running product**

These notebooks import the repository engine. They do **not** reimplement
PulseAI, they do **not** use XGBoost/SHAP, and they do **not** claim clinical
performance.

## Deploy the browser app (no Jupyter required)

From the repo root, after `python -m pip install -r backend/requirements.txt`:

```powershell
powershell -ExecutionPolicy Bypass -File .\notebooks\start_demo.ps1
```

or

```powershell
python notebooks\launch_demo.py
```

Then open **http://127.0.0.1:4173** (not `localhost`).

- Email: `clinician@valveguard.demo`
- Password: `1234`
- Load a synthetic showcase → **Run five-tier inference**

Expected artifact id: `20260917T121953Z`.

## Notebooks

| Notebook | What it runs |
|---|---|
| `00_deploy_demo.ipynb` | Starts `:8000` + `:4173` and checks `/health/ready` |
| `01_data_contract.ipynb` | Manifest label audit, 26/12 tensor names, optional workbook parse |
| `02_five_tier_engine.ipynb` | Real Tiers 1–5 on the four synthetic showcases |
| `03_metrics_safety.ipynb` | Artifact metrics (technical only) and fail-closed Stage 3 |

```powershell
python -m pip install -r notebooks\requirements.txt
jupyter notebook notebooks
```

If Jupyter is unavailable, run the same Python:

```powershell
python notebooks\launch_demo.py --no-browser
python notebooks\engine_index.py
python -m unittest discover -s backend/tests -v
```

## Selected programs (not copies)

Engine:

- `model/tier1_varc3_rules.py`
- `model/tier2_dynamic_competing_risk.py`
- `model/tier3_longitudinal_progression.py`
- `model/tier4_calibration_safety.py`
- `model/tier5_surveillance_policy.py`
- `model/pulseai_engine.py`

Also used by judges:

- `backend/runtime.py`
- `backend/trajectory.py`
- `backend/data_pipeline.py`
- `backend/app.py`
- `valveguard-client/contract.js`
- `start-demo.ps1`

`python notebooks/engine_index.py` prints that list and checks the files exist.

## Environment

Demo:

```
python >= 3.11
pandas, openpyxl, torch (CPU), fastapi, uvicorn, httpx
```

Notebook extras: `jupyter`, `ipykernel`, `matplotlib`.

There is no `xgboost`, `lifelines`, or `shap` in this product.
