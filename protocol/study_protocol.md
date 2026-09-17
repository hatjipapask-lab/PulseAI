# Study protocol

Markdown copy of `Protocol (2).docx` (Word file kept). Wording is copied from the Word document, including source typos. The secondary-endpoint table is restored as Markdown.

Dyania Health Hackathon September 2026
Team Name: PulseAI, Model: ValveGuard
Team Members: Athanasiou-Paraskevopoulou Maria, Chatzipapas Konstantinos, Myaris Stylianos

Study Protocol

Study Title & Objectives

Title
How long and how well? Dynamic Function-Forecasting and Risk-Trajectory Modelling to Guide the Individualized Surveillance after Bioprosthetic Aortic Valve Replacement: A Machine Learning, Time-to-Event Approach Optimizing Early-Warning Framework

Primary Objectives
To develop and validate a dynamic prediction model that, at each follow-up encounter after bioprosthetic aortic valve replacement, estimates the individual continuous incidence trajectory of structural valve deterioration (SVD) (moderate to high), as ell as the expected course of the valve’s performance. The risk is evaluated and updated dynamically after each follow-up using serial echocardiographic and clinical results of the patient.

Secondary Objectives:
To quantify the prospective accuracy of the projected functional course against each patient's next actual echocardiogram, and to characterize how that accuracy decays with forecast distance and with the number and spacing of prior studies.
To derive and validate an adaptive surveillance recommendation algorithm that determines the optimal time window for the next clinical follow-up and echocardiogram on an individualized basis for each patient, balancing early detection of clinical complications with the minimization of unnecessary healthcare resource utilization. (e.g., escalating from 12 months to 3–6 months for rapidly steepening risk trajectories)
To integrate a self-evaluation feedback loop, wherein the system queries the attending physician to verify whether its previous prognostic predictions and estimated timeframes were clinically validated.
Compare hemodynamic failure trajectories between surgical (SAVR) and transcatheter (TAVR) bioprostheses by contrasting their Δmean gradient acceleration and transvascular regurgitation patterns.
To determine, the interval during which reintervention could be undertaken electively rather than urgently (redo SAVR or Valve-in-Valve TAVR) prior to emergency hemodynamic decompensation or irreversible left ventricular dysfunction. This objective concerns the state of the prosthesis alone and makes no assessment of the patient's fitness for intervention.

Exploratory Objective:
To estimate the closing elective window, which combines the valve-side projection above with a patient-side projection of operability: the crossing of the rising projected risk of structural failure and a falling projected probability of remaining a low-risk candidate for elective redo surgery or valve-in-valve intervention, the latter estimated from age, renal function, ventricular function and comorbidity. No validated model exists for the forward trajectory of operability, and projecting an operative risk score forward is not a validated use of that score; the crossing is therefore reported as an explicitly non-validated decision-support illustration and never as a threshold for action.

Target Population

Inclusion Criteria
Adult patients (>-18) undergoing primary bioprosthetic aortic valve replacement - surgical (SAVR) (full/mini-sternotomy, thoracotomy) or transcatheter (TAVR) (transfemoral, subclavian, other validated access route) into native aortic anatomy.
Bioprosthetic tissue valves (bovine pericardial, porcine tissue, or stentless bioprostheses/homografts).
A valid baseline reference echocardiogram, defined as the transthoracic study performed 30 to 90 days after implantation.
At least one further follow-up transthoracic echocardiogram after the baseline reference study. No minimum duration of observation is required: patients are followed from the baseline reference study until an event, a competing event, or censoring, so that early failures and early deaths are retained.
Documented prosthesis specification — manufacturer, commercial model, nominal size in millimetres — and baseline anthropometrics permitting calculation of body surface area.

