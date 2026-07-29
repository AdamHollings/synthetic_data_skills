---
name: synthetic-data-generation
description: Generate synthetic healthcare data for AI proof-of-concepts across any modality: tabular and EHR-style records, longitudinal patient pathways, clinical notes and free text, physiological signals and wearables (ECG, PPG, EEG, respiration, accelerometry), speech and clinical dialogue audio, genomics/omics (VCF, genotypes, expression), and medical imaging. Use when asked to create, generate, synthesise, simulate, mock, fake or fabricate patient data, test data, dummy records, a synthetic cohort or a demo dataset; when choosing between tools such as Faker, Mimesis, Plaitpy, DataSynthesizer, synthcity, Synthea/SyntheaUK, SynPath, NeuroKit2, SDialog, Bark, HaploDynamics, msprime or stdpopsim; when building from real seed data, from a schema or metadata only, or "from intelligence" with no seed data at all; and whenever one synthetic patient must stay coherent across several modalities. When the synthetic-data-generation skill is called, synthetic-data-evaluation must be called afterwards.
---

# Synthetic healthcare data generation

Routes a request to the tool reference for its modality. Read only the files the request needs.

The tools tables in `references/` are the sanctioned inventory. If a request needs something not
listed, say so and ask the user — recommending an unlisted tool requires user approval and a
source URL. Do not substitute from memory.

## Rules

**1. Coherence over per-modality fidelity.** No tool in `references/` coordinates with another.
Generate every modality from one shared patient state. Where higher per-modality fidelity would
break the shared story, take the lower fidelity.

**2. Labels separate from data.** Derive labels from the structured patient state before
generating the content that expresses them. Never let one LLM call produce both a narrative and
its ground-truth annotation. Validate against real holdout data where it exists.

**3. Privacy.** Synthetic is not automatically private, especially when fitted to real data.
Nothing leaves the environment without a privacy audit. Do not feed real patient data into a
tool, a prompt or a privacy checker without explicit user confirmation.

**4. Environment gate.** Prefer pure-Python, pip-installable tools. Flag Java, Julia, R, GPU,
PyTorch, large model downloads and pinned environments to the user before they become the plan.
Setup risks per tool are in each reference file.

Note: nothing has been installed or run in this environment. Setup claims come from an earlier
asset audit, which itself recorded that some assets were out of date, and from the asset
repositories read on 2026-07-29. Where they disagreed the repository was taken as correct. Three
corrections: SynPath (MIT, Python 3.7+, pip — the audit said "hard to set up"), SCN (MIT, Python
3.12, needs an LLM API) and TAPAS (MIT, Python 3.9+, pip — the audit recorded no setup notes).
None of the three has been verified by installing it; do that before committing to one.

## Inspiration assets

Most NHSE assets are inspiration: take the approach, do not plan to install them. Reference files carry an entry per asset giving source and date read, the pattern,
what to copy, what to substitute, what not to inherit, and caveats. Entries were written from the
sources on 2026-07-29.

Substitution is the point. Where an asset uses a specialist library for a step, an LLM call or
plain Python often does the same job with nothing to install — prefer that unless the caveats say
otherwise.

If a task needs detail an entry does not cover, ask the user or fetch the source URL. The target
environment may have no outbound network, so never make a fetch a dependency of the method.

## Step 1 — define the patient state

Do this before generating anything, including for single-modality requests.

Write a per-patient state object: demographics, conditions with onset dates, medications,
severity, progression, and the encounter timeline. Generate every modality from it.

- **Trajectory, not snapshot.** Decide the arc in the state; let modalities sample from it.
- **One clock.** All modalities share a single timeline.
- **Deterministic seeding.** One seed per patient per modality, derived from the patient ID.

Precedent: the Coherent Data Set layers structured pathway data into a longitudinal record and
attaches ECG, imaging, notes and genomic data via FHIR resources when a patient has a relevant
event. Cardiovascular-focused, a research artifact, not installable — replicate the approach.
See `references/healthcare-ehr.md`.

## Step 2 — route by modality

| Request | Read | First candidate |
| --- | --- | --- |
| Single table, flat records, schema to fill, multi-table | `references/tabular.md` | Faker/Mimesis; DataSynthesizer where distributions matter |
| Pathways, journeys, encounters over time, FHIR, activity data | `references/healthcare-ehr.md` | SynPath, Synthea/SyntheaUK as patterns |
| Notes, letters, discharge summaries, free text | `references/clinical-text.md` | SCN |
| ECG, PPG, respiration, EDA, EMG, EEG, wearables | `references/signals-wearables.md` | NeuroKit2 |
| Speech, consultation audio, dialogue, transcripts | `references/audio-speech.md` | SDialog |
| Genotypes, VCF, variants, expression, omics | `references/genomics.md` | HaploDynamics; msprime/stdpopsim for population realism |
| No seed data — build from domain knowledge | `references/from-intelligence.md` | Read before choosing any tool above |

Multi-modal requests read several files, after Step 1.

## Step 3 — route by seeding case

| Available | Approach |
| --- | --- |
| Real seed data, permitted | Fit a generator to it. Confirm permission first; privacy audit is then mandatory |
| Schema or metadata only | Template- and prior-driven generation (`references/tabular.md`); encode correlations explicitly |
| Domain knowledge only | Read `references/from-intelligence.md` first — this is a recorded open gap |

## Not supported

**Medical imaging** (CT, MRI, pathology, histology, DICOM, video). No reference file exists; there
is not enough assessed material to route on. What is known: medigan provides
pre-trained GANs for mammography, brain MRI, chest X-ray, endoscopy and cardiac MRI, GPU
recommended, with unresolved questions about loading large models in the target environment;
MONAI is mentioned only in passing for chest X-ray; RoentMod modifies existing chest X-rays
rather than generating new ones; video generation is computationally prohibitive; privacy
auditing of image data is unaddressed. State the position and confirm the approach with the user
before promising imaging output.

Narrower gaps are in their own files: handwritten and scanned letters (`clinical-text.md`); PSG
montages, Doppler/ultrasound, phone/mHealth passive sensing (`signals-wearables.md`);
pathological speech (`audio-speech.md`); proteomics, metabolomics, epigenomics, microbiome
(`genomics.md`). Check the relevant gaps section before accepting a request.

## Step 4 — write the report

Write `REPORT.md` alongside the data. Fill sections 1–6 (summary, intended use, cohort
definition, provenance, labels, coherence) at generation time. Template and rules:
`.claude/skills/synthetic-data-evaluation/references/report.md`.

## Step 5 — evaluate

Hand the dataset to the **synthetic-data-evaluation** skill, which completes sections 7–10 of the
report. Required before the data is used in a demo or leaves the environment. That skill handles
the no-real-seed-data case where train-on-synthetic/test-on-real is impossible.
