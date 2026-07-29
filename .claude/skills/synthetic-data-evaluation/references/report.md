# Dataset report

Every generated dataset gets a `REPORT.md` written alongside the data files. One document covers
provenance and evaluation. It is the deliverable that makes the dataset usable by someone who was
not present when it was generated.

## Rules

- Sections 1–6 are written during generation, before evaluation runs.
- Sections 7–9 are written by the evaluation skill.
- Never delete a section. If a check did not run, keep the heading and state why.
- Never write "safe" or "validated" for a check that did not run. Use "not established".
- Record the source of every number in the cohort definition, including "assumed, no source".

## Template

```markdown
# <dataset name> — synthetic dataset report

## 1. Summary
What this is, how many patients, which modalities, one paragraph.
Generated: <date>. Generator: synthetic-data-generation skill.

## 2. Intended use
The PoC this was built for. The task it supports.
Not to be used for: <e.g. clinical decisions, performance claims, publication without real validation>.

## 3. Cohort definition
| Parameter | Value | Source |
| --- | --- | --- |
| Cohort size | | |
| Age / sex structure | | |
| Conditions and prevalence | | |
| Comorbidities | | |
| Severity mix | | |
| Timeline span | | |

Source is one of: real data, published statistic (cite), clinician estimate, assumed.

## 4. Provenance
Seeding case: real seed data / schema only / from intelligence.

| Modality | Files | Tool | Version | Seed | Key parameters |
| --- | --- | --- | --- | --- | --- |

If real seed data was used, state which dataset, under what permission, and whether the
evaluation holdout was excluded from generation.

## 5. Labels
Which fields are labels. How each was derived. Whether derivation was independent of the
process that generated the content it labels. If an LLM produced both, state it here — it
invalidates downstream performance claims.

## 6. Coherence
The shared patient state and which fields it fixed.
Cross-modality links asserted (e.g. ECG heart rate follows the observations table).
Fidelity deliberately traded for coherence, and where.

## 7. Evaluation — fidelity
Univariate, multivariate, clinical plausibility. Tool used. Result per level.
State which levels could not run and why.

## 8. Evaluation — utility
TSTR result with the real-trained baseline and the gap, or the reason TSTR could not run.
Discriminator AUC and its reading in both directions.
If TSTR did not run: downstream utility is unproven. State it in those words.

## 9. Evaluation — privacy and disclosure
Checks run and results. Checks not run and why.
Free-text leakage assessment if the dataset contains text.
Conclusion, one of: safe to share / not safe to share / not established.
If not established, say what would need to run to establish it.

## 10. Limitations
Known gaps, unverified assumptions, modalities excluded, anything a reader would otherwise assume.
```

## Why the report replaces pass/fail thresholds

No threshold has been agreed for what fidelity score is acceptable. Inventing one would be false
precision. The report instead makes the basis of every claim explicit, so a reader can judge
fitness for their own use. A number without its method, provenance and unrun checks beside it is
not evidence.
