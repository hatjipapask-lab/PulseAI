# Model approach

PulseAI is a deterministic-then-probabilistic, five-layer research pipeline. VARC-3 rules first identify current hemodynamic valve deterioration (HVD) candidates; a Dynamic-DeepHit-style competing-risk model estimates dynamic 1-, 3-, 5-, and 10-year SVD-related BVF risk; auxiliary heads forecast echocardiographic trajectories and post-HVD progression; separate calibration/safety and clinician-approved policy layers convert reliable risk into surveillance support. The system never autonomously diagnoses structural valve deterioration (SVD) or recommends an invasive intervention.

This repository implements and tests the complete software pipeline and includes two proof-of-concept data sources: three de-identified prototype workbooks and three expanded synthetic workbooks. These files support a hackathon training demonstration, but they are not a protocol-complete clinical cohort and no clinically trained checkpoint or measured performance is claimed. The validation procedures below remain the prespecified full-study plan.

---

## 1. Problem Formulation

We frame valve-durability prediction as **dynamic landmark time-to-event analysis with competing risks**, rather than independent binary classification at fixed dates.

The valid 30–90-day post-implant reference TTE defines study time zero. Every later valid assessment can define a prediction landmark \(s\), provided all predictors were available by \(s\). From each eligible landmark, Tier 2 models residual time to the first mutually exclusive event:

1. SVD-related bioprosthetic valve failure (Stage 3 HVD, structural reintervention, or SVD-attributed death);
2. other-cause death; or
3. non-structural index-valve failure / removal.

Stage 2 HVD is a co-primary serial functional course, not a competing first event on this clock. Death and non-structural failure are modeled as competing events because they prevent later observation of BVF. Right-censored patients, including those whose first observed hemodynamic change is Stage 2, contribute known event-free follow-up through that time rather than being treated as BVF events.

Serial echoes are irregularly spaced and partly missing, so the predictor consumes the complete pre-landmark history with measurement masks and time-gap information. The echo or record that establishes an outcome is never used to predict that outcome. Stage 2 candidates remain on the BVF risk set. Once Stage 3 occurs, the patient leaves the Tier 2 first-event risk set; subsequent Stage 2 → Stage 3 → SVD-related BVF progression is modeled separately by Tier 3.

Tier 1 VARC-3 rules identify **candidate HVD**, not SVD etiology. Training labels require independent clinical adjudication of event date, stage, etiology, and competing cause.

---

## 2. Chosen Model(s)

| Model | Role | Justification |
|---|---|---|
| Tier 1 deterministic VARC-3 rules | Current-state screening and endpoint-candidate generation | Reproduces the protocol's Stage 2/3 gradient and intraprosthetic-regurgitation pathways against the reference TTE. It exposes calculations, severe PPM, alternative causes, missing-data warnings, and the need for adjudication. |
| Tier 2 Dynamic-DeepHit-style competing-risk sequence model | **Primary high-capacity first-event candidate** | A missingness-aware irregular-time GRU, temporal attention, and static encoder produce one normalized joint cause-by-time distribution. This handles serial measurements, right censoring, death, and valve removal without incoherent independent classifiers. |
| Tier 3 longitudinal and progression model | Echo/LV forecasting and post-HVD prognosis | A separate irregular-time encoder feeds a horizon-conditioned trajectory decoder and a post-Stage-2/3 competing-risk head. It keeps first HVD and later progression as different clinical questions. |
| Tier 4 isotonic calibration and safety monitor | Reliability layer | Held-out, endpoint- and horizon-specific monotone calibration corrects systematic over- or under-confidence. Missingness, simple featurewise distribution shift, calibration availability, and uncertainty gates can force abstention. |
| Tier 5 versioned surveillance policy | Clinical decision-support layer | A stateless, clinician-owned policy maps current findings and calibrated one-year risk to `review_now`, `3_months`, `6_months`, or `standard_interval`. Thresholds can change without retraining prediction models. |
| Time-since-implant curve and baseline Cox model | Minimum comparators, planned for study evaluation | Quantify benefit beyond elapsed time and standard baseline covariates. |
| Landmark penalized Cox; cause-specific Cox/Fine–Gray; classical joint model; gradient-boosted survival; random survival forest | Prespecified comparators, not implemented in this prototype | Test whether the deep sequence model adds sufficient discrimination, calibration, and clinical utility to justify its complexity. |

