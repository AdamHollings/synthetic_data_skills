# Generating from intelligence (no seed data)

## Applies to

No real dataset to fit to. Available input is domain knowledge: a clinical scenario, a schema,
published prevalences, a cohort description. Read this before choosing a tool from any other
reference file — the seeding case constrains tool choice as much as the modality does.

## Status

Generating "from intelligence" is a recorded **gap**: it needs research to establish whether a
suitable tool exists. Generating from real data, by contrast, is well covered.

Consequences:

- Do not present this as a solved capability.
- Output is plausible; its statistical fidelity to any real population is asserted, not measured.
  State this to the user before starting and record it in report section 10.
- Several assessed tools do generate from parameters rather than seed data. The rest of this file
  is what the audit supports.

## What generates without seed data

**Encoded priors in templates.** Plaitpy: YAML templates with distributions and conditional logic,
correlations written explicitly (age ↔ condition prevalence). Maintenance risk — see `tabular.md`.
Faker and Mimesis fill surrounding detail; Mimesis extends with custom medical providers. Neither
contributes inter-field logic.

**Rule/module-based clinical knowledge.** Synthea's module approach models medical history from
clinical rules rather than a dataset. Inspiration, Java-based — reimplement the pattern. See
`healthcare-ehr.md`.

**Agent-based state modelling.** SynPath simulates pathways with per-patient agents in FHIR v4.
Inspiration. The pattern — agents whose state evolves under rules — is the direct route from domain
knowledge to a trajectory.

**Parameterised simulators needing no input files.** The strongest position here, because the
domain model is inside the tool:

- HaploDynamics — VCF genotype data from population, LD and mutation-rate parameters
  (`genomics.md`).
- NeuroKit2 — ECG, PPG, respiration, EDA, EMG from physiological parameters
  (`signals-wearables.md`).
- PySim — differential-equation models where a mechanism, not a trace, is required.
- msprime and stdpopsim — population-scale simulation using published, validated demographic
  models. stdpopsim supplies peer-reviewed domain knowledge in place of invented parameters.

**LLM role-play and narrative.** The NoteChat pattern and SDialog personas generate text and speech
from description alone; SCN generates pathways with matching notes and is recorded as easy to set
up on FDP. See `clinical-text.md` and `audio-speech.md`. The audit identifies this pattern as
well suited to an agentic PoC generator.

**Synthetic Panels** (`nhsengland/synthetic_panels`) generates a synthetic panel of respondents
reacting to messaging — persona simulation for survey and communications research rather than
clinical records. Inspiration; the audit records it as WIP and unproved.

- **Source unavailable.** `github.com/nhsengland/synthetic_panels` returned HTTP 404 on
  2026-07-29: private, renamed or removed. Ask the user for a working link before relying on it,
  and do not describe its method beyond the one-line audit description above.

## Method

Failure mode: asking an LLM for "50 realistic diabetic patients" and receiving 50 fluent, near-
identical records with no defensible distributions.

1. **Write the cohort definition.** Size, age/sex structure, condition prevalences, severity mix,
   comorbidity patterns, timeline span. Record the source of every number, including "assumed".
   This populates report section 3.
2. **Sample the patient state from that definition in code**, with a seeded RNG. Not with an LLM:
   LLM sampling collapses variety and produces distributions that cannot be audited.
3. **Derive labels from the state** before any content exists.
4. **Generate each modality from the state**, using parameterised simulators where they exist and
   LLM generation only where language is required.
5. **Record the definition in the report.** With no real comparator, the cohort definition is the
   specification the data is evaluated against.

## Label-validity trap

Highest risk in this file. If the synthetic data and the demonstrated AI are both LLM-driven, the
PoC can prove only that an LLM recognises its own output.

- Labels come from the structured state, fixed before the content expressing them is written.
- No single call produces both a narrative and its ground-truth annotation.
- Validate against real holdout data where any exists, even a small sample.
- Treat strong downstream results on this data as likely artefacts until shown otherwise.

## Governance

The related question is settled by the inspiration approach: assets inform what is built rather
than being run directly. Domain knowledge, published statistics and clinical
description are acceptable inputs. Real patient records are not, and must not be pasted into a
prompt without explicit permission and governance confirmation. If a real record informs generation
indirectly, the dataset is no longer seed-free and the privacy audit changes.

## Coherence

The patient state is written from scratch, so it can be internally consistent from the start. That
holds only while every modality reads from it. A modality generated from a fresh prompt rather than
the state loses the property.

## Report

Contributes sections 3 (cohort definition with sources), 4 (seeding case: from intelligence), 5
(label derivation) and 10 (fidelity to any real population is unmeasured).

## Evaluation

TSTR is impossible — no real holdout exists. Do not drop the utility axis. See
`synthetic-data-evaluation`, `references/utility.md`: clinical plausibility becomes the primary
signal, internal consistency replaces external fidelity, and the report states that downstream
utility is unproven. Clinician review of a sample carries more weight here than any metric.