Exclusion Criteria
Exclusion criteria invoke only information available at or before the baseline reference echocardiogram. This restriction is deliberate and is the governing eligibility principle of the study: a criterion that depends on information first knowable later would exclude patients on the basis of their own future, remove the event-free person-time that preceded that future, and produce a development cohort that does not represent the population in which the model is intended to run.
Non-bioprosthetic recipients (mechanical prosthesis in the aortic position).
Index procedure performed as a valve-in-valve intervention, or for pre-existing bioprosthetic failure. This preserves a native anatomical baseline and avoids left truncation bias of the durability clock.
Active infective endocarditis at the time of the index procedure, by modified Duke criteria or intraoperative microbiological confirmation.
Non-structural valve dysfunction present at or before the baseline reference echocardiogram. Non-structural dysfunction arising after the baseline study does not exclude a patient: endocarditis, paravalvular leak requiring closure, thrombosis requiring reintervention and malposition requiring intervention are handled as competing events at the date of diagnosis or intervention, while leaflet thrombosis resolving on anticoagulation and paravalvular leak not requiring intervention are recorded as time-varying covariates with the patient remaining at risk.
Concomitant replacement of one or more additional valves (mitral and/or tricuspid) altering systemic transvalvular haemodynamics. Concomitant coronary artery bypass grafting, septal myectomy, aortic root or ascending aortic procedures are permitted and recorded as covariates.
No post-discharge imaging follow-up (patients with only intraoperative/procedural records and zero outpatient post-discharge imaging follow-up).

Cohort Size Estimate
The target is 3,500 patients, minimum 3,000, each with a valid 30–90-day reference TTE and at least one later echo. No minimum duration of observation is required, so early failures and early deaths are retained. At a mean follow-up of 4.5 years this yields roughly 13,500–15,750 patient-years, about 450 transitions to moderate and 200 to severe deterioration or valve failure, and some 12,000 echocardiographic studies. Death from other causes and non-structural failure are competing events, so transition counts, not visit counts, set the sample size.
Size is justified on the criteria for developing clinical prediction models (Riley et al.) rather than on the events-per-variable heuristic, and because the primary endpoint is multi-state the requirement is computed per transition at its own rate, with the anticipated Cox–Snell R² set conservatively at 15% of the achievable maximum. The first transition then supports up to 25 predictor parameters, the terminal transition up to 15 — the latter requiring 159 events, which is what governs the study. 2,000 patients would be inadequate, and a mean follow-up of 3.5 years leaves even 3,500 at the requirement rather than above it: completing follow-up on enrolled patients yields more events than extending recruitment. The cap applies to the effective parameter count, including the longitudinal sub-model's variance components, and the two transition sub-models are not given equal complexity. The longitudinal sub-model is not the constraint, being powered by measurements rather than events. This event total does not license the full tensor — features enter a pre-specified, regularised set, and a deep architecture is retained only if validation justifies it over simpler survival models.

Endpoints

Primary Endpoint
Co-Primary Endpoint 1 - end of functional life (time-to-event)
Time-to-incident for the first occurrence of SVD-related bioprosthetic valve failure: the earliest of (a) severe (VARC-3 stage 3) hemodynamic structural valve deterioration; (b) aortic valve reintervention for structural deterioration; (c) death attributable to structural deterioration. Evaluated within a 10-year observational window, with other-cause death and non-structural valve failure as competing events.
Co-primary endpoint 2 — the functional course (longitudinal)
The observed serial functional state of the prosthesis from the baseline reference echocardiogram to the end of observation, and the timing of the ordered transitions the valve makes along it: normal function → moderate (VARC-3 stage 2) deterioration → severe (stage 3) deterioration or bioprosthetic valve failure, comprising: mean transprosthetic gradient (mmHg), Doppler velocity index, effective orifice area (cm²), and intraprosthetic aortic regurgitation grade (0–4) each with its measurement-validity status.

