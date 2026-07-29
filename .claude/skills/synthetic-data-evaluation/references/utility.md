# Utility

Fidelity asks whether the data looks right. Utility asks whether it works for the task.

## TSTR

Train on synthetic, test on real. Train a model on synthetic data, evaluate on held-out real data,
compare against the same model trained on real data.

1. Hold out a real test set, untouched by generation. If the synthetic data was fitted to real
   data, the holdout must not have been in that fit.
2. Train model A on synthetic, model B on real training data. Same architecture,
   hyperparameters and preprocessing — any other difference invalidates the comparison.
3. Evaluate both on the real test set.
4. Report the synthetic score, the real-trained baseline and the gap. A synthetic score alone is
   uninterpretable: 0.78 AUC means one thing against a 0.81 baseline and another against 0.95.

Lighter variant: a single "does a model perform comparably" check, for iteration rather than the
reported result.

## Discriminator check

Train a classifier to distinguish synthetic from real records.

- Easily separable → poor fidelity: some value range, formatting artefact or absent correlation
  gives it away.
- Not separable at all → privacy alarm, not success. Data reproducing real records exactly is both
  maximally faithful and maximally leaky. Read alongside `privacy.md`.

## Tools

No sanctioned library performs TSTR. SynthGauge is distributional. synthcity's
utility metrics (ML fairness, privacy, augmentation) carry a PyTorch dependency that may not be
viable in the target environment.

The harness is therefore in-house, using scikit-learn. Do not substitute a TSTR library from
memory; if one is needed and none is available, say so.

## Script

`scripts/tstr.py` — not built. Given a synthetic dataset, real training set, real test set and
target column, report:

- train-on-synthetic → evaluate on real test,
- train-on-real → evaluate on real test (baseline),
- synthetic-vs-real discriminator AUC.

sklearn only, deterministic seed. A script rather than prose because the failure modes are
procedural: leaking the test set into training, preprocessing the two arms differently, omitting
the baseline. Build when a dataset with a real holdout requires it.

## When TSTR cannot run

The common case here: generated from intelligence, no real holdout. Do not drop the utility axis
or present fidelity as covering it.

- Clinical plausibility becomes the primary quality signal (`fidelity.md`).
- Train and test on synthetic (TSTS) to establish that the encoded signal is learnable. This is a
  substantially weaker claim than TSTR and must be reported as such.
- Compare against published expectations where the user supplies them; record the source.
- State that downstream utility is unproven, in those words, in report section 8.
- Recommend clinician review of a sample.

## Label provenance

A utility result is only as good as its labels. Read report section 5 first.

- If one LLM produced both the content and the label, a strong result may only show that a model
  can read what another model wrote. This inflates utility scores specifically.
- Confirm labels were derived from the patient state before content existed.
- If they were not, record it in section 8 and discount the result rather than presenting it.

See the generation skill's `references/from-intelligence.md`.

## Report

Section 8. Record the synthetic score, the real-trained baseline, the gap, the discriminator AUC
with its reading in both directions, whether TSTR or TSTS ran, and label provenance. If TSTR could
not run, state it.
