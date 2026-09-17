# Notebooks — proof of concept

These notebooks describe and call the **ValveGuard** engine. They do not reimplement PulseAI, do not use XGBoost/SHAP, and do not claim clinical performance.

This Dyania fork contains **documents and notebooks only**. To execute them, clone:

https://github.com/hatjipapask-lab/ValveGuard

Then install `backend/requirements.txt` and `notebooks/requirements.txt` in that repository.

## What is here

| Notebook | What it is for |
|---|---|
| `00_deploy_demo.ipynb` | Start the loopback API and static UI |
| `01_data_contract.ipynb` | Tensor contract and label audit |
| `02_five_tier_engine.ipynb` | Tiers 1–5 on synthetic showcases |
| `03_metrics_safety.ipynb` | Technical metrics and fail-closed Stage 3 |

No patient workbooks are included in this public repository.