Structural Valve deterioration is classified by following mechanisms:
Echo-Doppler Diagnostic Thresholds (VARC-3 Stage 2/ 3 - moderate/severe)
Moderate (Stage 2): Δmean gradient >10mmHg resulting in >20mmHG with concomitant EOA decrease >0.3cm2/>25% or DVI fall >0.1/>20%
Severe (Stage 3): Δmean gradient >20mmHg resulting in >30mmHg with concomitant EOA decrease >0.6cm2/>50% or DVI fall >0.2/>40%OR severe intraprosthetic aortic regurgitation, new or worsening (>2+/3+) from baseline.
Morphological Diagnostic Criteria (Imaging-based or histopathologically)
Documented irreversible intrinsic structural leaflet deterioration (calcification, fibrosis, leaflet tear, perforation, or flail) on echocardiography or multi-detector cardiac CT leading to hemodynamic compromise.

SVD-Related Clinical Reintervention
Performance of surgical re-replacement (redo SAVR) or transcatheter reintervention (Valve-in-Valve TAVR) secondary to bioprosthetic dysfunction, or surgical explant with pathologically/histologically confirmed intrinsic leaflet deterioration and explicit exclusion of active infective endocarditis.

SVD-Related Death
Death is attributed to structural valve deterioration where any of the following applies: death occurring after documented severe deterioration on the verified functional record, without an independent sufficient competing cause; death during or within 30 days of a reintervention performed for a structural indication; autopsy demonstrating intrinsic leaflet deterioration — calcification, tear, perforation or flail — with explicit absence of active vegetation; or sudden unexplained death in a patient with documented moderate or severe deterioration on an echocardiogram within the preceding 12 months.
Exclusions from the Primary Endpoint: Hemodynamic failure purely secondary to patient-prosthesis mismatch (PPM) present from baseline, active prosthetic valve endocarditis, paravalvular leak (PVL), or isolated non-structural valve thrombosis without permanent tissue alteration.
Severe patient–prosthesis mismatch is measured on the baseline reference echocardiogram only, as indexed effective orifice area of 0.65 cm²/m² or less (0.55 cm²/m² or less where body mass index is 30 kg/m² or greater), and is treated as a baseline covariate rather than a longitudinal endpoint. Patient–prosthesis mismatch is a property of the implant fixed at the time of surgery; an indexed effective orifice area that falls during follow-up represents structural deterioration, not emergent mismatch.
Secondary Endpoints

| Endpoint | Measurement | Timeframe |
|---|---|---|
| All-cause aortic valve reintervention | Redo SAVR, ViV-TAVR or surgical explant for any indication, including paravalvular leak, endocarditis, thrombosis and malposition; from operative records, departmental logs and cross-centre reconciliation | From baseline reference echocardiogram to end of observation (max 10 yr); full cumulative incidence curve |
| Clinically expressive bioprosthetic valve failure | Moderate or severe deterioration on the primary course plus new NYHA ≥II symptoms attributable to the valve, or LVEF fall ≥10 percentage points to <50%, or valve-related heart failure hospitalisation | From baseline reference echocardiogram to end of observation; full cumulative incidence curve |
| Progression of paravalvular regurgitation | Increase of ≥1 grade on the four-level ordinal scale, recorded in its own field and never combined with intraprosthetic regurgitation; non-structural by definition | Continuously across all serial studies; full cumulative incidence curve |
| All-cause mortality (competing risk) | Verified date of death from the national civil registry and vital statistics, linked by the site honest broker; cause recorded where available | Up to 10 yr post-op; absorbing state of the primary endpoint |
| Non-structural bioprosthetic valve failure (competing risk) | Failure related to endocarditis, valve thrombosis, paravalvular leak or malposition, by modified Duke criteria, imaging or reintervention indication | Up to 10 yr post-op competing event |
| Clinical expression of baseline severe patient–prosthesis mismatch | Among patients with severe PPM on the baseline reference study (EOAi ≤0.65 cm²/m², or ≤0.55 where BMI ≥30): new or persistent NYHA ≥II symptoms attributable to the valve, failure of left ventricular mass regression, or valve-related heart failure hospitalization, in the absence of any significant change in gradient, Doppler velocity index or effective orifice area from baseline. Descriptive endpoint; classified as non-structural valve dysfunction and never as structural deterioration | Continuously across all serial studies and clinical encounters; reported as cumulative incidence within the baseline-PPM stratum |

