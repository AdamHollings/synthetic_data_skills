# broken_Arm_data — synthetic dataset report

## 1. Summary

One synthetic hospital admission note for one patient with a broken arm, in
`broken_Arm_data/data.csv`. Two columns, one row: `patient_id`, `note_text`. One modality
(clinical free text). The note is semi-structured — headed sections in the style of a
Trauma & Orthopaedics admission clerking (presenting complaint, history, examination,
imaging, procedure in ED, investigations, impression, plan).

The clinical scenario is a fragility distal radius fracture in an older woman after a
low-energy fall, unstable after closed reduction in ED and therefore admitted for volar
plate fixation. n=1.

Generated: 2026-07-29. Generator: synthetic-data-generation skill.
Reproduce with `scripts/generate_broken_arm_note.py`.

## 2. Intended use

A single worked example of a clinical admission note: something to test a text ingest path,
render in a UI, prototype a redaction or extraction prompt against, or show a stakeholder
what the text modality looks like. It is an example, not a dataset.

Not to be used for: training or evaluating any model (n=1); any performance, accuracy or
benchmark claim; any statement about how real admission notes are distributed in style,
length, structure or content; clinical reference, teaching or decision support. The clinical
content is plausible and internally consistent but has not been reviewed by a clinician
(section 10).

## 3. Cohort definition

| Parameter | Value | Source |
| --- | --- | --- |
| Cohort size | 1 patient, 1 note | User request |
| Age / sex structure | Female, age sampled uniformly from 65–79; realised age 78 | Assumed, no source. Fixed to the demographic in which fragility distal radius fracture is commonest, so that the scenario hangs together. Not a population sample |
| Conditions and prevalence | Fixed, not sampled: closed dorsally displaced comminuted intra-articular distal radius fracture, right, with ulnar styloid fracture. Neurovascularly intact. Unstable after closed reduction | Assumed, no source. Prevalence is meaningless at n=1 — this is one chosen presentation, not a draw from a distribution |
| Comorbidities | Fixed: hypertension, hypothyroidism, bilateral knee osteoarthritis. Penicillin allergy. No anticoagulation, no prior fragility fracture | Assumed, no source. Chosen as common, non-interacting comorbidity in this age group, and to justify the "avoid NSAIDs" line in the plan |
| Severity mix | Single severity: warrants admission and operative fixation. No mix — n=1 | Assumed, no source. An admission note requires a presentation that genuinely gets admitted; an uncomplicated distal radius fracture is usually discharged from ED with a cast, so instability post-reduction was chosen to make the admission coherent |
| Timeline span | Single day, 2026-07-29. Fall ~16:50, ED 17:25, radiographs 18:00, manipulation 18:25, ward clerking 19:00; surgery listed for 2026-07-30 | Generation date; intervals assumed |
| Mechanism | Mechanical fall from standing height onto outstretched hand, indoors | Assumed, no source |
| Social | Lives alone, ground-floor flat, independent, non-smoker | Assumed, no source. Chosen to make the occupational therapy line in the plan follow from the history |

Every number in this table is assumed. None is drawn from a published statistic, an audit,
or a real cohort.

## 4. Provenance

Seeding case: **from intelligence** — no real seed data was read, fitted to, or consulted.
Per `references/from-intelligence.md` this is a recorded gap in the skill: the output is
plausible, and its fidelity to any real corpus of admission notes is asserted, not measured.

| Modality | Files | Tool | Version | Seed | Key parameters |
| --- | --- | --- | --- | --- | --- |
| Clinical text (admission note) | `broken_Arm_data/data.csv` | Hand-authored template rendered by `scripts/generate_broken_arm_note.py`; Faker for the patient name | Faker 40.36.0, Python 3.11 | Master seed 20260729; per-patient seed = 20260729 + index, applied to both the RNG and the Faker instance | Reference date 2026-07-29; scenario and comorbidity as in section 3; semi-structured headed format per user choice |

No real seed data was used, so no permission question and no holdout exclusion applies.

