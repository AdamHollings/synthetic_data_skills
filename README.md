# Synthetic healthcare data skills

An agentic proof-of-concept generator for healthcare AI. It produces realistic synthetic
healthcare datasets across modalities — tabular EHR records, longitudinal pathways, clinical text,
physiological signals and wearables, speech and dialogue, genomics — so that AI PoCs can be built
and demonstrated without touching real patient data.

The repository is mostly **two Claude Code skills** plus the scripts and data from the first dataset
built with them. The skills are the product; the dataset is the worked example.

## Repository layout

```
.claude/skills/
  synthetic-data-generation/    routes a request to the right tool per modality
  synthetic-data-evaluation/    fidelity / utility / privacy framework, and the REPORT.md template
data/broken_arm_day1/           first generated dataset + its REPORT.md
scripts/                        generation and evaluation code for that dataset
data_repos/                     read-only clones of reference repos (gitignored)
CLAUDE.md                       the operating instructions Claude follows in this repo
```

## The skills

Each skill is a lean router `SKILL.md` plus a `references/` folder holding the depth. Read the one
or two reference files a task needs, not the whole set.

[synthetic-data-generation](.claude/skills/synthetic-data-generation/SKILL.md) — an 8-step workflow:
agree scope and route by modality, assess and install pip-installable tools, clone only where
needed, write a data specification, sample a patient state with a seeded RNG, generate every
modality from that state, write the report, hand to evaluation. References cover
[tabular](.claude/skills/synthetic-data-generation/references/tabular.md),
[healthcare-ehr](.claude/skills/synthetic-data-generation/references/healthcare-ehr.md),
[clinical-text](.claude/skills/synthetic-data-generation/references/clinical-text.md),
[signals-wearables](.claude/skills/synthetic-data-generation/references/signals-wearables.md),
[audio-speech](.claude/skills/synthetic-data-generation/references/audio-speech.md),
[genomics](.claude/skills/synthetic-data-generation/references/genomics.md) and the no-seed-data case
in [from-intelligence](.claude/skills/synthetic-data-generation/references/from-intelligence.md).

[synthetic-data-evaluation](.claude/skills/synthetic-data-evaluation/SKILL.md) — three axes:
[fidelity](.claude/skills/synthetic-data-evaluation/references/fidelity.md) (univariate,
multivariate, clinical plausibility),
[utility](.claude/skills/synthetic-data-evaluation/references/utility.md) (TSTR, discriminator),
[privacy](.claude/skills/synthetic-data-evaluation/references/privacy.md) (exact-match, attribute and
membership inference, adversarial audit). The
[report template](.claude/skills/synthetic-data-evaluation/references/report.md) defines the
`REPORT.md` every dataset carries.

The tools tables inside `references/` are the sanctioned inventory — they are the authority on which
tools may be recommended, and carry licences, dependencies, verdicts and dates read. Adding one
requires user approval and a recorded source URL.

## Principles

- **Cross-modal coherence over per-modality fidelity.** Generate every modality from one shared
  patient state on one clock. Independent per-modality generation sharing only a patient ID is not a
  synthetic patient.
- **Labels separate from data.** Derive labels in code from the patient state *before* the content
  expressing them exists. Never let one LLM call produce both a narrative and its ground truth,
  otherwise a PoC can prove only that an LLM recognises its own output.
- **Generation and evaluation are one job.** Every dataset gets a `REPORT.md`: provenance
  (sections 1–6) written during generation, evaluation (sections 7–10) after.
- **Privacy is load-bearing.** Synthetic is not automatically private. Nothing leaves the
  environment without a privacy audit, and an unrun check is "not established", never "safe".
- **No pass/fail thresholds.** None has been agreed; reports state what was measured, what was not,
  and why.
- **Environment gate.** Prefer pure-Python, pip-installable tools. Java, Julia, R, GPU and large
  model downloads get flagged before they become the plan.

## Known gaps

- **Medical imaging is not supported.** Too little assessed material to route on, so there is no
  imaging reference file. Confirm the approach with the user before promising imaging output.
- **Nothing in the tools tables has been verified by running it.** Repository claims are still
  claims — install and smoke-test before committing to a tool.
- **`scripts/clinical_rules.py` and `scripts/tstr.py` are per-dataset, not general.** The rule
  checker exists for the broken-arm dataset; a reusable TSTR harness does not exist yet. Interfaces
  are specified in the fidelity and utility references. Build when a real dataset needs them.

## Worked example — `data/broken_arm_day1`

One synthetic patient, the first 24 hours after presenting to ED with a distal radius fracture:
11 clinical notes and nine structured tables (demographics, timeline, vitals, limb neurovascular
observations, bloods, medications, derived labels). Built for note-reading PoCs — information
extraction, summarisation, timeline reconstruction.

Seeding case is *from intelligence* (no real seed data). The structured tables reproduce exactly
from seed `20260217`; the LLM-written notes do not reproduce, and the report says so. Evaluation
verdict on sharing is **not established**, because free-text leakage scoring needs a second model
and only the generating model is reachable from this environment.

Read [data/broken_arm_day1/REPORT.md](data/broken_arm_day1/REPORT.md) for the full account — it is
also the best example of what a report from these skills looks like.

```powershell
.venv\Scripts\python.exe scripts\generate_broken_arm_day1.py            # regenerate (LLM calls)
.venv\Scripts\python.exe scripts\clinical_rules.py data\broken_arm_day1 # 21 plausibility rules
.venv\Scripts\python.exe scripts\text_identifier_scan.py data\broken_arm_day1
.venv\Scripts\python.exe scripts\extraction_smoke_test.py data\broken_arm_day1
```

## Setup

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`scripts/call_llm.py` is the project's LLM entry point, against Foundry-hosted models. It needs
`FOUNDRY_HOSTNAME` and `TOKEN` in a `.env` file (gitignored). It returns `None` when every attempt
fails — check before writing the result into a record. Smoke-test a single call before any batch:
retries back off quadratically, so one dead call burns ~9 minutes.

Use it where a step needs language (narrative, dialogue, free-text fields). Do **not** use it to
sample the patient state or derive labels — those are code with a seeded RNG.

## Using the skills

Open the repo in Claude Code and ask for what you need ("generate a synthetic cohort of…",
"is this dataset safe to share?"). The skills trigger from the request, and `CLAUDE.md` supplies the
operating rules. Both are readable on their own if you want the methodology without the agent.
