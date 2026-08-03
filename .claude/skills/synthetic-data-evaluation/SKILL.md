---
name: synthetic-data-evaluation
description: Assesses synthetic healthcare data along fidelity, utility and privacy. Use when asked whether synthetic data is good, realistic, clinically plausible, useful or safe to share; for univariate and multivariate distribution comparison, clinical-plausibility rule checks, TSTR (train-on-synthetic / test-on-real), synthetic-vs-real discriminator tests, membership- and attribute-inference or re-identification risk, disclosure control, free-text leakage, a privacy audit before a dataset leaves the environment, or an evaluation report for a generated dataset. Also use immediately after generating any dataset with the synthetic-data-generation skill, including the "no real seed data" case where TSTR is impossible. Covers SynthGauge, synthcity metrics, TAPAS/SAS and PrivFingerprint.
---

# Synthetic healthcare data evaluation

Every generated dataset gets an evaluation, recorded in its `REPORT.md`. This skill decides which
checks can run and routes to the method detail.

The tools tables in `references/` are the recommended inventory. You must ask for user approval if
using an unlisted tool. Where no tool exists for a check, the reference file says so.

## Rules

**1. Read the report before interpreting any result.** Section 4 gives the seeding case, which
fixes what can run at all. Section 5 gives label provenance: if one LLM produced both the content
and its label, a strong utility score may only show that a model can read what another model wrote.
A result read without those two is not evidence.

**2. Fidelity and privacy are one reading, not two.** Data reproducing real records exactly is both
maximally faithful and maximally leaky. The discriminator check has a floor and a ceiling: easily
separable means poor fidelity, not separable at all is a privacy alarm. Never report a fidelity
result without the privacy result beside it.

**3. Do not ingest real patient data to run a check.** The output of a check over real data is
itself a disclosure question. Where a check structurally requires real data — membership inference,
exact-match — stop and confirm with the user how and by whom it should be run. It may be a
human-run step.

**4. No pass/fail thresholds.** None has been agreed, and inventing one would be false precision.
Report what was measured, what was not, and why, so the reader can judge fitness for their own use.

**5. An unrun check is "not established", never "safe".** This applies to the free-text leakage
assessment and the safe-to-share verdict especially. Say what would need to run to establish it.

## Axes

**Fidelity** — does it look like real data. Three levels: univariate (column distributions),
multivariate (correlations and joint structure, where cross-modal coherence shows up as a number),
clinical (domain logic a clinician would catch). → `references/fidelity.md`

**Utility** — is it useful for the task. TSTR: train on synthetic, test on held-out real, compare
against a real-trained baseline. Lighter checks: ML comparison, synthetic-vs-real discriminator.
→ `references/utility.md`

**Privacy** — does it leak. Exact-match checks are necessary and not sufficient; membership and
attribute inference are the real test. → `references/privacy.md`

Writing or completing the dataset report → `references/report.md`

## Local scripts

`scripts/call_llm.py` — `call_llm(prompt, model=..., temp=0.7, ...) -> str | None`, plus
`call_llm_async` for batches. It returns `None` when every attempt fails; check before using the
result. Two rules specific to evaluation:

- **Try to pass a different `model` than the one that generated the text.** A model asked to find
  identifying detail in its own output under-reports it — the label-validity trap in privacy form.
  Where the environment exposes only one model, use it, and record in report section 9 that
  generation and extraction shared a model and that the result is therefore a lower bound on
  what is identifying. This is what makes LLM entity extraction a viable substitute for GLiNER and
  spaCy (`references/privacy.md`).
- **LLM extraction is not reproducible.** No seed is exposed and `temp` defaults to 0.7. Acceptable
  for exploration and flagging, too weak for a score that must be defended. Record which of the two
  it is.

`scripts/clinical_rules.py` — **not built.** Declarative clinical-plausibility rule checker.
Interface in `references/fidelity.md`.

`scripts/tstr.py` — **not built.** TSTR harness plus discriminator AUC, sklearn only. Interface in
`references/utility.md`.

Build either when a real dataset needs it, not speculatively. Both are deterministic checks that
are unreliable done by inspection — a model asked to eyeball 5,000 rows will miss violations and
invent others.

## Checklist

Copy this into your response and tick items off as you go. Doing a step implicitly does not tick
its box.

```
Evaluation progress:
- [ ] 1. REPORT.md sections 1-6 read; seeding case and label provenance established before any result is interpreted
- [ ] 2. Scope fixed — which checks can run, which need real data, which need user permission
- [ ] 3. Tools acquired and verified — installed in .venv and smoke-tested, or recorded as not runnable
- [ ] 4. Fidelity: levels 1-3 run, or explicitly recorded as not run and why
- [ ] 5. Utility: TSTR against a real holdout, or the substitution named as a substitution
- [ ] 6. Privacy: checks run; nothing requiring real data run without user confirmation
- [ ] 7. Fidelity and privacy read against each other before either is reported
- [ ] 8. REPORT.md sections 7-10 written; verdict is safe to share / not safe to share / not established
```