Proposed Data Sources

Hospital information systems and departmental records at each participating centre
Structured administrative data; unstructured clinical narrative

Local extraction by each site's own personnel under the site data controller's authority, into a common pseudonymised schema; no direct external access to source systems

Identifiers for pseudonymisation, sex, age at implantation, anthropometrics, comorbidity, renal function, calcium and phosphate metabolism, prior chest irradiation

Cardiac surgical and catheterisation laboratory records

Operative and procedural reports

Departmental logbooks and operative report archives

Procedure date, approach, access route, prosthesis manufacturer, model and nominal size, post-dilatation, concomitant procedures

Echocardiography archives — picture archiving and communication systems, cardiovascular information systems, and departmental report repositories

Structured report objects where populated; otherwise narrative reports, word-processed documents or scanned images

Structured report parsing where available; bilingual natural language extraction with optical character recognition fallback otherwise, with the extraction method recorded per study

Mean and peak gradient, peak velocity, outflow tract and transvalvular velocity–time integrals, outflow tract diameter, effective orifice area, Doppler velocity index, intraprosthetic and paravalvular regurgitation grade, ventricular dimensions and function, leaflet morphology description

MIMIC-IV-Echo (PhysioNet)
Structured echocardiographic measurements and DICOM studies

Free but credentialed: PhysioNet account, CITI human-subjects and privacy training certificate, signed data use agreement.

Serial echo measurements for prototyping the trajectory sub-model and the measurement-quality log

ClinicalTrials.gov

Trial protocols, statistical analysis plans, posted results

Open, no registration

Endpoint definitions used by pivotal valve trials, observed event rates, serial echo tables — free calibration material for your own assumptions

Mortality data
Date and, where available, cause of death
National civil registry and vital statistics, accessed through the sites established institutional procedure with linkage performed by a designated honest broker within each site

Date of death, cause where recorded

Reintervention outside the treating centre

Procedure records

Cross-site reconciliation between participating centres; national insurance and procedural records where institutionally permitted

Date, type and indication of reintervention

Ground Truth Definition
Ground truth is a single verified functional record per patient: a time-ordered series of adjudicated echocardiographic measurements — mean gradient, Doppler velocity index, effective orifice area, intraprosthetic aortic regurgitation (paravalvular recorded separately) — each with a measurement-quality status and its extraction provenance, from the baseline reference study to the end of observation. The failure endpoint is read out of the same record as the first confirmed crossing of the VARC-3 stage 3 boundary, resulting in Structural Valve Deterioration.
Ground truth structural valve deterioration (SVD, Y = 1) is established via blinded Clinical Events Committee (CEC) adjudication confirming the first occurrence of irreversible, intrinsic bioprosthetic failure. Events are classified according to standardized Valve Academic Research Consortium 3 (VARC-3) and EAPCI/ESC/EACTS consensus criteria using a hierarchical multi-tiered adjudication pipeline.
To train and evaluate our model without label leakage or missclassification, the ground truth Y = 1 must meet at least one of the following three objectives:

Tier 1 (Explant Histopathology - Gold Standard): Surgical inspection or autopsy showing intrinsic leaflet tearing, macroscopic calcification, perforation, or mechanical prolapse, with explicit histological absence of active bacterial/fungal vegetations (ruling out infective endocarditis).
Tier 2 (Reintervention for SVD): Documented redo SAVR or ViV-TAVR performed specifically for structural hemodynamic failure (excluding reoperations performed purely for suture dehiscence, isolated paravalvular leak, or endocarditis).
Tier 3 (Serial Echocardiographic Progression): In non-reoperated patients, stage is assigned from change relative to the patient's baseline reference echocardiogram. Moderate (stage 2): Δmean gradient ≥10 mmHg resulting in ≥20 mmHg, with a concomitant fall in effective orifice area ≥0.3 cm² or ≥25%, or in Doppler velocity index ≥0.1 or ≥20%; or new or ≥2-grade increase in intraprosthetic aortic regurgitation resulting in ≥moderate. Severe (stage 3): Δmean gradient ≥20 mmHg resulting in ≥30 mmHg, with a concomitant fall in effective orifice area ≥0.6 cm² or ≥50%, or in Doppler velocity index ≥0.2 or ≥40%; or new or ≥3-grade increase in intraprosthetic aortic regurgitation resulting in severe. Absolute gradient, effective orifice area, indexed effective orifice area and Doppler velocity index values at a single study are review triggers and covariates, never event criteria.