The primary neural candidate is appropriate because it jointly learns from tabular baseline data and irregular serial measurements, while its discrete competing-risk likelihood uses censored follow-up correctly. The output remains clinically inspectable as cause-specific cumulative-incidence curves. Tier 1 pathways, measurement deltas, data-quality warnings, and Tier 3 forecasted slopes provide transparent clinical context; attention weights are internal pooling weights and are **not** presented as causal explanations.

The deep model is not assumed to be the final winner. It should be selected or stacked only if patient-level out-of-fold and untouched temporal/site validation show improvement over simpler survival comparators. With the protocol's expected 150–200 primary events, regularized classical models may generalize better despite the larger number of visits.

The implementation uses vectorized PyTorch tensors, packed variable-length sequences, mini-batch training, and checkpointed schemas, which is sufficient for the proposed 2,500–3,000-patient registry scale.

---

## 3. Feature Engineering

### What the executable engine receives

`PulseAIEngine.predict` does **not** ingest the full study chart. It receives one `EngineInput` JSON object (`pulseai.engine-input/1.2`):

1. `baseline_echo` — the 30–90-day reference TTE (`EchoAssessment`).
2. `current_echo` — the landmark follow-up TTE (same schema).
3. `history` — label-free `PredictionHistory` ending at that landmark.
4. `clinical_context` — PPM BMI; exclusive NSVD-member flags (thrombosis, endocarditis, PVL, malposition) plus high-flow; repeat-echo status and physician forecast feedback for confirmation/policy only; implant-to-echo day counts. Omitted alternative-cause keys stay unknown (`null`), never `false`.
5. `current_progression_state` — adjudicated `event_free` / `stage_2` / `stage_3` (default `event_free`).

Each echo object may carry: `assessed_at` (**required**), mean gradient, EOA, DVI, intraprosthetic AR grade \(0\)–\(4\), Vmax, EOAi, LVEF. All hemodynamic fields may be `null`. If EOAi is missing, it is derived as EOA/BSA when both exist. History times are **days from the reference TTE**; visit 0 must be time zero; the last visit time must equal `landmark_time_days` and must equal current minus reference calendar days. Availability time cannot precede occurrence. An outcome-supporting visit is rejected. Patient ID is audit-only, never a learned feature.

**Static slots (26, checkpoint order):** `age_years`, `female` (1/0 only), `bmi_kg_m2`, `bsa_m2`, `tavr`, `valve_size_mm`, reference mean gradient / EOA / DVI / Vmax / EOAi / LVEF / AR grade, `severe_ppm`, `valve_model_index`, `stented`, `sutureless`, `externally_mounted_leaflets`, `diabetes`, `ckd_stage_3_or_greater`, `bicuspid_anatomy`, `egfr`, `serum_calcium`, `serum_phosphate`, `chest_radiation`, `concomitant_cabg_or_aortic_procedure`.

STS-PROM and EuroSCORE II are study-record comparators for the exploratory operability curve. They are **not** packed into this tensor. Repeat-echo status and physician forecast feedback are **not** GRU features.

Reference hemodynamics are sent **twice** on purpose: as `baseline_echo` for VARC-3 (Tier 1) and again as the first history visit plus the seven `baseline_*` static slots for the GRUs. The client keeps those copies aligned.

**Longitudinal slots per visit (12):** mean gradient, EOA, DVI, Vmax, EOAi, LVEF, AR grade, suspected thrombosis, active endocarditis, isolated paravalvular AR, prosthetic malposition, transient high-flow.

Missing cells stay `null` and become observation masks. Hard structural rejects: missing dates/objects, landmark mismatch, non-increasing visit times, or a leaky outcome echo. Soft gates: Tier 4 warns below two visits and abstains when more than **40%** of all static+visit slots are missing.

The thin-client **study record** is wider than this tensor. Symptoms/NYHA, CAD, hypertension, creatinine, NT-proBNP, medications, access route, center ID, manufacturer string, free-text concomitant notes, STS-PROM, EuroSCORE II, and outcome/censoring rows are **not** packed into the deterioration tensor. Outcomes are retained for the study file and are excluded from inference by design.

### a) Optimal patient input

The chart that lets every layer do its intended job, with no masks and no quality flags from missingness:

