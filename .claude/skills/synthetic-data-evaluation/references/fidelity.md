# Fidelity

## Our fidelity tiers vs V-Star

The V-Star framework defines fidelity levels for synthetic data evaluation. Our tiers overlap in
intent but differ in focus: V-Star emphasises statistical resemblance to a real comparator; ours
are designed for NHS healthcare datasets where real comparator data may not be available, and where
the distinction between "realistic generation" and "validated against real data" is the key
boundary.

### Team fidelity tiers

| Tier | Focus | What it means |
| --- | --- | --- |
| **Low** | Data structure and valid values | Correct columns, data types, valid codes, plausible marginals. Data looks like it should structurally. Independent sampling — no conditional relationships. |
| **Medium** | Inter-variable relationships look realistic | Everything in Low, plus: realistic join cardinalities (twins, multiple spells, censored pregnancies, NICE-schedule contacts), realistic missingness calibrated against published DQ reports (field-level at minimum; provider-level opt-in), univariate distributions calibrated to published NHS statistics, conditional sampling (age→parity, BMI→GDM, previous CS→delivery method), rare events at published prevalence with clinically coherent cascades, additional tables (e.g. MSD405, MSD109, MSD107 for MSDS), configurable fairness mode. |
| **High** | Mostly indistinguishable from real data | Same generation approach as Medium. The difference is validation: High fidelity is earned by evaluating against real comparator data (KS tests, JS divergence, discriminator AUC, TSTR, privacy audit) and confirming realistic distributions including rare values. A grade, not a generation mode. |

Low → Medium is a generation improvement. Medium → High is primarily a validation improvement.
Without real data to compare against, the best claim is Medium.

## Evaluation levels (L0–L3)

Four evaluation levels, increasing in difficulty and decreasing in tool support. Run in order; a
dataset failing an earlier level does not need a later one yet. Record each level separately in
report section 7 — a single combined score hides which level failed, and the levels have different
remedies.

## Level 0 — schema conformance

Prerequisite before any statistical check. Validates that the generated output matches the
specification structurally.

Checks:
- **Column presence**: every field the spec defines exists as a column, regardless of mandation
  level (M, R, D all produce columns)
- **Column count**: no extra or missing columns per table
- **Data types**: each column's values conform to the declared type
- **Mandatory non-null**: M fields have no missing values
- **Required population**: R fields are populated where the condition applies
- **Derived presence**: D fields exist as columns (value may be NULL where derivation notes say so)
- **Code list validation**: every coded field contains only values from its declared code list
  (codes are strings — "01" ≠ 1)
- **Cross-table foreign keys**: IDs referenced across tables exist in the parent table

When a machine-readable schema exists in `schemas/`, load it and automate these checks. Manual
inspection of column names against a 200-field spec is error-prone.

A dataset failing L0 should not proceed to L1 — fix the schema failures first.

## Level 1 — univariate

Individual column distributions compared against a reference. At Medium tier, the reference is
published statistics (NHS Maternity Statistics, ONS, DQ dashboards). At High tier, the reference
is real microdata.

### Categorical fields

| Metric | What it measures | Range | Good value |
| --- | --- | --- | --- |
| Hellinger distance | Distance between two probability distributions — magnitude of difference, not just reject/don't reject | 0–1 | < 0.1 good, > 0.3 investigate |

At Medium tier, compare synthetic frequencies against a reference distribution constructed from
published stats. At High tier, compare directly against real data frequencies.

Replaces chi-squared p-values: Hellinger gives magnitude (how different), not just a binary
reject/don't reject that depends on sample size.

### Continuous fields

| Metric | What it measures | Range | Good value |
| --- | --- | --- | --- |
| KS distance | Max gap between cumulative distributions — catches shape, spread, location differences | 0–1 | < 0.05 very good, < 0.15 acceptable |
| EMD / Wasserstein | Minimum "work" to transform one distribution into the other — how far values need to move | 0–∞ (units of the variable) | Lower = better. Compare across generation runs. |