**Model and prompt strategy.** No LLM API was called and no generative text model was run.
The prose is a single fixed template inside `render_note()`, authored once by the assistant
(an LLM) and committed to the repository, where it can be read and audited. At generation
time the pipeline is deterministic string interpolation: the template reads fields out of
the state dict and originates no clinical fact of its own.

This is the SCN pattern (`references/clinical-text.md`) with the per-note LLM call collapsed
into a reviewable artefact. The trade is deliberate and is a limitation as much as a
strength: it buys auditability and determinism at the cost of linguistic variety, which
matters at n=1 and would matter a great deal at n=100 (section 10).

SCN's augmentation stage — injecting typos, abbreviations and inconsistency so the text does
not read as clean model prose — was **not** implemented. The reference file calls this the
one asset in the audit that addresses the "clean LLM prose is a recognisable tell" problem.
Skipping it is a known fidelity gap, recorded in section 10.

Faker was chosen per `references/clinical-text.md`, which sanctions it for identifiers and
names inside letter templates. It was installed and run in `.venv/` — this note was actually
generated, not described.

## 5. Labels

**There is no label column in `data.csv`.** The user chose the note-text-only file layout, so
the structured fields the note renders are not emitted.

They do exist. `patient_state()` in `scripts/generate_broken_arm_note.py` fixes every clinical
fact as a typed field before any prose exists: `side`, `site`, `pattern`, `associated`,
`open_fracture`, `mechanism`, `dorsal_tilt_pre`, `dorsal_tilt_post`, `radial_height_loss_mm`,
`neurovascular_intact`, `compartment_syndrome`, `ed_procedure`, `reduction_stable`,
`management`, observations, bloods, PMH, medications, allergy. `render_note()` reads from that
dict and writes no clinical value of its own.

Derivation is therefore independent of the text in the way the skill requires: the fields were
not extracted from the note, the note was rendered from the fields. Anyone needing ground truth
for an extraction PoC can emit those fields as columns without regenerating the text.

**No LLM produced both a narrative and its annotation at generation time.** The residual
label-validity exposure is upstream and should be stated plainly: an LLM (the assistant) chose
the scenario and wrote the template. A PoC that extracts these fields from this note and scores
well has demonstrated that the extractor can read a template an LLM wrote — not that it can read
a real clerking. Per `references/clinical-text.md`, treat strong results on this note as an
artefact until shown otherwise on real held-out text.

## 6. Coherence

The shared patient state is `patient_state()`. It fixes identity (`patient_id`, name, sex,
date of birth, age, hospital number), the injury and its radiographic parameters, the ED
course, observations, bloods, past medical history, medications and social circumstances.

One clock: every timestamp in the note derives from a single `injury_datetime` by fixed
offsets, so fall → ED arrival → radiographs → manipulation → clerking is ordered by
construction and cannot be inverted by editing the template. The note references no event
later than the clerking, other than the explicitly future trauma list.

Internal links asserted within the note, all enforced by reading from one state:

- Age, sex and low-energy mechanism → the "fragility fracture" framing and the fracture
  liaison referral in the plan.
- `reduction_stable = False` and the post-reduction dorsal tilt → the impression "unstable
  after closed reduction" → the decision to admit and fix, which is what makes this an
  admission note rather than an ED discharge.
- `neurovascular_intact = True` and `compartment_syndrome = False` → the examination findings,
  and the escalation criteria in the plan are written as things to watch for, not things
  present.
- Hand dominance vs injured side → the "right-hand dominant" line.
- Antihypertensive in the drug history → "avoid NSAIDs" in the analgesia plan.
- Lives alone → the occupational therapy review.
- Penicillin allergy is recorded and no antibiotic is prescribed anywhere in the note.

Fidelity traded for coherence: the clinical scenario is **fixed rather than sampled**. Only
peripheral detail (name, age within band, hospital number, time of day, heart rate, blood
pressure, haemoglobin) varies with the seed. Sampling fracture site, mechanism, age and
management independently would give variety at n>1 but would readily produce incoherent
combinations — a child with a fragility fracture, an open fracture managed in a sling. Per the
skill's first rule, the lower-variety, coherent option was taken. Scaling this to a cohort needs
a set of internally consistent archetypes, not more randomness in these fields (section 10).