- Adult with a confirmed primary bioprosthetic SAVR or TAVR; implant date; approach; nominal size; valve model in the frozen vocabulary (or architecture coded so stented / sutureless / external leaflets are known).
- BMI (measured, never BSA-substituted) so severe PPM is evaluable, and BSA so EOAi can be computed when not reported.
- Reference TTE **30–90 days** after implant with a complete hemodynamic set: mean gradient, Vmax, EOA, EOAi, DVI, AR grade, LVEF.
- At least one later TTE, preferably several irregular follow-ups, each with the same hemodynamic set; occurrence and availability dates; **none** of those visits is the outcome-establishing echo. A landmark is any post-reference visit with predictors available at that time. Protocol **study inclusion** still uses ≥12 months of follow-up; that is not a landmark gate, and shorter follow-up is allowed at inference (flagged as study-inclusion mismatch).
- **Current** alternative-cause flags resolved to yes or no (not unknown): thrombosis, endocarditis, isolated PVL, malposition, high-flow. Do not send an NSVD umbrella flag. Historical visits may leave members unknown (`null` ≠ “no”).
- Diabetes, CKD ≥3 (or stage), bicuspid anatomy, chest radiation, concomitant CABG/aortic procedure.
- Latest pre-landmark eGFR, calcium, and phosphate.
- Repeat-echo confirmation status when Tier 1 is Stage 2/3, and physician feedback on any prior forecast (`unknown` / `confirmed` / `rejected`): these are confirmation/evaluation fields, not GRU covariates.
- Adjudicated progression state: `event_free` unless a committee has recorded Stage 2 or 3 (reviewer + date required in the client). Missing current state defaults to `event_free` at inference; training labels remain `(time, cause)` including censored.
- For **training** only, not inference: earliest CEC-adjudicated first event or censoring (BVF / other-cause death / non-structural failure / censored) after the landmark. The prototype uses generator Stage-3 hemodynamic templates on the BVF clock, not CEC gold standard.

### b) Realistic patient input (incomplete, still legal)

The engine is built for sparse charts. A typical inference payload still has the **same JSON shape**, but many numeric slots are `null`:

- **Must still be present to run:** implant date and SAVR/TAVR (client), dated reference TTE in the 30–90-day window, at least one dated later TTE, landmark alignment, current alternative-cause flags as yes/no in the client, governance acknowledgements. The Python API treats omitted alternative-cause keys as unknown (`null`), not `false`.
- **Usually observed in a working TTE pair:** mean gradient plus at least one of EOA or DVI (otherwise the gradient pathway is indeterminate); AR grade if regurgitation is being assessed. Vmax and EOAi improve support and PPM but are not each strictly required; EOAi can be derived from EOA/BSA.
- **Often missing and masked:** LVEF; BMI (then PPM is not evaluable); BAV; radiation; concomitant procedure; eGFR/calcium/phosphate; valve model outside vocabulary; sex other than female/male.
- **Often missing in historical visits:** the four exclusive NSVD-member flags and high-flow (`null` ≠ “no”).
- **Prototype training reality (synthetic notes, 1,408 patients):** observed — age, female/male, SAVR/TAVR, size, BSA, valve-model/architecture when the name matches, diabetes, CKD ≥3, reference and serial gradient/Vmax/EOA/EOAi/DVI/AR. Always masked — BMI, PPM, LVEF, BAV, labs, radiation, concomitant procedure, and all visit-level mechanism flags. `labs_expanded.xlsx` is year-dated and is **not joined**. Stage 3 hemodynamic templates are mapped onto the BVF clock; they are **not CEC BVF**. Stage 2 templates are censored. Death notes are other-cause death. The generator has **no** non-structural-failure template. IE and PVL appear only as negative implant eligibility screens; Stage 2/3 templates exclude endocarditis and persistent thrombosis. That NSVD zero is structural rather than a measured incidence, and it does not reclassify the 126 Stage-3 templates as NSVD. A clinician-entered client request can fill BMI, LVEF, current flags, and the three lab slots even though training never saw them observed.
- **De-identified real workbooks:** year-only dates and incomplete echo fields; they are inventoried, not converted into supervised landmarks.
- **Consequence:** a realistic case can still get a Tier 1 candidate (or `indeterminate`), a masked GRU prediction, and a warning; if missingness exceeds 40% of tensor slots, or current HVD is Stage 3/indeterminate, Tier 4 **abstains** and numbers are not shown as low risk.

### Required Full-Study Data

The intended model requires the protocol target of **2,500–3,000 patients**, approximately **10,000–15,000 patient-years**, and at least **150–200 adjudicated primary SVD-related BVF events**. Each patient needs:

- the 26 static slots above, a valid 30–90-day reference TTE, and ≥1 post-reference echo. Protocol study inclusion also asks for ≥12 months of observation; that is a cohort rule, not a per-landmark gate.
- at each assessment, up to 12 longitudinal values plus occurrence time, availability time, and endpoint-support flag;
- an earliest adjudicated event type/date or verified censoring date, including death and non-structural failure;
- for Tier 3 training, later observed values for six trajectory targets: gradient, Vmax, EOA, DVI, LVEF, and AR grade.

The model can represent missing values. At least the reference TTE and one later echo are required to form a landmark; fewer than two visits triggers a safety warning.

### Proof-of-Concept Data

- **De-identified prototype source:** 215 notes from 117 patients, 43,550 laboratory rows from 17 patients, and 5,807 medication rows from the same 17 patients. Only 17 patients link across all three files, and echo variables in the notes are incomplete.
- **Expanded synthetic source:** 13,834 notes, 95,908 laboratory rows, and 4,258 medication rows for 1,500 linked synthetic patients. It contains 10,834 serial TTE records for 1,496 patients (median eight, range one–13), including a 30–90-day reference TTE. These TTE records contain gradient, Vmax, EOA/EOAi, DVI, and AR, but not LVEF.
- **Combined prototype pool:** up to 1,617 distinct patient IDs; 1,517 link across notes, labs, and medications. After the 30–90-day reference, later-echo, and protocol study-inclusion 12-month extract, **1,408** synthetic patients are engine-eligible.

For proof-of-concept training, the sources will be harmonized by patient and date. Notes provide implant, serial echo, and outcome templates; laboratory records occupy compact eGFR/calcium/phosphate slots when the client supplies them at inference. Year-only `labs_expanded.xlsx` dates are not joined. Medications remain study-record context. Stage 3 hemodynamic templates map onto the BVF clock as numeric candidates, not CEC events. Stage 2 templates are censored. The generator has no non-structural-failure class.

### Engineered Features

| Feature | Derivation | Clinical Rationale |
|---|---|---|
| Reference-relative HVD measurements | Current minus reference mean gradient and Vmax; reference minus current EOA and DVI; AR grade change | Directly exposes the changes used by VARC-3 Stage 2/3 criteria. |
| Annualized observed gradient/Vmax change | Measurement difference divided by years from reference TTE | Makes progression comparable across irregular follow-up intervals. |
| Severe PPM | EOAi ≤0.65 cm²/m², or ≤0.55 cm²/m² when BMI ≥30 kg/m² | Separates elevated baseline prosthetic gradients from incident deterioration and supports prespecified subgroup analysis. |
| Observation masks | One binary observed/missing indicator per static and longitudinal feature | Prevents a filled numeric value from being mistaken for an observed measurement. |
| Irregular timing representation | Log-scaled inter-visit gap and time since reference TTE | Allows the recurrent model to distinguish the same change over months versus years. |
| Intercurrent-state indicators | Timestamped thrombosis, endocarditis, PVL, malposition, and high-flow flags | Exclusive NSVD-member states and a flow gate, without an overlapping NSVD umbrella. |
| Forecasted gradient/Vmax change | \((\hat y(s+h)-y(s))/h\) from Tier 3 | Provides a clinically understandable summary of the predicted hemodynamic trajectory. |

Tier 1 exposes its rule calculations for review, but the current default Tier 2/3 neural schema learns temporal change from raw serial values, masks, and visit timing rather than directly ingesting the Tier 1 candidate stage. This avoids turning a rules-layer candidate into an SVD label.

### Handling Missing Data

Missing values remain `None` until batching. Model tensors replace missing numeric cells with zero **only while adding a separate observation mask**, so zero is never interpreted as an observed clinical measurement. Feature means and scales are fitted on observed values from the training partition only. No last-observation-carried-forward, MICE, SMOTE, or synthetic oversampling is used.

The GRU receives measurement masks and irregular visit timing, allowing it to learn different behavior for measured and unmeasured fields. Tier 4 reports any missingness, warns when fewer than two visits are available, and by default abstains when more than 40% of model feature slots are missing. Tier 1 returns `indeterminate` when required rule pathways cannot be resolved instead of silently classifying the valve as normal.

A missed visit is represented indirectly through the longer time gap; the current prototype does not include an explicit missed-appointment feature or model the observation process. Informative follow-up missingness is therefore a limitation to test during validation.

---

## 4. Validation Strategy