KS and EMD are complementary: KS catches *whether* distributions differ, EMD captures *how much*.
At Medium tier, compare against a theoretical CDF from published summary stats (e.g. birth weight
~ Normal(mean, SD) from ONS). At High tier, compare against the real empirical CDF.

### Why these over chi-squared

Chi-squared p-values are a function of sample size: generate enough records and every distribution
"significantly" differs from the target. Hellinger distance is sample-size-invariant and bounded
[0, 1], making it comparable across datasets and generators. The same argument applies to EMD for
continuous columns. KS distance can be computed against a theoretical CDF from published summary
stats — no real microdata required.

## Missingness

Missingness is an L1 concern — checked after schema conformance (L0) and alongside univariate
distributions.

At Medium tier, missingness checks compare against published aggregate statistics (DQ dashboards,
summary reports). This is best-effort realism — the rates are sourced but not validated against
real microdata. At High tier, missingness is validated against actual provider-level completeness
data, confirming the generation matches real patterns. Same principle as the overall tier model.

### Field-level missingness (minimum for Medium tier)

| Check | What it tests | Reference source | Good value |
| --- | --- | --- | --- |
| Overall missing rate per field | National missingness rate matches published DQ reports | Data quality dashboards, published DQ reports | Within published range |
| Structural vs realistic missingness | Spec-mandated NULLs (TOS "always NULL") are distinct from realistic missingness | TOS derivation notes | Structural NULLs: 100% NULL. Realistic missingness: rate matches DQ reports. |
| M-field completeness | Mandatory fields have no missing values | Specification | 0% missing |

### Provider-level missingness (when provider-level generation was used)

| Check | What it tests | Reference source | Good value |
| --- | --- | --- | --- |
| Provider completeness variance | Missingness varies across providers, not uniform | Published provider-level DQ | Variance > 0; not all providers identical |
| Completeness distribution shape | Distribution of provider completeness rates is right-skewed (most good, tail of poor) | Published DQ dashboards | Right-skewed, not uniform or bimodal |
| Cross-field missingness correlation | Fields that tend to be missing together at poor providers are correlated | Domain knowledge, DQ reports | Positive correlation between related fields' missingness within providers |
| Geographic completeness pattern | Missingness has spatial/regional structure | Published regional DQ breakdowns | Regional variation present, matches known patterns |
| Fairness interaction | Missingness doesn't disproportionately affect protected groups in ways that don't match real patterns | DQ breakdowns by demographic | Consistent with published demographic patterns. See `references/fairness.md` for the full fairness framework — this check covers only the missingness dimension of fairness |

Provider-level checks apply only when provider-level missingness was generated (Medium tier
opt-in). For field-level-only datasets, check only overall rates.

### Reference sources for missingness (known)

- MSDS: NHS England MSDS Data Quality dashboards, provider-level completeness reports
- Other TOS datasets: equivalent NHSE DQ dashboards where they exist
- Where no published source exists, state this in the report — missingness rates are then based
  on the data specification (which may itself be estimated)

## Level 2 — multivariate

Correlations and joint distributions. Most tools are weak here, and it is where cross-modal
coherence becomes measurable.

Check correlation structure, conditional distributions (distribution of a lab value given a
diagnosis), and for multi-modal datasets, agreement across modalities for the same patient.

Cross-modal coherence has no dedicated metric in the audit. Apply multivariate fidelity across
files: derive comparable features per modality and test agreement. Examples:

| Pair | Test |
| --- | --- |
| ECG ↔ observations table | Heart rate derived from the waveform vs the recorded value |
| Clinical note ↔ labs table | Values stated in prose vs the structured record |
| Note ↔ pathway | Conditions and medications mentioned vs those on the record at that date |
| Wearable ↔ functional status | Derived activity and sleep biomarkers vs recorded status |
| Genotype ↔ phenotype | Variants assigned vs conditions in the patient state |
| Any modality ↔ timeline | Artefact timestamps vs encounter dates |

