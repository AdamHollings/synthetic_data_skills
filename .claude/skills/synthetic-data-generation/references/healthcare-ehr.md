# EHR records and longitudinal pathways

## Applies to

Patient journeys rather than snapshots: encounters over time, care pathways, FHIR resources,
longitudinal event sequences, disease progression, hospital activity. Also read this when a
request is phrased as flat records but the PoC needs a trajectory.

## Standing decision

Whether NHSE assets are run or used as reference is settled: **inspiration approach**. Read the
approach, reimplement in Python, do not plan a PoC around installing them.
SCN is the exception recorded as easy to set up.

## Tools

| Asset | Use for | Verdict | Constraints |
| --- | --- | --- | --- |
| SynPath / SynPathD (`nhsx/SynPath`) | Agent-based pathway simulation, FHIR v4 output. Strongest UK-specific pathway reference | Runnable — see entry below | MIT, Python 3.7+, pip. The audit's "hard to set up" is not supported by the repository |
| SCN (`nhsengland/synthetic_clinical_notes`) | LLM pipeline generating pathways with matching clinical notes | Runnable — see entry below | MIT, Python 3.12, needs an LLM API |
| SyntheaUK (`nhsengland/swpc_synthea`) | Longitudinal event sequences generated natively; module/rule-based clinical knowledge | Inspiration | Apache 2.0, JDK 11+, Gradle — Java is the blocker |
| Synthea | Superseded here by SyntheaUK | No | — |
| synthcity time-series plugins | Generic longitudinal series, irregular time series, censored data, survival | Maybe | PyTorch — see `tabular.md` |
| TimeGAN / ydata-synthetic | Generic tabular time series | Unassessed | Named in the audit's gap assessment only; no setup notes or verdict |
| DLH_007 (Confluence, Data Linkage Hub) | Synthetic linked datasets for benchmarking data linkage methods | Unsure | Internal Confluence only, not fetchable, so no entry can be written. Active research project, may not be ready — ask the user |
| MIMIC-IV v3.1 | Real dataset. Comparator for longitudinal structure; holdout that makes TSTR possible | Reference only | Real patient data — not a generation input without permission and governance confirmation |

Artificial HES data is recorded in `tabular.md`.

## Inspiration entries

Read the source before reimplementing. Entries written from the repositories on 2026-07-29. If a
task needs detail these do not cover, ask the user or fetch the URL — but the target environment
may have no outbound network, so do not make a fetch a dependency.

### SynPath

`github.com/nhsx/SynPath` — MIT, Python 3.7+, pip, `nox` for tests. 67 commits, 13 open issues.

- **Pattern:** two agent types. `PatientAgent` holds patient state and the medical record;
  `EnvironmentAgent` represents a facility (hospital, GP). A pathway is a sequence of environment
  visits; each visit triggers interactions that update the patient record. Simulation runs
  step-by-step for one patient at a time, stopping on max steps, elapsed time or an event such as
  death.
- **Copy:** the separation of agents from an **intelligence layer** — a directory of Python
  interaction functions holding the decision rules, with agents configured by JSON. Clinical logic
  is swappable without touching the simulation loop, which is exactly what a PoC generator needs.
  Also copy: the record is built by events rather than sampled.
- **Substitute:** the intelligence layer is the intended extension point — write our own decision
  functions, or drive them from an LLM. FHIR conversion uses `fhir.resources` (pip) with optional
  validation against a HAPI FHIR server.
- **Don't inherit:** nothing blocking identified.
- **Caveats:** the audit records "could be hard to set up, particularly on FDP", which the
  repository does not support — it is pure Python and pip-installable. Verify before relying on
  the audit's verdict either way. One patient at a time means cohort generation is a loop; check
  runtime before promising large cohorts. Inputs are `config.json`, an intelligence directory, and
  patient/environment data as JSON or CSV.

### SCN — synthetic clinical notes

`github.com/nhsengland/synthetic_clinical_notes` — MIT code, OGL 3.0 docs, Python 3.12, actively
maintained by the NHS England Data Science team.