Clinical Adjudication Committee: Independent blinded panel reviewing all borderline cases to exclude non-structural confounders, including temporary gradient spikes from confirmed hypo-attenuated leaflet thickening (HALT) reversed by oral anticoagulation, and flow-dependent hyperdynamic gradients (e.g., severe sepsis, severe anemia with normal DVI).

Statistical Analysis Plan

Sample Size
The study target is 3,500 adults with a primary bioprosthetic SAVR or TAVR, with 3,000 as the minimum, each with a valid 30–90-day reference TTE and at least one later echo. No minimum duration of observation is required: patients enter at the reference study and are followed until an event, a competing event or censoring, so that early failures and early deaths are retained rather than excluded. At a mean follow-up of 4.5 years this yields approximately 13,500–15,750 patient-years, about 450 transitions to moderate deterioration and 200 to severe deterioration or bioprosthetic valve failure, and roughly 12,000 echocardiographic studies. Death from other causes and non-structural failure are competing events, so transition counts — not visit counts — set the sample size.

Size is justified on the criteria for developing clinical prediction models (Riley et al.): small optimism in apparent fit, no more than 0.05 between apparent and adjusted explained variation, and precise estimation of baseline risk. Because the primary endpoint is a multi-state course, the requirement is computed separately for each transition at its own rate, with the anticipated Cox–Snell R² set conservatively at 15% of the maximum achievable since no prior model of this type exists. On that basis the first transition supports up to 25 predictor parameters and the terminal transition up to 15, the terminal transition requiring 159 events at that complexity. The terminal transition is the less frequent and therefore governs the study: 3,000 patients meet its requirement with limited margin, 2,000 would not meet it at all, and a mean follow-up of 3.5 years leaves even 3,500 patients sitting at the requirement rather than above it — so completing imaging follow-up on patients already enrolled contributes more events than extending recruitment. The cap applies to the effective parameter count, including the variance components contributed by the longitudinal sub-model, not to the list of covariate names; the two transition sub-models are not permitted equal complexity. The longitudinal sub-model is not the constraint, being powered by the number of serial measurements rather than by events. Planning assumes a low early hazard of SVD-related failure, rising after years 7–10, which is why the extract must be multi-centre and multi-year rather than an early-postoperative snapshot. This event total does not license fitting the full static-plus-per-visit tensor: features enter a pre-specified, regularised set, and a deep architecture is retained only if the adjudicated event count and external validation justify it over simpler survival models.

Train / Validation / Test Split:
Split Strategy: Data is partitioned at the patient level into a 70% Training set, 10% Tuning/Validation set, and 20% Held-out Test set. All longitudinal visits, operative records, and serial echocardiograms for a given patient remain strictly in the assigned partition to prevent data leakage across time or subjects.
Temporal / Geographical Validation: Additionally, temporal split validation (e.g., training on implants prior to a calendar cut-off and testing on subsequent implants) is performed to verify real-world transportability.
Handling Low Base Rates (Imbalance): Addressed using survival loss formulations (e.g., Cox partial likelihood or dynamic cross-entropy with IPCW: Inverse Probability of Censoring Weighting) and time-to-event sampling, rather than artificial synthetic oversampling (such as SMOTE), which distorts longitudinal clinical physics.
Calibration: Brier Score across predefined horizons (1, 3, 5 years), calibration slope, and expected-to-observed calibration plots.
Clinical Decision Utility: Decision Curve Analysis (DCA) to measure Net Benefit across actionable clinical threshold probabilities (e.g., 5% to 20% risk of 1-year deterioration prompting early echo surveillance), ensuring false positives (unnecessary 3-month echoes) and false negatives (missed silent acute failures) are balanced.

