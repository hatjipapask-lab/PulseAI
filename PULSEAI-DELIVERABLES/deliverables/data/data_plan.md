# data.md

ValveGuard / PulseAI **data deliverable**. Same contract as `data/data_plan.md`. Inspect it live in `notebooks/01_data_contract.ipynb`. Source workbooks are gitignored; fitted checkpoints live in `backend/artifacts/synthetic-poc-v1/`.

PulseAI separates the **optimized study dataset the engine requires** from the **two data sources available for this hackathon prototype**. The prototype can demonstrate training and end-to-end inference; it cannot establish clinical performance.

---

## 1. Data Sources — Real Deployment

| Source | Data Type | Access Pathway | Variables Used |
|---|---|---|---|
| EHR / valve registry | Structured tables and clinical notes | FHIR/SQL extract through institutional data warehouse | Age, sex, BMI/BSA, comorbidities, symptoms, renal/mineral markers |
| Surgical and cath-lab records | Procedure tables and operative reports | STS/TVT or local procedural registry | SAVR/TAVR, implant date, valve manufacturer/model/size, access, concomitant procedures |
| Longitudinal echo system | DICOM-SR and validated report extraction | PACS/CVIS | Mean gradient, Vmax, EOA/EOAi, DVI, intraprosthetic AR, LVEF |
| Laboratory and medication records | Timestamped observations/orders | FHIR/SQL | Creatinine/eGFR, calcium/phosphate, NT-proBNP, anticoagulant/antiplatelet/diuretic classes |
| Death and reintervention registries | Outcome dates and procedure records | Linked registry/claims through an honest broker | Death, redo SAVR, ViV-TAVR, explant, last verified follow-up |

The full study target is **2,500–3,000 patients**, **10,000–15,000 patient-years**, and at least **150–200 adjudicated SVD-related BVF events**. The **executable engine** never sees the entire EHR: it receives one `EngineInput` (reference TTE, current TTE, 26 static slots, 12 longitudinal slots per visit, visit times/availability, clinical context, adjudicated progression state). Section 3 lists that payload in the optimal fill versus a realistic incomplete fill. Tier 3 training additionally needs future gradient, Vmax, EOA, DVI, LVEF, and AR targets. Missing tensor cells are allowed; two or more serial echoes are required to form a landmark. Protocol study inclusion uses ≥12 months of follow-up; that is not a landmark eligibility gate.

---

## 2. Data Sources — Prototype / Hackathon

| Dataset | Size Used | Why Selected | Limitations as Proxy |
|---|---|---|---|
| **De-identified real-world prototype:** `notes_deidentified(1).xlsx`, `labs_deidentified(1).xlsx`, `medications_deidentified(1).xlsx` | 215 notes / 117 patients; 43,550 lab rows and 5,807 medication rows / 17 patients; 17 patients link across all three files | Provides realistic note structure, missingness, coding variation, laboratory records, and medication histories | Small linked cohort; year-level dates; incomplete echo fields; note mentions are not automatically adjudicated labels |
| **Expanded synthetic cohort:** `notes_expanded.xlsx`, `labs_expanded.xlsx`, `medications_expanded.xlsx` | 13,834 notes, 95,908 labs, and 4,258 medications / 1,500 linked patients; 10,834 TTEs / 1,496 patients | Supplies complete linkage, repeated follow-up, and controlled first-event/trajectory examples | Artificial patterns may make performance optimistic; no TTE LVEF, explicit non-SVD removal class, or reliable Stage 2→3/BVF sequence |

The union contains up to **1,617 patient IDs**, but only **1,517** link across notes, labs, and medications. After the 30–90-day reference, later-echo, and protocol **study-inclusion** 12-month extract, **1,408** synthetic patients are engine-eligible. The 12-month cut is a cohort filter, not a landmark gate: included patients may still have earlier landmarks. The expanded lab workbook was inspected and **not joined** (`Result Date` is a calendar year; echo landmarks are fractional years from implant). eGFR/calcium/phosphate stay `null` in training unless a live client request supplies those labs. Synthetic data are not treated as external validation.

---

## 3. What the ML engine actually receives

The thin client may hold a full study chart (demographics, implant, echoes, labs, medications, outcomes, adjudication, governance). **Inference packs only `EngineInput`.** Fields that stay on the study record and never enter the **deterioration tensor** include symptoms/NYHA, CAD, hypertension, creatinine, NT-proBNP, medication rows, access route, center ID, manufacturer free text, STS-PROM, EuroSCORE II, outcome/censoring rows, and governance checkboxes. Repeat-echo status and physician forecast feedback are confirmation/evaluation fields, not GRU features.