- **Pattern:** five sequential stages — create synthetic patient, generate a realistic admission
  reason (emergency or elective), simulate the journey from admission to pre-discharge, generate a
  clinical note for each stage of that journey, then augment notes with typos and medical
  abbreviations.
- **Copy:** notes generated per journey stage rather than per patient, so documentation follows
  the pathway instead of existing alongside it. Also copy the augmentation stage — realistic notes
  are not clean notes, and this is the only asset in the audit that addresses it.
- **Substitute:** the LLM. It uses OpenAI `gpt-4o` via API, but `call_llm` and `read_write_data`
  in `src/processing.py` are explicitly the platform-specific, replaceable functions — swap
  `call_llm` for whichever model is available. Prompts, templates and schemas live in
  `src/prompts.py`, `src/doc_templates.py`, `src/schemas.py`, with guidance in
  `docs/adapting_the_pipeline`.
- **Don't inherit:** the Palantir Foundry assumptions; the repository states it is intentionally
  platform-agnostic and confines those assumptions to the two functions above.
- **Caveats:** an LLM writes both the journey and the notes, so labels for any downstream task
  must be derived separately — see `clinical-text.md`. Output realism depends entirely on prompt
  and template quality, which is where the work actually is.

### SyntheaUK

`github.com/nhsengland/swpc_synthea` — Apache 2.0, JDK 11+, Gradle. Adaptation of a Synthea fork
taken 15 May 2024, with incompatible changes for NHS England. 4,919 commits. Documentation at
`nhsengland.github.io/swpc_synthea/`.

- **Pattern:** module-based clinical modelling. Disease progression is expressed as declarative
  modules of states and transitions rather than sampled from data, which is how it produces
  coherent longitudinal histories without seed data.
- **Copy:** the module concept — encode clinical knowledge as explicit state machines per
  condition, with the patient moving between states over time.
- **Substitute:** the whole runtime. Reimplement modules in Python; the value is the modelling
  approach, not the Java.
- **Don't inherit:** JDK 11+ and Gradle.
- **Caveats:** the README does not enumerate output formats or document how the UK modules differ
  from upstream — that detail is in the MkDocs site, so fetch it or ask the user if the difference
  matters. Java remains the reason this stays inspiration.

### Coherent Data Set

No URL has been recorded for this. Ask the user for a source before relying on detail beyond the
description below.

## Cross-modal precedent: the Coherent Data Set

Layers structured Synthea data into a longitudinal patient-level EHR, attaching ECG, MRI imaging,
clinical notes and genomic data via standard FHIR resources when a synthetic patient has a
relevant event. Cardiovascular-focused; a research artifact, not installable — replicate the
approach.

Transferable mechanism: modality artefacts are created by pathway events, so nothing exists that
the patient's timeline does not account for.

Diffusion-based work such as Coherent Denoising targets filling in a patient's missing modalities
consistently with what is known. Cited in the audit to establish that cross-modal coherence is an
open research problem. Do not promise a general solution.

## Gaps

- Cross-sectional schema → temporally coherent multi-visit trajectory. Partial gap; the tooling
  does not do this for you.
- Temporal realism generally. Most generators produce snapshots or independent draws, not arcs
  where labs drift, medications change and signals shift with progression. Combining a genomics
  tool, a signal simulator and an LLM generator yields three disagreeing timelines. Where a
  progression needs a mechanism rather than interpolation, PySim (differential equations, assessed
  Yes) can drive it — see `signals-wearables.md`.
- Cross-modal coherence has no off-the-shelf solution.

## Coherence

This file owns the shared timeline. The pathway determines when encounters occur and therefore
when each modality has an artefact: an ECG exists because a cardiology appointment produced one; a
note exists because a consultation happened. Generate the pathway first, hang other modalities off
its events.

## Report

Contributes to report sections 3 (timeline span), 4 (pathway generator and parameters) and 6 (the
event model linking modalities).

## Evaluation

Temporal and cross-modal coherence surface as multivariate fidelity failures —
`synthetic-data-evaluation`, `references/fidelity.md`. Pathway plausibility (event ordering,
medication–condition pairing) belongs to the same clinical rules layer.
