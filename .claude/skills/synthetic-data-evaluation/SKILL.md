---
name: synthetic-data-evaluation
description: Assess synthetic healthcare data along fidelity, utility and privacy. Use when asked whether synthetic data is good, realistic, clinically plausible, useful or safe to share; for univariate and multivariate distribution comparison, clinical-plausibility rule checks, TSTR (train-on-synthetic / test-on-real), synthetic-vs-real discriminator tests, membership- and attribute-inference or re-identification risk, disclosure control, free-text leakage, a privacy audit before a dataset leaves the environment, or an evaluation report for a generated dataset. Also use immediately after generating any dataset with the synthetic-data-generation skill, including the "no real seed data" case where TSTR is impossible. Covers SynthGauge, synthcity metrics, TAPAS/SAS and PrivFingerprint.
---

# Synthetic healthcare data evaluation

Every generated dataset gets an evaluation, recorded in its `REPORT.md`. This skill decides which
checks can run and routes to the method detail.

The tools tables in `references/` are the sanctioned inventory. Where no tool exists for a check,
the reference file says so. Recommending a tool that is not listed requires user approval and a
source URL — do not substitute from memory.

Assets recorded as inspiration have an entry in `references/privacy.md` giving source and date
read, the pattern, what to copy, what to substitute, what not to inherit, and caveats. Take the
approach rather than the toolchain: where an asset uses a specialist library for a step, an LLM
call often does the same job with nothing to install — subject to the caveats, which for privacy
work include non-determinism and self-assessment bias. If a task needs detail an entry does not
cover, ask the user or fetch the source URL; the target environment may have no outbound network,
so never make a fetch a dependency.

## Axes

**Fidelity** — does it look like real data. Three levels: univariate (column distributions),
multivariate (correlations and joint structure, where cross-modal coherence shows up as a
number), clinical (domain logic a clinician would catch). → `references/fidelity.md`

**Utility** — is it useful for the task. TSTR: train on synthetic, test on held-out real, compare
against a real-trained baseline. Lighter checks: ML comparison, synthetic-vs-real discriminator.
→ `references/utility.md`

**Privacy** — does it leak. Exact-match checks are necessary and not sufficient; membership and
attribute inference are the real test. → `references/privacy.md`

## Constraints on interpretation

**Fidelity and privacy are in tension.** Data that reproduces real records exactly is both
maximally faithful and maximally leaky. The discriminator check has a floor and a ceiling: easily
separable means poor fidelity, not separable at all is a privacy alarm. Never report a fidelity
result without the privacy result beside it.

**Check label provenance before reading any utility result.** If one LLM produced both the content
and the label, a strong score may only show that a model can read what another model wrote. Read
section 5 of the report first.

**Do not ingest real patient data to run a check.** Some privacy tools were assessed as inspiration
rather than as tools to run, because the output of a check over real data is itself a disclosure
question. Where a check structurally requires real data, stop and confirm with the user how and by
whom it should be run. See `references/privacy.md`.

## Step 1 — establish what can run

Determine whether real data exists for comparison and whether its use is permitted. This fixes the
scope of the whole evaluation.

| Situation | Fidelity | Utility | Privacy |
| --- | --- | --- | --- |
| Real seed data used, available for comparison | Full | TSTR against real holdout | Mandatory; direct leakage risk |
| Real data exists, not used for generation | Full, as reference distribution | TSTR if the holdout is representative | Required; lower risk |
| No real data | Clinical + internal consistency only | TSTR impossible — Step 3 | Lower risk; re-check if any real record informed a prompt |

## Step 2 — route to the method

| Task | Read |
| --- | --- |
| Distributions, correlations, joint structure, cross-modal coherence, clinical plausibility | `references/fidelity.md` |
| TSTR, ML-utility comparison, synthetic-vs-real discriminator | `references/utility.md` |
| Membership/attribute inference, re-identification, free-text leakage, safe-to-share decision | `references/privacy.md` |
| Writing or completing the dataset report | `references/report.md` |

## Step 3 — no real seed data

TSTR cannot run. Do not drop the utility axis and report fidelity alone. Substitute and label the
substitution in the report:

- Clinical plausibility becomes the primary quality signal (`references/fidelity.md`).
- Internal consistency replaces external fidelity: check the data against the patient state and
  cohort definition it was generated from, and check modalities against each other.
- Compare against published distributions where the user supplies them; record the source.
- State that downstream utility is unproven, in those words.
- Recommend clinician review of a sample. With no real comparator it is the strongest validation
  available.

## Step 4 — write the report

Complete sections 7–10 of the dataset's `REPORT.md`: fidelity, utility, privacy and disclosure,
limitations. Template and rules: `references/report.md`.

There are no numeric pass/fail thresholds. None has been agreed, and inventing them would be false
precision. The report instead states what was measured, what was not, and why, so
the reader can judge fitness for their own use.

If results are poor, hand back to the **synthetic-data-generation** skill with the specific
failure — a broken correlation, an implausible medication pairing, a cross-modal mismatch — not a
request to regenerate.

## Scripts

Two deterministic checks should become scripts under this skill. Neither is built. Build when a
real dataset needs one.

- `scripts/clinical_rules.py` — declarative clinical-plausibility rule checker.
- `scripts/tstr.py` — TSTR harness plus discriminator AUC, sklearn only.

Interfaces are specified in `references/fidelity.md` and `references/utility.md`.
