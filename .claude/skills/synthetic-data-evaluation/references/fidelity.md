# Fidelity

Three levels, increasing in difficulty and decreasing in tool support. Run in order; a dataset
failing level 1 does not need level 3 yet. Record each level separately in report section 7 — a
single combined score hides which level failed, and the levels have different remedies.

## Level 1 — univariate

Individual column distributions: means, variances, category frequencies, missingness rates,
ranges. Table stakes. Necessary, not sufficient.

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

## No real comparator

Levels 1 and 2 require a reference distribution. Without one:

- Level 3 becomes the primary evidence.
- Check internal consistency instead: observed prevalences, age structure and comorbidity patterns
  against the cohort definition in report section 3, and modalities against each other using the
  table above.
- Compare against published distributions where the user supplies them; record the source.
- State in report section 7 which levels did not run and why.

## Report

Section 7. Record the tool used, the result per level, and levels that could not run. Pair with the
privacy result from section 9 — high fidelity is also high leakage (`privacy.md`). When level 2
fails on cross-modal agreement, name the specific disagreement when handing back to
`synthetic-data-generation`.