## Step 1 — read the report

Sections 1-6 of the dataset's `REPORT.md`, before running anything. Two fix the scope of everything
that follows:

- **Section 4, seeding case** — real seed data, schema only, or from intelligence. Step 2 turns this
  into the list of checks that can run.
- **Section 5, label provenance** — whether labels were derived from the patient state before the
  content existing. If they were not, utility results are discounted rather than presented
  (Rule 1).

If sections 1-6 are missing or thin, the dataset was not generated through the
**synthetic-data-generation** skill's Step 7. Say so and reconstruct what you can before evaluating;
record in section 10 what could not be reconstructed.

## Step 2 — establish what can run

Determine whether real data exists for comparison and whether its use is permitted. This fixes the
scope of the whole evaluation.

| Situation | Fidelity | Utility | Privacy |
| --- | --- | --- | --- |
| Real seed data used, available for comparison | Full | TSTR against real holdout | Mandatory; direct leakage risk |
| Real data exists, not used for generation | Full, as reference distribution | TSTR if the holdout is representative | Required; lower risk |
| No real data | Clinical + internal consistency only | TSTR impossible — see **No real seed data** | Lower risk; re-check if any real record informed a prompt |

Anything in the right-hand column that needs real data is subject to Rule 3: confirm with the user
before it runs, and confirm who runs it.

## Step 3 — acquire and verify tools

Nothing in `references/` has been verified by running it; the tables record repository claims.
Install from PyPI into `.venv` and smoke-test on a small slice before reporting any number from it.

TAPAS is the one worth the attempt first. It is recorded as inspiration with no setup notes, but
the repository shows a pip-installable package with a CLI, and if it installs it is the only real
adversarial audit available (`references/privacy.md`). Most of the strongest privacy tools are
inspiration-only, so the runnable set is thinner than the tables imply.

Where a tool will not install or is inspiration-only, record it as not runnable and carry that into
report section 9. A check that could not run is not a check that passed (Rule 5).

## Step 4 — fidelity

Three levels, run in order; a dataset failing level 1 does not need level 3 yet. Record each level
separately — a combined score hides which level failed, and the levels have different remedies.
→ `references/fidelity.md`

Level 3, clinical plausibility, is a rules-based layer written in-house. There is no off-the-shelf
metric; do not search for a library.

## Step 5 — utility

TSTR where a real holdout exists: train on synthetic, test on real, and report the real-trained
baseline and the gap beside it. A synthetic score alone is uninterpretable.
→ `references/utility.md`

Check label provenance from Step 1 before reading any result here. Where TSTR cannot run, see
**No real seed data** below — do not drop the axis or let fidelity stand in for it.

## Step 6 — privacy

Weakest to strongest: exact-match, attribute inference, membership inference, adversarial auditing.
Exact-match is necessary and nowhere near sufficient. → `references/privacy.md`

Rule 3 governs this step. Membership inference and exact-match structurally require real data
alongside the synthetic; stop and confirm rather than running them unprompted. Free text is the
leakage path structured metrics miss.

## Step 7 — read fidelity against privacy

Before writing either result. A high fidelity score and a clean privacy result are consistent; a
high fidelity score and an undistinguishable discriminator are the same finding read twice, and the
reading is leakage (Rule 2).

## Step 8 — write the report and the verdict

Complete sections 7-10 of the dataset's `REPORT.md`: fidelity, utility, privacy and disclosure,
limitations. Template and rules: `references/report.md`.

The verdict is one of **safe to share**, **not safe to share**, **not established**. Where the
checks that would justify sharing could not run — inspiration-only tooling, or a check needing real
data that must not be touched — the answer is "not established", and the decision routes to the
user with a statement of what would settle it.

If results are poor, hand back to the **synthetic-data-generation** skill with the specific failure
— a broken correlation, an implausible medication pairing, a cross-modal mismatch — not a request
to regenerate. Then re-run the checks that failed.

## No real seed data

TSTR cannot run. Do not drop the utility axis and report fidelity alone. Substitute, and label the
substitution in the report:

- Clinical plausibility becomes the primary quality signal (`references/fidelity.md`).
- Internal consistency replaces external fidelity: check the data against the patient state and
  cohort definition it was generated from, and check modalities against each other.
- Train and test on synthetic (TSTS) to establish that the encoded signal is learnable. A
  substantially weaker claim than TSTR; report it as such.
- Compare against published distributions where the user supplies them; record the source.
- State that downstream utility is unproven, in those words.
- Recommend clinician review of a sample. With no real comparator it is the strongest validation
  available.

Privacy risk is lower, not zero. Re-check whether any real record informed generation, including
via a prompt; whether LLM-generated free text surfaces memorised training content; and whether
invented records collide with real people by chance in a small, distinctive population.
