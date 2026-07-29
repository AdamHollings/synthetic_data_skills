# Privacy

Non-negotiable for healthcare. Synthetic is not automatically private: a generator fitted to real
data can memorise and reproduce it, and a record need not be copied verbatim to identify someone.

## Governance before method

An unresolved governance question sits underneath this axis: how does an agent interact with
privacy tooling without ingesting real data? If PrivFingerprint identifies a collision and the
agent sees that output, the output is itself a disclosure question. The project's decision is the
inspiration approach: these assets inform what is built rather than being run by the agent over
real data.

- Do not load real patient data to run a privacy check unprompted.
- Membership inference and exact-match testing structurally require real data alongside synthetic.
  When one is needed, stop and confirm with the user how and by whom it should be run. It may be a
  human-run step.
- Treat the output of a privacy check as potentially disclosive, not just its input.

## Fidelity–privacy tension

Data reproducing real records exactly is both maximally faithful and maximally leaky. Report the
fidelity result beside the privacy result. A discriminator that cannot distinguish synthetic from
real is an alarm, not a success (`utility.md`).

## Checks, weakest to strongest

**Exact-match.** Is any synthetic record identical to a real one? Necessary and, per the audit,
nowhere near sufficient. Passing means little; failing is disqualifying. Nearest-neighbour distance
extends it to near-copies.

**Attribute inference.** Can sensitive attributes be predicted from quasi-identifiers? A real
leakage mode with no record copied.

**Membership inference.** Can an attacker establish that a specific real individual was in the
training data? With attribute inference, this is what the audit calls the real test.

**Adversarial auditing.** Can an attacker infer real records from synthetic ones under an explicit
threat model?

## Tools

| Tool | Use for | Verdict | Constraints |
| --- | --- | --- | --- |
| TAPAS / SAS (`alan-turing-institute/tapas`) | Adversarial privacy auditing: specify an attacker, test what they recover | Runnable — see entry below | Python 3.9+, pip or Poetry, MIT. The audit recorded no setup notes; the repository shows a pip-installable package with a CLI |
| PrivFingerprint (`github.com/nhsengland/privfp-experiments`) | Privacy risk scoring for free-text data | Inspiration — partly reusable, see below | Julia and OpenJDK, but confined to stages we do not need |
| PrivacyLeakage (`nhsengland/priv-lm-health-extended`) | Privacy risks and mitigations in healthcare language models, where leakage sits in the model as well as the data | Inspiration | Hard to set up, particularly on FDP |
| synthcity | Runnable metrics: re-identification risk scoring, attribute prediction from quasi-identifiers via XGBoost or neural net | Maybe | PyTorch — flag before use. The only option here shipping runnable privacy metrics |
| NDRS Pseudonymiser | Unknown | Unknown | No description, link or considerations recorded in the audit, so no entry can be written and no source can be fetched — ask the user before treating it as an option |
| DataSynthesizer | Generation-side mitigation: differential-privacy modes | Use | Where privacy is the binding constraint, regenerating with DP may be the fix rather than auditing harder. See the generation skill's `references/tabular.md` |

Free text is the leakage path structured metrics miss: an unusual combination of narrative details
can identify someone when every field looks unremarkable. PrivFingerprint is the audit's route for
this.

## Inspiration entries

Read the source before reimplementing. Entries written from the repositories on 2026-07-29. If a
task needs detail these do not cover, ask the user or fetch the URL — but the target environment
may have no outbound network, so do not make a fetch a dependency.

### TAPAS / SAS

`github.com/alan-turing-institute/tapas` — MIT, Python 3.9+, pip or Poetry, CLI `tapas`,
docs on ReadTheDocs. Houssiau et al. 2022 (NeurIPS). 73 commits, 45 open issues.

- **Pattern:** define an attacker and a threat model, then measure what that attacker recovers
  from the synthetic data. Privacy as an attack outcome, not a distance metric.