- **Train / validation / test split:** Prespecified 70% / 10% / 20% patient-level split. Every landmark, echo, procedure, and outcome for one patient stays in one partition. Training APIs reject patient identifiers shared between training and validation. The held-out test set is never passed to model fitting or early stopping.
- **Cross-validation approach:** Within the training partition, grouped cross-validation by patient will tune architecture, regularization, time bins, ranking-loss weight, and comparator hyperparameters. Out-of-fold predictions—not in-sample predictions—will support model comparison, optional stacking, and calibration-model development.
- **Temporal validation:** A later implant-era cohort will remain untouched during development to detect changes in valve generations, imaging practice, and follow-up.
- **External validation:** At least one center or registry site will be held out. Where sample size permits, valve-manufacturer/model families absent from training will form a transportability stress test rather than being mixed randomly across partitions.

For the hackathon proof of concept, eligible records from both available sources will be concatenated only after schema harmonization, then split 70% / 10% / 20% by patient and stratified where possible by source and first-event type. Synthetic rows derived from the prototype distribution are not independent external validation. Because only 17 de-identified patients link across all three modalities, performance will be reported as an internal technical demonstration rather than evidence of transportability.

Tier 4 calibration maps must be fitted on out-of-fold or held-out patient predictions at each endpoint/horizon. Patients censored before a horizon have an unknown (`null`) binary status for that horizon and are not treated as non-events. For the full study, calibration and time-dependent metrics should use censoring-aware estimators/IPCW when appropriate.

The prespecified evaluation suite is:

- time-dependent AUROC and competing-risk concordance at 1, 3, 5, and 10 years;
- integrated and horizon-specific Brier scores;
- calibration-in-the-large, calibration slope, and calibration plots;
- decision-curve net benefit across clinically reviewed thresholds;
- sensitivity, calibration, and Brier-score analyses by SAVR/TAVR, sex, age, valve model/architecture, valve size/PPM, bicuspid anatomy, and center.

The protocol's AUROC, C-index, and calibration-slope values are **target criteria**, not achieved results. Deep learning will be retained only if the event count and validation performance justify it. The repository's backend tests (`python -m unittest discover -s backend/tests`) verify the engine contract, leakage guards, NSVD/label audit, fail-closed artifact loading, demo showcases, and complete Tier 1→5 execution; they do not establish clinical validity.

---

## 5. Expected Model Outputs

A single `PulseAIEngine` inference returns:

1. **Current rules result:** VARC-3 candidate state (`no_hvd`, `stage_2`, `stage_3`, or `indeterminate`), triggering pathway, measurement changes, PPM, alternative causes, and data-quality warnings.
2. **First-event prognosis for eligible patients:** uncalibrated cause-specific probability mass and cumulative-incidence curves for SVD-related BVF, other-cause death, and non-structural failure; BVF risk and event-free probability at 1, 3, 5, and 10 years.
3. **Trajectory/progression result:** forecast mean gradient, Vmax, EOA, DVI, LVEF, and intraprosthetic AR; annualized predicted gradient/Vmax change; and, after adjudicated Stage 2/3, next-event risk for Stage 3, SVD-related BVF, death, and non-SVD removal.
4. **Reliability result:** calibrated milestone risk, empirical reliability bounds, calibration status, missingness and out-of-distribution summaries, warnings, and `ok` / `warning` / `abstain`.
5. **Clinical action:** `review_now`, `3_months`, `6_months`, or `standard_interval`; Heart Team review flag; risk and policy version used; and machine-readable reasons.

For an event-free patient, including a current Stage 2 candidate, Tier 4 calibrates `svd_bvf` risk. After adjudicated Stage 2, it calibrates combined Stage 3-or-BVF `progression` risk. After Stage 3, it calibrates `svd_bvf` risk. If the current echo already matches Stage 3 candidate criteria or is indeterminate, Tier 2 first-event prediction is withheld and the patient is routed to review.

**Output format:** structured JSON containing the five tier-specific blocks, `engine_status`, and an explicit statement that the engine provides surveillance decision support only. `intervention_recommendation` is always `null`.

The current explainability surface consists of deterministic Tier 1 pathways/calculations, named risks, predicted trajectories, safety warnings, and policy reason codes. SHAP feature attribution is a planned evaluation/interface extension after a final model is selected; it is not implemented or claimed as a current output. The Tier 4 uncertainty range is a prototype calibration-reliability indicator, not a formal patient-level confidence interval.

