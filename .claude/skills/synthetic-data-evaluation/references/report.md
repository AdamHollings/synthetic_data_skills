# Dataset report

Every generated dataset gets a `REPORT.md` written alongside the data files. One document covers
provenance and evaluation. It is the deliverable that makes the dataset usable by someone who was
not present when it was generated.

## Rules

- Sections 1–6 are written during generation, before evaluation runs.
- Sections 7–10 are written by the evaluation skill.
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

For code-generated fields, Version is the package version or the commit SHA of a cloned repo, and
Seed is the RNG seed. For LLM-generated fields there is no seed: record the model ID under Version,
the temperature under Key parameters, and "none — not reproducible" under Seed. A seed recorded
against LLM-generated content is a false provenance claim.

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

### RAG summary

| Level | Scope | RAG | Summary |
| --- | --- | --- | --- |
| L0 | Schema conformance | 🟢/🔴 | X/Y tables pass; Z fields flagged |
| L1 | Univariate distributions | 🟢/🟡/🔴 | Worst Hellinger: X (field). N fields Amber or Red. |
| L1 | Missingness rates | 🟢/🟡/🔴 | N fields within range; M fields flagged |
| L2 | Multivariate associations | 🟢/🟡/🔴 | Key pairs checked; worst Cramér's V gap: X |
| L2 | Mode collapse (Gower) | 🟢/🟡/🔴 | NN distance distribution shape |
| L2 | Provider completeness | 🟢/🟡/🔴 | Variance present / absent (if provider-level) |
| L3 | Clinical plausibility | 🟢/🔴 | N rules checked; M violations found |

One row per evaluation category, not per field. The RAG rating reflects the worst result
in that category. Fields or pairs that scored Amber or Red are listed in the Detail section
below — Green items are not enumerated individually.

RAG bands defined in `fidelity.md`.

### Exceptions (Amber and Red)

| Field / pair | Metric | Value | RAG | Issue |
| --- | --- | --- | --- | --- |

Only items that did not score Green. Omit this table if all checks are Green.

### Detail

Univariate, multivariate, missingness, clinical plausibility results with full context.
Tool used. Result per level. State which levels could not run and why.

## 8. Evaluation — utility
TSTR result with the real-trained baseline and the gap, or the reason TSTR could not run.
Discriminator AUC and its reading in both directions.
If TSTR did not run: downstream utility is unproven. State it in those words.

## 9. Evaluation — privacy and disclosure
Checks run and results. Checks not run and why.
Free-text leakage assessment if the dataset contains text. Where an LLM did the entity extraction,
record its model ID and the generating model ID; if they are the same, say so and that the result
is a lower bound.
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

RAG bands (Green/Amber/Red) were introduced as interpretation guidance — they signal where to
look, not whether a dataset passes or fails. A Red rating means "investigate this metric," not
"reject the dataset." The RAG summary table gives at-a-glance readability; the detail section
provides the context needed to judge fitness for use.