Independent per-modality generation appears here as correlations near zero where clinical knowledge
requires them. The remedy is the patient state in the generation skill, not a re-run of the metric.

### Categorical-categorical association

| Metric | What it measures | Range | Good value |
| --- | --- | --- | --- |
| Cramér's V | Association strength between two categorical variables | 0 (none) – 1 (perfect) | > 0 for known associations. Compare synthetic V vs expected from clinical knowledge. |

Use for validating conditional sampling chains where both variables are categorical (e.g.
presentation → delivery method, service type → disposition category). The generation skill's
ordered conditional sampling should produce non-zero Cramér's V between linked fields.

### Continuous-continuous correlation

Pearson correlation — already standard. Compare direction and magnitude against known clinical
relationships from the conditional sampling chain.

### Record-level diversity

| Metric | What it measures | Range | Good value |
| --- | --- | --- | --- |
| Gower distance (within-dataset) | Nearest-neighbour distances between synthetic records, handling mixed types natively | 0–1 per pair | Distribution not too tight (mode collapse) and not uniformly spread (some natural clustering). Compare across generation runs. |

Gower handles mixed-type NHS data (categorical codes + continuous measurements + dates) without
requiring one-hot encoding. Compute distribution of nearest-neighbour Gower distances to detect
mode collapse.

At High tier, Gower is also used for DCR (Distance to Closest Record) — comparing synthetic-to-real
distances against holdout-to-real distances.

## Level 3 — clinical fidelity

Domain logic a clinician would catch immediately. Statistical fidelity is not sufficient for
healthcare. Examples: no pregnant males; lab values consistent with the stated diagnosis;
plausible medication–condition pairings.

Extend per modality in play: genotype supporting phenotype, notes asserting only recorded facts,
signal features matching the patient's condition and medication.

This rarely has an off-the-shelf metric; it is a rules-based layer written in-house. Do not search
for a library.

## Tools

| Tool | Use for | Verdict | Constraints |
| --- | --- | --- | --- |
| SynthGauge | Metrics and visualisations comparing feature distributions between real and synthetic data. `Evaluator` class gives a consistent interface; multiple instances compare generators on the same metrics | Use | Covers levels 1–2. No clinical logic |
| synthcity | Fidelity metrics alongside utility and privacy in one suite, with healthcare plugins | Maybe | PyTorch — flag before use. Prefer when already used for generation |