Hard requirements to *construct* a request: dated 30–90-day reference TTE, at least one later dated TTE, landmark day count matching current minus reference, visit 0 at time zero, no outcome-supporting echo in the history, and (in the product client) current alternative-cause flags as yes or no.

The Python engine itself requires only `baseline_echo`, `current_echo`, and `history`. Omitted alternative-cause keys stay unknown (`null`); they are never coerced to `false`. The 30–90-day window is a **client hard error**; if implant-to-reference days are supplied to Tier 1 outside that window, the engine still runs and records `reference_tte_outside_30_90_day_window`. Follow-up shorter than 12 months is a **study-inclusion** warning, not a landmark reject. Implant date is not a tensor feature; only the derived day counts enter `clinical_context`. Reference hemodynamics are duplicated: `baseline_echo` for VARC-3 and the `baseline_*` static slots plus visit 0 for the GRUs.

### a) Optimal scenario — every intended slot filled

| Block | Patient input the engine receives |
|---|---|
| Identity / implant | Pseudonymous ID (audit only); age at implant; sex encoded as female=1 / male=0; BMI kg/m²; BSA m²; SAVR vs TAVR; nominal size mm; valve-model index from the frozen vocabulary; architecture flags (stented, sutureless, externally mounted leaflets); implant-to-reference and implant-to-current days |
| Reference TTE (30–90 d) | Date; mean gradient; Vmax; EOA; EOAi (or EOA/BSA); DVI; intraprosthetic AR 0–4; LVEF; same values copied into the 12-slot visit-0 vector; occurrence and availability at day 0 |
| Serial follow-up | One or more later TTEs with the same 7 hemodynamics; visit times in days from reference; availability ≤ landmark; exclusive NSVD-member flags known (0/1) when documented |
| Current (landmark) TTE | Same hemodynamic set; **clinical_context** tri-state flags resolved: thrombosis, endocarditis, isolated PVL, malposition, high-flow = true/false; BMI for PPM |
| Baseline clinical | Diabetes; CKD ≥3; bicuspid anatomy; chest radiation; concomitant CABG or aortic procedure |
| Labs at/before landmark | Latest eGFR, serum calcium, serum phosphate |
| Confirmation / policy (not GRU) | Repeat-echo confirmation; physician prior-forecast feedback; `current_progression_state` |
| Derived | `severe_ppm` from EOAi and BMI (≤0.65, or ≤0.55 if BMI ≥30) |

Training (not shown at inference) additionally needs the first **CEC-adjudicated** event after the landmark. The prototype instead maps generator Stage-3 hemodynamic templates onto the BVF clock.

### b) Realistic scenario — same schema, many `null`s

The JSON keys do not change. Missing measurements stay `null` and become masks. Zero is never used as a filler for an unobserved clinical value.

| Typically present | Typically absent / masked | Still collected but **not** sent to the deterioration tensor |
|---|---|---|
| Implant date, SAVR/TAVR, age, sex if female/male, valve size, BSA | BMI (PPM then unevaluable) | Height, weight (except when used to compute BMI/BSA before packing) |
| Dated reference TTE in 30–90 d and ≥1 later TTE | LVEF on every TTE (always missing in synthetic training) | NYHA, dyspnea, angina, syncope, edema, fatigue |
| Mean gradient; often EOA and/or DVI; often AR grade | BAV, radiation, concomitant procedure | CAD, hypertension, STS-PROM, EuroSCORE II |
| Approach and a model name *if* it matches vocabulary | eGFR / calcium / phosphate unless the user added labs | Creatinine, NT-proBNP |
| Current yes/no member flags (client will not coerce unknown→false) | Historical mechanism flags (synthetic training leaves all `null`) | Medication list |
| Repeat confirmation often `unknown`; physician feedback often `unknown` | Valve model index if the name is unseen | Access route, center, manufacturer string, outcome rows |

**Prototype training fill (`notes_expanded.xlsx` after study-inclusion 12-month extract + later echo):** 1,408 eligible patients. Observed static: age, sex, approach, size, **BSA**, model/architecture when named, diabetes, CKD ≥3, reference hemodynamics except LVEF. Always `null`: BMI, PPM, LVEF, BAV, labs, radiation, concomitant, and all visit-level mechanism flags. Labels on that set: **126 Stage-3 hemodynamic templates** mapped onto the BVF clock (not CEC BVF), 468 other-cause death templates, 814 censored (including Stage-2 templates). The generator has **no** non-structural-failure template. Infective endocarditis and paravalvular leak appear only as negative implant eligibility screens; Stage 2/3 templates explicitly exclude endocarditis and persistent thrombosis. The NSVD cause is therefore structurally zero, not a measured incidence and not evidence that the 126 Stage-3 templates are misfiled NSVD. A live client request can be *more* complete than this training fill if the clinician enters BMI, LVEF, current yes/no flags, and labs.