Cross-modality links: none. This is a single-modality dataset.

Cross-dataset links: none. `BA001` is **not** any of the ten patients in `data/patients.csv`;
the two datasets share no identifiers and were generated from separate states.

## 7. Evaluation — fidelity

Tool used: none. SynthGauge and synthcity both compare a synthetic set against a real reference
distribution; there is no real comparator here and no real corpus of admission notes was
accessed, so neither was applicable — not skipped. `scripts/clinical_rules.py` is named in
`references/fidelity.md` but is not built; the reference file says to build it sized to the
first real dataset's rules, and a declarative rule engine is not warranted at n=1. The checks
below were run instead as a one-off script over `data.csv` and the patient state, 48 checks in
five groups, and are reported per level.

**Level 1 — univariate: did not run.** Requires a reference distribution over note features
(length, section count, vocabulary, negation rate). There is none, and n=1 would not support a
distributional comparison if there were.

**Level 2 — multivariate: did not run as a cross-modal metric.** This is a single-modality
dataset, so there is no second modality to test agreement against. The one row of the
`references/fidelity.md` level-2 table that does apply — *clinical note ↔ structured record,
values stated in prose vs the structured record* — was run as note-versus-patient-state
agreement and is reported below. Note that this is a weaker test here than it would be for an
independently generated pair: the note was rendered from the state, so agreement is partly
guaranteed by construction. It is still worth running, because it catches clinical facts the
template asserts on its own, and it found a substantive one (F1).

| Check group | Checks | Result |
| --- | --- | --- |
| Structural | 7 | Pass — 1 row; columns `patient_id`, `note_text`; no empty cells; `patient_id` matches the state; all 13 headed sections present and in clerking order; 4,551 chars over 91 lines |
| Note ↔ state agreement | 7 | Pass — all 29 interpolated state values appear verbatim in the prose; all 3 past-medical-history items and all 3 medications with doses present |
| Timeline (one clock) | 2 | Pass — narrative times chronological: fall 16:50 → ED 17:25 → radiographs 18:00 → manipulation 18:25 → clerking 19:00; the only future-dated event is the listed trauma list on 30/07/2026 |
| Clinical plausibility (level 3) | 22 | Pass — detail below |
| Privacy / leakage screen | 10 | Pass — reported in section 9 |
| **Total** | **48** | **48 pass, 0 fail** |

**Level 3 — clinical plausibility: the primary evidence, as `references/fidelity.md` requires
when there is no comparator. 22 of 22 passed.** These are domain-logic checks written for this
scenario, not a generic metric:

| Check | Result |
| --- | --- |
| Stated NEWS matches NEWS2 recomputed independently from the six observations | Pass — recomputed 0, stated 0 |
| Stated age matches date of birth at the reference date | Pass — 78 |
| Fragility framing consistent with age and low-energy mechanism | Pass |
| Dorsal tilt improves after reduction (26° → 12°) | Pass |
| Residual tilt abnormal, so "unstable after closed reduction" is justified | Pass |
| Unstable reduction → operative management | Pass |
| Operative admission → nil by mouth documented | Pass |
| Closed injury → skin intact, no wound described | Pass |
| Closed injury → no antibiotics prescribed | Pass |
| Penicillin allergy recorded and no penicillin-class drug prescribed | Pass |
| NSAIDs avoided given age and antihypertensive, and none prescribed | Pass |
| Neurovascular status intact in the state → recorded intact on examination | Pass |
| Compartment syndrome absent, but escalation criteria present in the plan | Pass |
| Dinner-fork deformity consistent with dorsal displacement | Pass |
| No anticoagulant, and VTE risk assessment documented | Pass |
| Fragility fracture → fracture liaison / bone health referral | Pass |
| Fall → falls assessment | Pass |
| Lives alone → occupational therapy review before discharge | Pass |
| All seven blood results within adult female reference ranges | Pass |
| History "denies numbness" does not contradict intact sensation on examination | Pass |
| No sex/anatomy contradiction (no pregnancy, obstetric or male-specific content) | Pass |
| No reference to the uninjured limb being injured | Pass |