Subgroup Analyses
Implant Approach: TAVR vs. SAVR (evaluating performance differences due to stent crimping/expansion mechanics vs. surgical sewing ring geometry).
Valve Model & Architecture: Externally mounted pericardial tissue (e.g., Trifecta) vs. internally mounted/supra-annular designs (Perimount, Magna Ease) vs. balloon-expandable TAVR (Sapien 3) vs. self-expanding TAVR (Evolut) to evaluate design-specific failure curves
AR Grade Current = Aortic Regurgitation (0-4, none to severe) (0= none, 1= trivial, 2= mild, 3 = moderate 4 = severe)
Native Leaflet Anatomy: Bicuspid Aortic Valve (BAV) vs. Tricuspid Aortic Valve (TAV).

Comparator / Baseline
Time-since-implant alone (null historical durability curve).
Static baseline surgical risk scores (EuroSCORE II and STS-PROM).
Standard institutional practice (fixed 12-month annual surveillance scheduling).
Landmark supermodel — cause-specific Cox or Fine–Gray on stacked landmark records with elapsed-time interactions. This is the benchmark the primary model must beat; a static model is too weak a comparator to demonstrate that dynamic updating adds value.
Static baseline model — competing-risk model on baseline covariates and the anchor study only, quantifying the value of serial surveillance data.

Ethical Considerations and Data Privacy

IRB / Ethics Review
The study protocol will be submitted for approval to the Research Ethics Committees (EHDE) and the Scientific Councils of all participating Greek university clinics and tertiary NHS hospitals (in accordance with Greek Law 4521/2018). Given that this is a non-interventional, retrospective observational study utilizing secondary, pseudonymized electronic health and imaging records without modifying clinical routine, patient care, or diagnostic pathways, a waiver of individual informed consent is requested pursuant to Article 9(2)(j) of the EU General Data Protection Regulation (GDPR 2016/679) and Article 30 of Greek Law 4624/2019 (processing of special categories of personal data for scientific research purposes).

Data Privacy (GDPR & Greek Law 4624/2019 Compliance):
Controllership. Each hospital is controller of its own source data. The multi-site pseudonymised research dataset is processed under a written joint controller arrangement specifying responsibilities for information provision, data subject rights, security and breach notification, with a single contact point for data subjects, executed before any data leaves a site and signed off by each site's Data Protection Officer.
Pseudonymization & De-identification: Full compliance with GDPR mandates and guidelines issued by the Hellenic Data Protection Authority (HDPA). All protected health identifiers—including patient names, National Social Security Numbers (AMKA), national ID/passport numbers, and internal medical record numbers (MRNs)—are stripped and replaced with cryptographically salted study identifiers (Patient_GR_XXX).
Handling of Longitudinal Dates: To maintain longitudinal temporal consistency for time-to-event survival modeling without revealing absolute calendar dates, exact encounter and imaging dates are shifted using an arbitrary, fixed, patient-specific offset preserved across all relational database tables.
Secure Computing Infrastructure: All data extraction, model training, and feature transformations are hosted within isolated, on-premise institutional server clusters or ISO 27001 / ISO 27701 certified secure EU-based research cloud environments. Access is restricted strictly to authorized investigators via role-based access control, two-factor authentication (2FA), and comprehensive immutable audit logging.