- **Copy:** the four abstractions — attacker, threat model, dataset, generator wrapper. The
  generator wrapper is what makes results comparable across generators rather than one-off.
- **Substitute:** the generator wrapper for whatever we generate with.
- **Don't inherit:** nothing blocking identified.
- **Caveats:** the audit recorded this as inspiration with no setup notes, but it is a
  pip-installable Python package — verify that in the target environment, because if it installs
  it is the only real adversarial audit available to us. Attacks need the real data the synthetic
  set was derived from, so it does not apply to seed-free datasets, and running it is subject to
  the governance rule above.

### PrivFingerprint

`github.com/nhsengland/privfp-experiments` (Privacy FingerPrint Phase 2) — MIT code, OGL 3.0
docs, experimental, ~103 commits.

- **Pattern:** three stages — generate text, extract sensitive entities from it, score how
  identifying the resulting combination is.
- **Copy:** the stage separation, and scoring on extracted entities rather than raw text.
- **Substitute:** entity extraction. They use GLiNER (primary), spaCy, scispaCy, SpanMarker,
  UniversalNER and Numind NER; an LLM call does the same job with nothing to install.
- **Don't inherit:** Synthea (hence OpenJDK) for the generation stage — we generate our own text;
  Ollama, llama.cpp and local Llama models for the same reason; the HomeBrew/Mac install steps.
- **Caveats:** Julia is required only by pyCorrectMatch in the scoring stage, so it is the
  scoring metric itself — substituting it means choosing another uniqueness measure, which is the
  open decision here. If the same LLM wrote the text and extracts the entities, it may
  under-report exactly what it generated, which is the label-validity trap in privacy form; use a
  different model for extraction than for generation. LLM extraction is also non-deterministic —
  acceptable for exploration and flagging, weak for a score that must be reproduced or defended.

### PrivacyLeakage

`github.com/nhsengland/priv-lm-health-extended` — MIT code, OGL 3.0 docs. NHS England PhD
internship, July–December 2024. Marked experimental and unsuitable for production without further
evaluation; current maintenance unclear.

- **Pattern:** two separable work packages — memorisation experiments (does the model retain
  training data) and privacy-in-context (how clinical information is handled during document
  processing).
- **Copy:** the split. Leakage from a model and leakage from a dataset are different questions and
  need different tests. Relevant whenever a PoC fine-tunes or trains on synthetic health data.
- **Substitute:** the model under test. Tested with Llama-3.1-70B but stated to work with compact
  alternatives such as SmolLM2-135M, so the method does not require large-model infrastructure.
- **Don't inherit:** the separate per-work-package environments unless running their code directly.
- **Caveats:** repository contains only public or fake data, and the same applies here — do not
  supply real records to reproduce it. Applies to the model, not the dataset, so it does not
  replace the dataset checks above.

## Gaps

- **Image data.** The audit rates privacy of synthetic output as broadly covered by NHS tooling
  except for images. Nothing assessed audits synthetic medical images for disclosure risk.
- **Audio.** Not addressed. Voice is biometric; raise it if audio may leave the environment.
- Most of the strongest tools are inspiration-only, so the runnable set is thinner than the asset
  list implies. Record this in report section 9 rather than implying a full audit ran.

## No real seed data

Risk is lower, not zero. Check:

1. Whether any real record informed generation, including via a prompt. If so, the dataset is not
   seed-free and the full audit applies.
2. Whether LLM-generated free text surfaces memorised training content. Review a sample.
3. Whether invented records collide with real people by chance in a small, distinctive population.
   Distinctiveness, not provenance, makes a record identifying.

## Report

Section 9. Record checks run with results, checks not run with reasons, free-text leakage
assessment where text is present, and a conclusion of one of: safe to share, not safe to share, not
established. Where the checks that would justify sharing could not run — inspiration-only tooling,
or a check requiring real data the agent must not touch — the conclusion is "not established", not
"safe". State what would be needed to establish it and route the decision to the user.