**Safety consequence:** completeness is counted over all 26 static cells plus \(12 \times V\) visit cells. Any missingness warns; **>40% missing** abstains; \(V < 2\) warns `sparse_longitudinal_history`. Stage 3 or indeterminate current HVD withholds displayed BVF probabilities. An abstention is not low risk.

---

## 4. Availability Assumptions

- A valid 30–90-day reference TTE can be identified and linked to the implanted valve.
- Serial echo values, event dates, death, and valve removal are linkable with consistent patient IDs.
- Valve manufacturer/model/size and SAVR/TAVR approach are consistently coded.
- Clinical notes can be converted into validated structured fields.
- **High risk:** the de-identified dates are often year-only, and the real prototype has sparse echo coverage.
- **High risk:** synthetic records dominate the pooled cohort and do not provide independent evidence of generalization.

---

## 5. Preprocessing and Data Quality

### Data Cleaning

Deduplicate by patient, event type, date, and source; normalize units and categorical spellings; reject impossible values; and preserve source provenance. Structured fields are extracted from notes using deterministic patterns and then checked against the original text. At **inference**, the client reduces labs to the latest eGFR, calcium, and phosphate on or before the landmark; creatinine, NT-proBNP, and all medications stay on the study record and are not tensor features. The **training** parser inspected `labs_expanded.xlsx` and refused the join because result dates are calendar years.

### Missing Data Strategy

The synthetic TTEs contain gradient, Vmax, EOA/EOAi, DVI, and AR but no LVEF; the real prototype is substantially sparser. Missing values remain missing and receive explicit observation masks. No LOCF, MICE, or SMOTE is used. Tier 4 warns on any missingness and abstains by default above 40% missing model slots; fewer than two visits triggers a sparse-history warning.

### Temporal Alignment

The reference TTE is day zero. At each landmark the engine uses only records whose occurrence and availability times are on or before that landmark. The outcome-establishing echo and later data are excluded. Synthetic note text provides fractional years from implant; year-only real dates are insufficient for precise dynamic modeling and those records are retained only when ordering is unambiguous.

### Label / Ground Truth Construction

In the full study, Tier 1 identifies VARC-3 candidates and a blinded committee assigns event date, stage, etiology, and certainty. Tier 1 output alone is never an SVD or BVF label. On the current synthetic training extract (1,408 patients with a 30–90-day reference TTE, later echo, and the protocol study-inclusion 12-month filter), first events on the BVF clock are **126 Stage-3 hemodynamic templates** (not CEC BVF), 468 other-cause death templates, and 814 censored. Stage 2 templates are **censored** on that clock. The generator has no non-structural-failure template: IE/PVL appear only as negative eligibility screens, and hemodynamic templates exclude endocarditis and persistent thrombosis. Real note mentions require manual adjudication and are not treated as ground truth.

---

## 6. Synthetic or Proxy Data (if applicable)

The expanded files use `SYN-*` identifiers and explicitly label their notes as synthetic research records. They reproduce implant characteristics, serial echo trajectories, labs, medications, SVD events, death, and censoring so the model can learn and demonstrate coherent output shapes.

Expected proof-of-concept results are decreasing training loss, monotone competing-risk curves, broad separation of generated deterioration patterns, and complete Tier 1→5 execution. Precision will be limited—especially at one year (25 SVD-HVD events), for LVEF, non-SVD removal, and post-HVD progression—and any strong metric may reflect the generator rather than clinical signal. A real study replaces these records with adjudicated multi-center data and repeats training, calibration, temporal validation, and held-out-center testing.

---

## 7. Data Governance and Privacy

The real-world prototype files use substituted patient identifiers and redacted note tokens; the synthetic files contain no real patients. Before public submission, all free text must still undergo residual-PHI scanning and the team must confirm the challenge-provided license/DUA permits redistribution. No attempt is made to re-identify patients.

A full deployment requires IRB/ethics approval, site-specific DUAs, GDPR-compliant pseudonymization, patient-consistent date shifting, encrypted storage, role-based access, and audited processing inside the approved institutional environment. Only derived model artifacts—not raw patient records—leave that environment.