Algorithmic Fairness (EU AI Act Alignment & Bias Auditing):
EU AI Act Alignment: Designed in compliance with the European Union AI Act requirements for high-risk clinical artificial intelligence systems, prioritizing human agency, technical robustness, data traceability, and explainability.
Demographic & Inter-Center Parity: The algorithm undergoes rigorous auditing across sex and age groups for equalized odds and parity in time-dependent calibration and Brier scores. Particular emphasis is placed on mitigating risk underestimation in female patients, who disproportionately receive small-diameter bioprostheses (21mm) with naturally elevated baseline gradients. Model calibration is independently evaluated across data originating from central university centers versus regional hospital registries to avoid institutional distribution shift.

Clinical Transparency & Human Oversight (Human-in-the-Loop):
Decision Support Interface: The system is engineered strictly as a Clinical Decision Support System (CDSS) for surveillance interval optimization, not an autonomous diagnostic or prescriptive agent. Model inference displays dynamic trajectory curves of 1-, 3-, and 5-year SVD risk accompanied by localized explainability metrics (SHAP feature attributions, such as annualized gradient slope and presence of patient-prosthesis mismatch).
Clinical Safeguards: Algorithmic recommendations are strictly bounded to imaging scheduling adjustments (e.g., "Elevated 3-year SVD risk (18%): Recommend accelerating echocardiographic surveillance to 3–6 months with focused symptom review"). Under no circumstances does the system recommend or schedule invasive procedures. Any definitive reintervention decision (redo SAVR or ViV-TAVR) remains under the sole authority of the institutional multidisciplinary Heart Team, predicated upon multi-modality imaging confirmation (TTE/TEE/cardiac CT) and clinical symptom manifestation.

References
Généreux P, Piazza N, Alu MC, et al. Valve Academic Research Consortium 3: updated endpoint definitions for aortic valve clinical research. Eur Heart J 2021;42:1825–1857.
Pibarot P, Herrmann HC, Wu C, et al. Standardized definitions for bioprosthetic valve dysfunction following aortic or mitral valve replacement: JACC state-of-the-art review. J Am Coll Cardiol 2022;80:545–561.
Capodanno D, Petronio AS, Prendergast B, et al. Standardized definitions of structural deterioration and valve failure in assessing long-term durability of transcatheter and surgical aortic bioprosthetic valves: EAPCI consensus statement endorsed by ESC and EACTS. Eur Heart J 2017;38:3382–3390.
Vahanian A, Beyersdorf F, Praz F, et al. 2021 ESC/EACTS guidelines for the management of valvular heart disease. Eur Heart J 2022;43:561–632.
Lancellotti P, Pibarot P, Chambers J, et al. Recommendations for the imaging assessment of prosthetic heart valves. Eur Heart J Cardiovasc Imaging 2016;17:589–590.
Collins GS, Moons KGM, Dhiman P, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models. BMJ 2024;385:e078378.
Riley RD, Snell KIE, Ensor J, et al. Minimum sample size for developing a multivariable prediction model: binary and time-to-event outcomes. Stat Med 2019;38:1276–1296.
van Houwelingen HC. Dynamic prediction by landmarking in event history analysis. Scand J Stat 2007;34:70–85.
Rizopoulos D. Dynamic predictions and prospective accuracy in joint models for longitudinal and time-to-event data. Biometrics 2011;67:819–829.
Fine JP, Gray RJ. A proportional hazards model for the subdistribution of a competing risk. J Am Stat Assoc 1999;94:496–509.
Austin PC, Lee DS, Fine JP. Introduction to the analysis of survival data in the presence of competing risks. Circulation 2016;133:601–609.
Gerds TA, Schumacher M. Consistent estimation of the expected Brier score in general survival models with right-censored event times. Biom J 2006;48:1029–1040.
Blanche P, Kattan MW, Gerds TA. The c-index is not proper for the evaluation of t-year predicted risks. Biostatistics 2019;20:347–357.
Van Calster B, McLernon DJ, van Smeden M, et al. Calibration: the Achilles heel of predictive analytics. BMC Med 2019;17:230.
Vickers AJ, Elkin EB. Decision curve analysis: a novel method for evaluating prediction models. Med Decis Making 2006;26:565–574.
