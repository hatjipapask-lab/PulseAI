# Dyania Health Hackathon 2026 — Team PulseAI

**Challenge:** Build a study — using machine learning, a statistical model, or whatever approach you prefer — proposing a protocol to predict aortic valve durability in patients with a bioprosthetic aortic valve replacement.
**Event:** September 15–17, 2026 (3 days)
**Team size:** 2–3
**Team:** PulseAI
**Model:** ValveGuard
**Members:** Athanasiou-Paraskevopoulou Maria — Medical Student; Chatzipapas Konstantinos — Electrical & Computer Engineering Student; Myaris Stylianos — Informatics Student

Runnable engine (not this fork): https://github.com/hatjipapask-lab/ValveGuard

---

## Problem Statement

Bioprosthetic aortic valves fail silently. Annual follow-up is too rigid for younger SAVR/TAVR recipients who may outlive the prosthesis, and a large fraction of patients drop out of surveillance once they feel well. Late identification of structural valve deterioration (SVD) presents as emergency reintervention, with higher mortality than planned redo. ValveGuard is a five-tier surveillance CDSS: VARC-3 candidate detection first, competing-risk and echo-trajectory models only on eligible cases, then calibration/abstention and a clinician-owned review interval. It does not diagnose SVD and never recommends an implant or reintervention.

## Our Approach

The intended study uses serial echocardiography (30–90-day reference TTE plus later studies), implant/registry fields, selected labs, and CEC-adjudicated events. This hackathon prototype trains and infers on expanded synthetic notes (1,500 linked patients; **1,408** engine-eligible after reference TTE, later echo, and a 12-month study-inclusion extract) plus a small de-identified workbook inventory that is **not** used as labels. Year-only lab dates are not joined. The executable model is a frozen five-layer pipeline (rules → Dynamic-DeepHit-style CIF → trajectory GRU → isotonic safety → draft surveillance policy). Actionable output is `review_now` / `3_months` / `6_months` / `standard_interval`, or an explicit abstention that is never shown as low risk.

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Candidate HVD ≠ SVD; CEC labels in the full study | Tier 1 is a deterministic VARC-3 screen. Training labels require independent adjudication of date, stage, and etiology. |
| Competing-risk landmark model, not a fixed-date classifier | Death and non-structural failure censor BVF. Stage 2 stays on the BVF clock; Stage 3 leaves it. |
| 26 static + 12 longitudinal slots; STS/EuroSCORE off-tensor | The engine receives one `EngineInput` (`pulseai.engine-input/1.2`). Surgical scores stay on the study record for an exploratory operability note only. |
| Missingness masks and fail-closed safety | Null is not “no”. >40% missing or Stage 3/indeterminate current HVD withholds numeric BVF risk. Draft policy stays `review_now` until a clinician group is recorded. |
| Synthetic PoC is not clinical performance | 126 Stage-3 hemodynamic templates are mapped onto the BVF clock (not CEC). NSVD is structurally untrained. No real PHI in this public fork. |

---

## Getting Started

> **Do not upload real patient data or clinical notes to this repository.**

This branch is the Dyania **document** submission. To run the laptop demo, clone ValveGuard, install `backend/requirements.txt`, and start `start-demo.ps1` (UI at http://127.0.0.1:4173). Notebooks in this fork import that engine; they will not train or infer from these files alone.

### Submit — Pull Request

Push `team/PulseAI` to the fork and open a Pull Request against `dyaniahealth/dyania-hackathon-avr-durability` `main`. Title: `Team submission: PulseAI`. **Do not merge.**

> **Deadline: September 17, 2026 — before the presentation session.**
> Only the last commit pushed before the deadline will be evaluated.

---

## Repository Structure

```
.
├── README.md
├── protocol/study_protocol.md     # plus Protocol (2).docx
├── model/approach.md              # also copied to ml/approach.md
├── data/data_plan.md
├── presentation/slides.pptx       # export to slides.pdf if the panel requires PDF
└── notebooks/                     # walkthrough; runtime is ValveGuard
```

---

## Submission Checklist

- [x] `README.md` — team overview, problem framing, key design decisions
- [x] `protocol/study_protocol.md` — complete study protocol
- [x] `model/approach.md` / `ml/approach.md` — ML methodology
- [x] `data/data_plan.md` — data plan
- [x] `presentation/slides.pptx` — slide deck (PDF export if PowerPoint is available locally)
- [x] `notebooks/` — proof-of-concept walkthrough (engine lives in ValveGuard)