The reduced proof-of-concept input space does **not** change the five-tier output schema: Tier 2 returns three causes across 40 quarterly bins plus tail probability, and the pipeline exposes 1-, 3-, 5-, and 10-year BVF risks and Tier 3 trajectory fields. Expected training results are convergence on the synthetic trajectory patterns, coherent monotone cumulative-incidence curves, and a working end-to-end surveillance demonstration. Statistical reliability will be lower: Stage 3 templates are uncommon, no explicit non-structural-failure examples exist, and post-HVD progression labels remain inadequate. Any apparently strong discrimination is an internal synthetic-data result, not evidence of real-world performance.

---

## 6. Clinical Integration

The intended integration is a passive EHR/CVIS/registry decision-support panel triggered when a valid post-reference TTE becomes available. Structured DICOM-SR or validated report extraction populates the echo fields; registry/EHR feeds supply baseline implant variables, intercurrent states, mortality, and reintervention outcomes.

The workflow is:

1. Tier 1 compares the current echo with the protocol reference TTE.
2. If the patient remains event-free, including a current Stage 2 candidate, Tier 2 updates conditional 1-, 3-, 5-, and 10-year first-event risk. Stage 3 or indeterminate current HVD withholds that head.
3. Tier 3 updates echo/LV forecasts for all eligible patients and uses its progression head after adjudicated Stage 2/3.
4. Tier 4 calibrates the relevant risk and checks whether the result is reliable enough to use.
5. Tier 5 applies a versioned, clinician-approved surveillance policy.

The prototype policy uses one-year risk cutoffs of 20%, 10%, and 5% for `review_now`, `3_months`, and `6_months`, respectively; lower risk maps to `standard_interval`. These are demonstration thresholds, not validated clinical cutoffs, and the code refuses to apply them until an approving clinical group is recorded. A current HVD candidate, adjudicated Stage 2/3, indeterminate rule result, missing calibration, or model abstention overrides risk-based scheduling and routes to review.

The Heart Team flag asks for multidisciplinary assessment and any needed confirmatory imaging. It does not choose redo SAVR, valve-in-valve TAVR, or an intervention date. Final diagnosis and treatment remain with clinicians and the Clinical Adjudication Committee/Heart Team.

---

## 7. Limitations and Failure Modes

- **Prototype data are synthetic-dominated:** 1,500 synthetic patients are fully linked, whereas only 17 de-identified patients link across notes, labs, and medications. The files can demonstrate training and inference but cannot establish clinical performance.
- **Low event count:** approximately 150–200 expected primary events may be insufficient for the full deep architecture. Penalized classical comparators and reduced models are mandatory safeguards against overfitting.
- **Incomplete realistic tensors:** model/architecture, comorbidities, labs occupy named slots but are often masked; STS/EuroSCORE, CAD, hypertension, medications, and NT-proBNP never enter the deterioration tensor.
- **Sparse or informative follow-up:** long gaps and missed echoes may reflect health status or access to care. Timing and masks help but do not fully model the observation process.
- **Measurement variability:** inter-reader and modality differences in gradient, EOA, DVI, AR, and LVEF can change rules and forecasts. Repeat confirmation and adjudication remain necessary.
- **Observation-dependent Stage 3-first label:** a patient first observed at Stage 3 may have passed through unobserved Stage 2 between scheduled echoes.
- **Alternative etiologies:** thrombosis, endocarditis, PVL, malposition, PPM, and flow states are flagged as exclusive members or gates. Dependable attribution requires imaging and clinical adjudication.
- **Distribution shift:** the Tier 4 z-score rule is a simple prototype. New valve models, centers, or implausible combinations may still escape detection.
- **Calibration and uncertainty:** isotonic maps need sufficient held-out events. An unfitted map causes abstention. Reported bounds are heuristic reliability ranges, not formal individual confidence intervals.
- **Late events vs follow-up length:** the fitted grid is quarterly through 10 years; synthetic and real follow-up may still be too short for a well-identified 10-year CIF.
- **Prototype policy thresholds:** surveillance cutoffs require prospective clinical review and decision-curve analysis before use.
- **Explainability/fairness not yet implemented:** SHAP, formal fairness testing, and subgroup recalibration are prespecified evaluation work, not current engine functions.
- **No causal treatment effect:** predictions do not estimate benefit from redo SAVR, valve-in-valve TAVR, anticoagulation, or any other therapy.

Clinicians must see the candidate-versus-adjudicated distinction, calibration status, safety warnings, abstention reasons, and current policy version beside every prediction. An abstention must never be displayed as low risk.