Most of the distance metrics (Hellinger, KS, EMD, Cramér's V, Pearson, Gower) are available in
scipy, scikit-learn, and the gower package — no specialist synthetic data library required.
Hellinger distance and Cramér's V are short functions (< 10 lines each); compute directly rather
than adding a dependency.

Comparability is the reason to prefer SynthGauge: a single generator scoring 0.8 means little; two
generators scored on identical metrics is informative.

No other fidelity tool is sanctioned. Adding one requires user approval and a source URL.

## Script

`scripts/clinical_rules.py` — not built. Declarative clinical-plausibility checker: rules defined
as data (condition → expected lab range, condition → plausible medications, impossible field
combinations), applied row-wise, returning pass/fail with offending records.

Deterministic, re-run on every dataset, and unreliable when done by inspection — a model asked to
eyeball 5,000 rows will miss violations and invent others. Build it sized to the first real
dataset's rules.

## Metric thresholds and interpretation

No universal thresholds have been agreed (SKILL.md Rule 4). These bands are a reasonable starting
point from NHS dataset evaluations. Report the values alongside these bands; do not reduce to
pass/fail.

### Distance metrics (Medium and High tier)

| Metric | Type | Tier | Good value | Interpretation |
| --- | --- | --- | --- | --- |
| Hellinger | Categorical | Medium+ | < 0.1 | 0 = identical, 1 = no overlap |
| KS distance | Continuous | Medium+ | < 0.15 | 0 = identical CDFs |
| EMD | Continuous | Medium+ | Lower = better | Units of the variable; compare across runs |
| Cramér's V | Cat-cat pairs | Medium+ | > 0 for known associations | 0 = independent, 1 = determined |
| Pearson r | Cont-cont pairs | Medium+ | r > 0.1, p < 0.05 for known relationships | Standard interpretation |
| Gower NN | Record-level | Medium+ | Not too tight | Distribution, not single value |
| Discriminator AUC | Real vs synthetic | High | 0.55–0.75 | < 0.55 = privacy alarm, > 0.85 = poor fidelity |

### RAG bands

RAG (Red/Amber/Green) ratings for the report summary table. These are interpretation guidance,
not hard pass/fail gates. The report explains context alongside the rating.

| Metric | Green | Amber | Red |
| --- | --- | --- | --- |
| Hellinger distance | < 0.1 | 0.1–0.3 | > 0.3 |
| KS distance | < 0.05 | 0.05–0.15 | > 0.15 |
| EMD / Wasserstein | Within range seen in calibration runs | 1.5–3× calibration range | > 3× calibration range |
| Cramér's V (vs expected) | Difference < 0.05 from expected | Difference 0.05–0.15 | Difference > 0.15 or wrong direction |
| Pearson r (vs expected) | Direction correct, magnitude within 0.1 of expected | Direction correct, magnitude off by 0.1–0.3 | Wrong direction or magnitude off by > 0.3 |
| Gower NN distribution | Shape matches cohort expectation | Mild clustering or over-dispersion | Severe mode collapse (mass near 0) |
| Missingness rate per field | Within 5pp of published rate | 5–15pp from published rate | > 15pp from published rate or structural NULL violated |
| Provider completeness variance | Variance present, right-skewed | Variance present but uniform shape | No variance (all providers identical) |
| Discriminator AUC (High only) | 0.55–0.75 | 0.75–0.85 | < 0.55 (privacy alarm) or > 0.85 (poor fidelity) |

EMD has no absolute threshold (scale-dependent). Green/Amber/Red are relative to calibration runs
on the same field. If no calibration data exists, report the raw value without a RAG rating.
"pp" = percentage points (e.g. published rate 15%, synthetic rate 22% = 7pp difference = Amber).

### Legacy p-value thresholds (from MSDS proof-of-concept)

Retained for continuity. These applied chi-squared and binomial tests, which are sample-size-
dependent and are superseded by the distance metrics above for new evaluations:

| Check type | Threshold | Interpretation |
| --- | --- | --- |
| Most distribution checks (chi-squared, binomial) | p > 0.01 → PASS | Cannot reject that synthetic matches target |
| Delivery method / high-DOF categoricals | p > 0.001 → PASS | More degrees of freedom needs a more lenient threshold |
| Correlations | r > 0.1 and p < 0.05 → PASS | Standard direction — low p = significant correlation present |

**Why these are being superseded.** Chi-squared p-values are sample-size-dependent: generate
enough records and trivially small differences become "significant." Hellinger distance measures
magnitude and is bounded [0, 1], making it comparable across datasets of different sizes. P-values
also read backwards for distribution checks (high p = PASS), which users misinterpret.

## NHS TOS datasets

For datasets with a TOS, L0 schema checks must verify all mandation levels (M, R, D). See
`synthetic-data-generation/references/nhs-datasets.md` for the D-field categories and which
should contain values vs NULL.

## No real comparator

Levels 1 and 2 require a reference distribution. Without one:

- Level 3 becomes the primary evidence.
- Check internal consistency instead: observed prevalences, age structure and comorbidity patterns
  against the cohort definition in report section 3, and modalities against each other using the
  table above.
- Compare against published distributions where the user supplies them; record the source.
- Check missingness rates against published DQ reports even without real microdata — DQ dashboards
  are aggregate statistics, not patient-level data, and are usable at any fidelity tier.
- State in report section 7 which levels did not run and why.

## Report

Section 7. Record the tool used, the result per level, and levels that could not run. Pair with the
privacy result from section 9 — high fidelity is also high leakage (`privacy.md`). When level 2
fails on cross-modal agreement, name the specific disagreement when handing back to
`synthetic-data-generation`.