**Internal consistency against the cohort definition (section 3): passed.** Realised age 78 is
inside the declared 65–79 band; sex, side, fracture pattern, mechanism, comorbidity and
management match section 3 exactly; the timeline falls inside the declared single-day span.

**Regeneration is deterministic.** Re-running `scripts/generate_broken_arm_note.py` reproduces
`data.csv` byte-for-byte (SHA-256 `81900d0e0c06a707df0229193f99ae3b…`).

### Findings

**F1. Only about 13% of the note is traceable to the patient state; the rest is asserted by the
template.** Measured by matching every state value against the rendered text: 571 of 4,551
characters correspond to a state field. The remaining ~87% is clinical content the template
states on its own authority, including the entire 1,134-character PLAN section, the systemic
examination, the radiograph views, "Group and save sent", "ECG: sinus rhythm, no acute change",
and all 30 pertinent negatives ("no loss of consciousness", "no tenting or blistering", "no
carpal fracture", "C-spine non-tender").

Those assertions are clinically consistent — the 22 level-3 checks above test many of them — but
they are *not* in the structured record. The consequence is specific and matters for anyone
building on this: **if the state fields are emitted as ground truth for an extraction PoC, the
majority of extractable clinical content in the note has no corresponding label.** An extractor
that correctly pulls "nil by mouth from midnight" or "no carpal fracture" would be scored as a
false positive against a ground truth that does not contain them. Remedy: promote the plan
items, pertinent negatives and examination findings into the state so the note interpolates
them, rather than hardcoding them in prose. Not applied — it changes generator behaviour and is
the user's call.

**F2. The note is 88% invariant under reseeding.** Rendering with a different patient index
changes 11 of 91 lines: name, date of birth, age, hospital number, four timestamps, heart rate,
blood pressure and haemoglobin. Every clinical fact — fracture pattern, side, radiographic
angles, comorbidity, medication, the whole plan — is byte-identical. This is the section 6
coherence trade made visible and quantified. It is correct behaviour for n=1 and a hard ceiling
at n>1: this generator cannot produce a varied corpus, only reskinned copies of one note.

**F3. No SCN-style augmentation, confirmed by inspection.** The note contains no typos, no
abbreviation inconsistency, no copy-forward, no dictation artefacts and no ragged structure. It
reads as clean generated prose. `references/clinical-text.md` identifies this as the single
recognisable tell of synthetic clinical text and records SCN's augmentation stage as the only
assessed asset that addresses it. Flagged at generation time (section 4) and confirmed here.

Neither F1 nor F3 was handed back to the generation skill. F3 is a documented, accepted scope
decision recorded before evaluation ran; F1 is a consequence of the user's note-text-only file
layout rather than a defect in what was asked for. F2 is not a defect at all at n=1. All three
are recorded so a reader does not over-read what this note is.

Read this section beside section 9: this note is unlike any real note by construction — one
fixed template, invented identifiers — which is also why its disclosure risk is low. The two
are the same fact.

## 8. Evaluation — utility

**TSTR did not run.** It is impossible here. Train-on-synthetic/test-on-real requires a real
holdout, and this is the from-intelligence seeding case with no real data at all — no real
admission notes were accessed, and MIMIC-IV, the comparator named in
`references/clinical-text.md`, is real patient data that was not used. There is also no
prediction task and, at n=1, nothing to train.

**TSTS (train and test on synthetic) did not run.** `references/utility.md` offers it as the
weaker substitute when TSTR is impossible, to show the encoded signal is at least learnable.
One row cannot be split into a train and test set, so it is unavailable, not skipped.

**Discriminator AUC did not run** — it requires real notes to discriminate against. Worth
recording what the reading would be if it did: F1–F3 in section 7 say this note would be
trivially separable from real clerkings by structure and cleanliness alone. Per
`references/utility.md` that reads as poor fidelity, and per `references/privacy.md` the same
easy separability is the reason the disclosure risk in section 9 is low.

**Downstream utility is unproven.** No check performed here provides evidence that a model
trained or demonstrated on this note would behave the same way on real clinical text.

**Label provenance** (`references/utility.md` says read section 5 before any utility result):
no LLM call occurred at generation time, and the structured fields were fixed before the prose
was rendered, so no result here is inflated by a model reading its own annotation. The residual
exposure is upstream — an LLM chose the scenario and wrote the template — and is stated in
section 5. Combined with F1, any extraction score computed against this note should be
discounted rather than reported.

**Clinician review has not happened and is the strongest validation available.** With no real
comparator, `references/from-intelligence.md` puts clinician review above any metric. The 22
level-3 checks in section 7 are domain rules written by the same assistant that wrote the note,
which is a weaker form of the same claim. A single orthopaedic or ED clinician reading this one
note would take a few minutes and would carry more weight than everything in section 7.

## 9. Evaluation — privacy and disclosure

The dataset is free text, so the leakage path that structured metrics miss is in scope. The
three checks `references/privacy.md` specifies for the no-real-seed-data case:

1. **Did any real record inform generation, including via a prompt?** No. No real dataset was
   read, fitted to, or pasted into a prompt. No patient record, real or otherwise, entered the
   generation process. Every value comes from Faker or a seeded `random.Random` over the
   parameters in section 3, and the prose is a template committed to the repository. The dataset
   is seed-free, so the full audit — exact-match, nearest-neighbour distance, membership
   inference, attribute inference, TAPAS adversarial auditing — does not apply. Those checks are
   structurally inapplicable here, not skipped: each requires the real data a synthetic set was
   derived from, and there is none. No real patient data was loaded to run any check.
2. **Does LLM-generated free text surface memorised training content?** Reviewed, with an
   important structural mitigation and one caveat. The mitigation: no generative model runs at
   generation time. The note is deterministic interpolation over a fixed template, so the entire
   output space of this generator is the ~90 lines of `render_note()`, which any reader can
   inspect in full. This reduces the question from auditing an open-ended generative process to
   reading one bounded, committed artefact. On review the template is generic clinical
   boilerplate — standard clerking headings, textbook examination findings, routine trauma plan —
   with no distinctive phrasing, no unusual narrative detail and nothing that reads as recalled
   from a specific document. The caveat: that review was performed by the same model that wrote
   the template. `references/privacy.md` names exactly this bias, that a model may under-report
   what it generated, and recommends a different model for the assessment than for the
   generation. That has not been done.
3. **Could invented records collide with a real person by chance?** Low. Ten leakage-screen
   checks were run over the note text, all passing: no NHS-number-shaped string, no
   UK-postcode-shaped string, no street address, no phone number or email, no named hospital,
   trust or clinician, no real place name, no dates beyond the three the record requires (date
   of birth, admission, planned surgery), no identifier overlap with `data/patients.csv`, a
   hospital number in no real numbering scheme, and no rare or distinctive narrative details
   (occupation, immigration status, stigmatised diagnosis, notable circumstance) of the kind
   that make a free-text record identifying when every field looks unremarkable. Distinctiveness,
   not provenance, is what makes a record identifying, and this note is deliberately
   undistinctive — F2 in section 7 is the same property viewed as a fidelity weakness. The one
   residual is a Faker name paired with a date of birth, which could coincide with a real person;
   the coincidence would be unverifiable and would disclose nothing, since nothing real was
   encoded to be recovered.

**Checks that did not run, and why.** PrivFingerprint is the audit's designated route for
free-text privacy scoring and **did not run**: `references/privacy.md` records it as
inspiration-only, requiring Julia and OpenJDK for the pyCorrectMatch scoring stage, with the
substitute uniqueness measure an open decision. So the one tool aimed squarely at this
dataset's modality was unavailable, and no free-text privacy *score* was computed — the
assessment above is provenance and rule-based screening, not a metric. TAPAS did not run
(needs real data, inapplicable to a seed-free dataset). PrivacyLeakage did not run and does not
apply — it tests leakage from a model, and no model was trained or fine-tuned here. synthcity's
re-identification metrics did not run: they need a real reference set, and the PyTorch
dependency would need flagging first.

**Conclusion: safe to share.** The judgement rests on provenance and on the bounded, inspectable
template, not on a free-text privacy metric — no such metric was computed. There is no real
individual whose information could be disclosed by this note, because no real individual's data
entered its generation at any point, and the note carries no distinctive detail that could
single anyone out.

Two qualifications a reader should carry with that conclusion. The memorisation review in check
2 is a self-assessment by the generating model, which `references/privacy.md` warns is biased;
having a second reader — a person, or a different model — read `render_note()` would close it
cheaply and is the one thing worth doing before wide distribution. And the conclusion is scoped
to this file as it stands: adding real seed data, switching from the fixed template to live LLM
generation, or scaling to a corpus with varied narrative detail all invalidate it and require a
fresh audit, since varied free text is where the distinctiveness risk actually lives.

## 10. Limitations

- **n=1.** No distributional, statistical or performance claim is possible in either direction.
- **Fidelity to real admission notes is unmeasured.** From-intelligence seeding, no comparator
  corpus. MIMIC-IV is named in `references/clinical-text.md` as a style comparator but is real
  patient data and was not accessed.
- **No SCN-style augmentation.** No typos, abbreviations, inconsistency, dictation artefacts or
  copy-forward. Real notes contain all of these; this one reads as clean prose, which is a
  recognisable tell and the wrong distribution to train anything on. Confirmed by inspection at
  evaluation — finding F3, section 7.
- **One template means near-zero linguistic variety, now measured.** Re-seeding changes 11 of 91
  lines — name, date of birth, age, hospital number, four timestamps, heart rate, blood pressure,
  haemoglobin. Every clinical fact is byte-identical. Anything needing varied writing style needs
  a different method. Finding F2, section 7.
- **Most of the note's clinical content is not in the structured state.** Only ~13% of the note
  is traceable to a state field; the plan, systemic examination and all 30 pertinent negatives
  are asserted by the template. An extraction PoC scored against the state fields would penalise
  an extractor for correctly reading content the ground truth does not contain. Finding F1,
  section 7 — the most actionable defect found, and unfixed.
- **No free-text privacy metric was computed.** PrivFingerprint, the audit's designated tool for
  this modality, is inspiration-only and did not run (section 9). The safe-to-share conclusion
  rests on provenance and on the template being bounded and inspectable, not on a score.
- **The memorisation review is a self-assessment.** The model that wrote the template also
  reviewed it for memorised training content — the bias `references/privacy.md` explicitly warns
  about. A second reader would close this cheaply (section 9).
- **The scenario is fixed, not sampled** (section 6). This note represents one presentation of
  "broken arm" and does not span the range — no humeral, olecranon, both-bone forearm, paediatric,
  open or polytrauma presentations, and no non-operative pathway.
- **Not reviewed by a clinician.** `references/from-intelligence.md` states clinician review
  carries more weight than any metric when there is no real comparator. It has not happened. The
  22 clinical-plausibility checks that passed in section 7 were written by the same assistant that
  wrote the note, so they establish that the note is self-consistent, not that it is clinically
  right. This is the single highest-value outstanding action and would take one clinician a few
  minutes.
- **Invented identifiers.** The name is Faker-generated and the hospital number is a random
  7-digit integer in no real numbering scheme. A name–date-of-birth coincidence with a real person
  is possible but carries no information, since nothing real was encoded.
- **Downstream utility is unproven**, in those words. Neither TSTR nor TSTS could run (section 8),
  and no substitute evidence of utility exists.
- **Fidelity levels 1 and 2 never ran** and no fidelity metric was computed. The 48 passing checks
  in section 7 are clinical-plausibility and internal-consistency checks — the note agrees with the
  state it was generated from and violates no domain rule written for it. That is a weaker claim
  than resembling real clinical text.
- **The file name is `data.csv` as requested**, which carries no indication of contents; the
  directory name `broken_Arm_data` has mixed casing. Both were specified by the user and left
  as-is.
