# broken_arm_day1 — synthetic dataset report

## 1. Summary

One synthetic patient, one hospital encounter, the first 24 hours after presenting to an emergency
department with a broken arm. The patient is a 68-year-old woman who fell onto an outstretched hand
on ice, sustaining a closed dorsally displaced extra-articular fracture of the left distal radius
with an ulnar styloid avulsion. She is given analgesia, X-rayed, has a closed reduction under
haematoma block in ED, and — because the check film shows residual dorsal angulation — is admitted
to a trauma ward and listed for open reduction and internal fixation on day 2. The dataset spans
09:20 on 17/02/2026 (the fall) to 09:00 on 18/02/2026, and contains 11 clinical notes plus nine
structured tables covering demographics, timeline, vital signs, limb neurovascular observations,
blood results, medication administrations and derived labels.

Generated: 2026-08-03. Generator: synthetic-data-generation skill. Repository commit at generation:
`e6a5bb4`.

## 2. Intended use

Built as a proof-of-concept substrate for AI applications that read a hospital record: clinical
information extraction (pull the fracture site, pattern, procedure and plan out of free text and
check against `labels.csv`), note summarisation, timeline reconstruction, note-versus-observation
consistency checking, and demonstrations of how structured and unstructured hospital data sit
together for a single patient.

Not to be used for: clinical decisions, model performance claims, statistical statements about any
real fracture population, training a model intended for deployment, or publication without real
validation. It is one patient — it has no distribution.

## 3. Cohort definition

| Parameter | Value | Source |
| --- | --- | --- |
| Cohort size | 1 patient, 1 encounter | Specified by user |
| Age / sex structure | Sampled: sex female with p=0.68, age ~N(71, 8) clipped to 52–88 for female; male ~N(66, 10) clipped 45–84. Realised: female, 68 | Assumed. Skew toward older women reflects the fragility-fracture presentation, but no published statistic was consulted |
| Presenting condition | Closed dorsally displaced extra-articular distal radius fracture (Colles'-pattern) with ulnar styloid avulsion, minimal dorsal cortical comminution, no intra-articular extension | Fixed by the scenario ("broken arm"); pattern chosen as the commonest adult wrist fracture. Assumed, no source |
| Mechanism | Fall from standing height onto outstretched hand (FOOSH), fragility mechanism | Assumed |
| Injured side | Sampled: right p=0.55; realised left. Dominant hand sampled right p=0.90; realised right | Assumed |
| Comorbidities | Sampled independently from a weighted list: hypertension 0.55, osteoporosis 0.45, T2DM 0.20, hypothyroidism 0.15, hypercholesterolaemia 0.35, knee OA 0.25. Osteopenia added if female, ≥65 and osteoporosis not drawn. Realised: essential hypertension, osteopenia | Assumed, no source. Prevalences are plausible-for-age guesses, not population figures |
| Allergies | 0.6 no known drug allergies, else penicillin rash. Realised: penicillin — rash | Assumed |
| Severity mix | Single fixed severity: displaced but closed, neurovascularly perfused throughout, transient median nerve paraesthesia at presentation resolving after reduction, reduction inadequate therefore operative fixation. NEWS2 0–1 throughout, no deterioration | Scenario definition, chosen to be a routine rather than a critical admission. Assumed |
| Vital sign ranges | Baseline HR 70–80, systolic 128–142, diastolic 72–84, then fixed arc offsets for pain, post-analgesia and post-reduction states, plus ±3–4 jitter | Assumed. Direction of change (tachycardia with pain, settling after reduction) is clinically conventional; magnitudes are invented |
| Blood result ranges | Sampled within stated reference intervals, except eGFR (computed) and vitamin D (28–46 nmol/L, deliberately low) | Reference intervals are conventional UK adult ranges, recorded in `labs.csv`. Sampling ranges assumed |
| eGFR | Computed from creatinine, age and sex with the CKD-EPI 2021 race-free equation, not sampled | Published equation, implemented in `scripts/broken_arm_day1_state.py`. Used so creatinine and eGFR cannot contradict each other |
| Timeline span | 09:20 17/02/2026 to 09:00 18/02/2026 (23h 40m). Admission date is arbitrary and synthetic | Specified by user ("first day") |

## 4. Provenance

Seeding case: **from intelligence** — no real seed data, no real record, nothing fitted to real
data. The cohort definition above is the specification, and per
`references/from-intelligence.md` this is a recorded gap in the skill: the output is plausible, and
its statistical fidelity to any real population is asserted, not measured.

| Modality | Files | Tool | Version | Seed | Key parameters |
| --- | --- | --- | --- | --- | --- |
| Patient state, timeline, vitals, limb obs, labs, medications, labels | `patient.csv`, `conditions.csv`, `events.csv`, `observations.csv`, `limb_observations.csv`, `labs.csv`, `medication_administrations.csv`, `regular_medications.csv`, `labels.csv` | `scripts/broken_arm_day1_state.py` (project code, Python `random.Random`) | Python 3.11.3 | 20260217 | NEWS2 computed by `news2()` (SpO2 scale 1); eGFR by `ckd_epi_2021()` |
| Names, address, postcode | `patient.csv` | Faker, `en_GB` locale | 40.36.0 | 20260217 (`seed_instance`) | Identifiers only; no clinical content |
| NHS number | `patient.csv` | Project code | — | 20260217 | Synthetic 999 test range, valid mod-11 check digit |
| Clinical notes | `clinical_notes.csv` | `scripts/call_llm.py` → Foundry-hosted model | `ri.language-model-service..language-model.gpt-5-1` | none — not reproducible | temperature 0.4, 11 independent calls, no chat history. Prompt built by `facts_block()` from the state, filtered to each note's own timestamp |
| Note typo augmentation | `clinical_notes.csv` (`typo_edits_applied`) | `scripts/generate_broken_arm_day1.py` `augment()` | — | 20260218 | Max 2 misspellings per note, nursing and triage notes only, drawn from a fixed 8-word list of non-clinical words. Never applied to numbers, drug names, doses or findings |

No real seed data was used, so no holdout question arises and nothing real was placed in a prompt.

Regenerating the structured tables from the same seed reproduces them exactly. The note text does
not reproduce: the LLM exposes no seed, and a seed recorded against it would be a false claim.

The typo augmentation follows the SCN pattern (`nhsengland/synthetic_clinical_notes`, MIT), noted in
`references/clinical-text.md` as the only assessed asset that addresses the "clean LLM prose" tell.
No SCN code was copied or cloned; only the idea of a post-generation augmentation stage.

## 5. Labels

`labels.csv` holds 26 label rows. Every one is derived in code by `derive_labels()` in
`scripts/broken_arm_day1_state.py`, from the patient state and the code-built tables, and is written
**before any note text exists**. The generation script enforces the order: state → tables → labels →
prompts → notes.

Three derivation classes, recorded per row in the `derivation` column:

- **Scenario definition (fixed).** `fracture_present`, `fracture_site`, `fracture_pattern`,
  `open_fracture`, `comminution`, `intra_articular_extension`, `closed_reduction_performed`,
  `reduction_adequate`, `admitted`, `planned_operation` and similar. These are the scenario the user
  asked for, written into the state object.
- **Sampled in code.** `injured_side`, and `dominant_hand_injured` as a comparison of two sampled
  fields.
- **Computed from the structured tables.** `peak_pain_score_day1` and `max_news2_day1` (maxima over
  `observations.csv`, where NEWS2 itself is computed by `news2()`),
  `pain_controlled_after_reduction`, `escalation_of_care_required` (threshold on max NEWS2),
  `paraesthesia_resolved_after_reduction` (from `limb_observations.csv`),
  `opioid_administered_day1` and `vte_prophylaxis_given_day1` (from
  `medication_administrations.csv`).

No LLM produced a label, and no single call produced both a narrative and its ground truth. The
notes are a rendering of the labels, not their source.

The label-validity trap is not fully escaped, however, and this is the dataset's main methodological
limitation. The labels are independent of the text, so extraction accuracy is a fair measure of
*whether a model can read the note*. But the note was written by an LLM from a fact list, so
extraction is easier than on real notes — the facts are present, well-formed and uncontradicted. A
strong extraction score here should be read as a smoke test, not as evidence of real-world
performance.

## 6. Coherence

One patient state object (`build_state()`), one clock (all timestamps derive from
`ADMISSION_DAY = 2026-02-17` via `_t()`), and every table and every note generated from that state.

Fields the state fixed, and which downstream artefacts read them:

| State field | Consumed by |
| --- | --- |
| Demographics, PMH, allergies, social history | `patient.csv`, `conditions.csv`, `regular_medications.csv`, and the header of every note prompt |
| Injured side, dominant hand | `patient.csv`, `labels.csv`, `limb_observations.csv`, all 11 notes |
| Diagnosis and radiographic features | `conditions.csv`, `labels.csv`, both radiology reports, the T&O and consultant notes |
| Event timeline | `events.csv`, and the cut-off that filters every note prompt |
| Vitals arc and pain arc | `observations.csv` (NEWS2 computed from the vitals), quoted in the triage, clerking, procedure, pre-op, nursing and ward-round notes |
| Limb neurovascular arc | `limb_observations.csv`, and the paraesthesia thread running through notes 1, 2, 4, 6, 7, 9, 10, 11 |
| Medication arc | `medication_administrations.csv`, and the analgesia narrative in the ED and nursing notes |

Cross-modality links asserted:

- Every clinical number in a note is quoted from the tables — vitals, NEWS2, blood results, doses,
  the 12° residual angulation and 2 mm shortening. Verified for this generation: see section 7.
- Creatinine and eGFR cannot disagree, because eGFR is computed from creatinine, age and sex rather
  than sampled. An earlier draft sampled them independently and produced an eGFR of 53 alongside a
  normal creatinine; that was fixed before the final run.
- The median nerve paraesthesia present at 10:15 and 12:45, improving at 13:15 after reduction and
  normal from 16:10, appears in that order in the notes and nowhere out of order.
- Each note prompt contains only the events, observations, results and medicines timestamped at or
  before its own timestamp, so a note structurally cannot cite a later event. The post-reduction
  radiology result is gated separately to 13:40 (when the report was issued) rather than 12:48 (when
  the reduction happened).
- Metformin is marked withheld rather than given on the morning of surgery, because the state has
  the patient nil by mouth from 02:00. (Not exercised this run — metformin was not drawn.)

Fidelity deliberately traded for coherence:

- The vital-sign arc is a hand-written trajectory with small random jitter, not a physiological
  simulation. Real observation series are noisier and less monotonic. Chosen so the numbers track
  the pain and analgesia story exactly.
- Blood results are sampled independently within reference ranges, apart from eGFR. Real panels
  correlate (urea with creatinine, calcium with albumin). Accepted because no result drives the
  narrative.
- The clinical arc — reduction inadequate, therefore admit and fix — is fixed rather than sampled.
  With one patient there is no distribution to preserve, and a coherent story was worth more than a
  sampled outcome.

## 7. Evaluation — fidelity

Evaluated 2026-08-03 by the synthetic-data-evaluation skill. Seeding case is *from intelligence*
(section 4), so there is no reference distribution and levels 1 and 2 cannot run in their normal
form.

**Level 1 — univariate: not run.** There is no real comparator, and with n=1 patient there is no
distribution to compare. A single record has no mean, variance or category frequency. SynthGauge,
the sanctioned level 1–2 tool, was not installed: it compares a synthetic set against a real set,
and neither side of that comparison exists here. This is a structural limitation of a one-patient
dataset, not a deferred check.

**Level 2 — multivariate: replaced by cross-modal agreement, run.** The audit's substitute for a
missing reference distribution is agreement between modalities for the same patient
(`references/fidelity.md`, cross-modal table). Implemented as eight deterministic rules in
`scripts/clinical_rules.py` (R14–R21), covering the note ↔ labs, note ↔ observations, note ↔
timeline and label ↔ table pairs from that table. **All 8 passed** on the final generation:

- Every vital sign quoted in prose exists in `observations.csv` (R15), and every blood result quoted
  in prose matches `labs.csv` exactly (R16). No paraphrased or drifted number.
- No note cites a clock time later than its own timestamp (R17), and no note cites the post-reduction
  measurements before the 13:40 report that produced them (R18).
- No note attributes the fracture, cast or reduction to the uninjured side (R19). The uninjured hand
  is mentioned — it is the working hand — which the rule permits.
- Every timestamp in every file falls inside the encounter window (R14).
- Every note signature matches the author recorded against it (R20).
- All 26 derived labels agree with the tables they were derived from (R21).

**Level 3 — clinical plausibility: run, primary evidence.** Thirteen rules (R01–R13) in
`scripts/clinical_rules.py`, written in-house as `references/fidelity.md` requires. **All 13
passed:** physiological ranges, NEWS2 recomputed from the recorded vitals, systolic above diastolic,
eGFR consistent with creatinine under CKD-EPI 2021, abnormal flags matching the stated reference
ranges, no drug contraindicated by the recorded allergy, every regular medicine justified by a
recorded condition, paracetamol interval and 24-hour maximum, age-appropriate opioid dose, nothing
oral after nil-by-mouth, limb perfusion maintained in plaster with the compartment-syndrome label
agreeing, no backslab recorded before it was applied, and events in a possible order.

The checker was written before the final generation and found two real defects on the run before it:

1. **Oral paracetamol scheduled at 06:00, four hours after nil-by-mouth began at 02:00** (R10). A
   genuine clinical error. Fixed at source by changing that dose to the IV route, which is what
   would actually happen on the morning of surgery.
2. A false positive from R19 flagging "manages feeding with right hand" as a wrong-side reference.
   The rule was tightened to require an injury word near the side, not the rule's finding accepted.

An earlier draft also produced an eGFR of 53 alongside a normal creatinine; that was caught during
generation and fixed by computing eGFR rather than sampling it (section 6).

**What these results do and do not show.** 21/21 rules passing says the record is internally
consistent and free of the specific errors encoded — it does not say the record resembles a real
one. The rules were written by the same agent that generated the data, so they test the coherence
the generator was trying to achieve, and cannot find a category of error nobody thought of. The
strongest available validation, per `references/fidelity.md`, is clinician review of the notes; that
has **not** been done.

## 8. Evaluation — utility

**TSTR did not run.** There is no real holdout to test on — no real data was used or is available
(section 4). Train-on-synthetic/test-on-real is structurally impossible for this dataset, and no
substitute reproduces it.

**TSTS did not run either.** The skill's substitute for TSTR is train-on-synthetic/test-on-synthetic,
to show that the encoded signal is learnable. With one patient there is no train/test split and
nothing to learn. `scripts/tstr.py` was not built; it would have nothing to operate on.

**Substitute run: extraction smoke test** (`scripts/extraction_smoke_test.py`). The intended PoC task
is reading facts out of the notes, so a model was given the 11 notes with no structured data and
asked for 15 fields, compared against `labels.csv` — which was written before the notes existed.
Result: **15/15 semantically correct; 11/15 exact string matches.** The four non-matches are all
verbosity, not error (e.g. ground truth "Left distal radius", extracted "left distal radius with
associated left ulnar styloid avulsion"; ground truth "Minimal, dorsal cortex only", extracted
"minimal dorsal cortical comminution"). Numeric fields — peak pain 8, max NEWS2 1 — were exact.

This is a smoke test and is reported as one. It establishes that the labelled facts are present and
readable in the prose, and that a note-reading PoC will have something to find. It is not evidence of
utility, for two compounding reasons: the notes were written by an LLM from an explicit fact list, so
the facts are well-formed and uncontradicted in a way real notes are not; and the same model
(`gpt-5-1`) both wrote the notes and did the extraction, because it is the only model reachable from
this environment (see section 9). That is the label-validity trap in its clearest form.

**Downstream utility is unproven.** A model that performs well on this dataset has not been shown to
perform on real clinical notes.

## 9. Evaluation — privacy and disclosure

**No real data informed generation.** Verified by construction, not by assertion: the patient state
is sampled in code from the section 3 distributions, the prompts are built by `facts_block()` from
that state alone, and no real record, dataset or document was read into any prompt. Per
`references/privacy.md` the seed-free case carries lower risk, not zero.

**Checks run:**

- **Direct identifier inventory (deterministic).** Every identifier in the dataset is synthetic by
  construction: the NHS number is in the 999 test range reserved for synthetic data and carries a
  valid mod-11 check digit; name, address and postcode come from Faker's `en_GB` provider; hospital,
  ward and GP practice names are invented; the 10 clinician names are a fixed fictional list in the
  generation script.
- **Free-text identifier scan** (`scripts/text_identifier_scan.py`, deterministic). Across all 11
  notes: **no** NHS-number-like string, **no** postcode, **no** phone number, **no** email address,
  **no** MRN-style identifier. Eight date-like matches, all of which are the encounter dates
  (17/02/2026, 18/02/2026), not a date of birth. Personal names appearing: the patient's, three
  times, and each clinician's in their own signature — all accounted for in `patient.csv` and the
  author list. No identifier appears in the prose that the structured record does not already hold.
- **Exact-match and membership inference: not applicable.** Both structurally require the real
  dataset the synthetic data was derived from. There is none. Not run, and not deferred — there is
  nothing for them to test.

**Checks not run:**

- **Free-text leakage scoring (PrivFingerprint pattern): not run.** The pattern's second stage
  requires entity extraction by a model *different* from the one that wrote the text, because a model
  under-reports identifying detail in its own output. Six alternative model IDs were probed against
  the Foundry endpoint (`gpt-4o`, `gpt-4-1`, `gpt-5-mini`, `claude-sonnet-4`, `gemini-2-5-pro`, `o3`)
  and all returned 404; the model list endpoint also returns 404. Only `gpt-5-1` — the generating
  model — is reachable, so the check cannot be run validly from this environment. The deterministic
  scan above is a narrower substitute: it finds patterned identifiers, but it does not score how
  identifying the *combination* of narrative details is, which is the risk PrivFingerprint exists to
  measure. The third stage (uniqueness scoring via pyCorrectMatch) requires Julia and was not
  attempted.
- **Memorisation of training content: not established.** Whether the generating model reproduced
  memorised text from its training data cannot be tested from here — it needs a second model, or
  access to the training corpus. A manual read of all 11 notes found nothing that reads as recalled
  from a specific source, which is weak evidence and is not a check.
- **TAPAS adversarial audit: not run.** Its attacks need the real data the synthetic set was derived
  from, so it does not apply to a seed-free dataset (`references/privacy.md`, TAPAS caveats).
- **Chance collision with a real person: not established.** The record is a common name with a
  Faker-generated address in a real-format UK postcode; whether that combination matches a living
  person cannot be checked offline, and checking it would require a real population register.

**Fidelity read against privacy (Rule 2).** The usual tension does not arise here. The
synthetic-vs-real discriminator has nothing to discriminate against, and the coherence reported in
section 7 is internal consistency with a state object, not proximity to any real record. No
generator was fitted to real data, so there is no memorisation-through-fitting pathway. The residual
privacy risk in this dataset sits in the language model's weights, not in the sampled tables — and
that is exactly the pathway that could not be tested.

**Conclusion: not established.**

Not "safe to share", because the free-text leakage assessment — the check that matters most for a
text dataset, and the one `references/clinical-text.md` calls mandatory before text leaves the
environment — could not be run validly. The dataset is one invented patient with synthetic
identifiers throughout, and the deterministic evidence is clean, so the expected risk is low. But
low expected risk established by the narrower of two available checks is not the same as established
safety.

To establish it, one of:

1. Access to a second model on the Foundry endpoint, then run the PrivFingerprint-pattern extraction
   and uniqueness scoring with that model, recording both model IDs.
2. A human reviewer reading the 11 notes for anything that reads as recalled rather than generated.
3. A decision from the user that a one-patient, wholly-invented record with 999-range identifiers
   does not require a leakage assessment before leaving the environment — which is a governance call,
   not a technical one, and is theirs to make.

## 10. Limitations

- **One patient.** No distribution, no prevalence, no variance. Nothing statistical can be said with
  this dataset, and levels 1 and 2 of fidelity cannot run in their normal form.
- **From intelligence, so fidelity to any real population is asserted and not measured.** This is a
  recorded gap in the generation skill (`references/from-intelligence.md`), not an oversight here.
  Every number in the cohort definition is marked "assumed" except the eGFR equation and the
  reference intervals.
- **Downstream utility is unproven.** TSTR is impossible; the extraction smoke test is not a
  substitute for it.
- **The label-validity trap is mitigated but not escaped.** Labels are code-derived and fixed before
  any text existed, so extraction accuracy is a fair measure of note-reading. But the notes are LLM
  prose written from a clean fact list, and only one model is reachable, so both generation and any
  LLM-based evaluation share a model. Treat strong results on this data as artefacts until shown
  otherwise on real notes.
- **No clinician has reviewed it.** With no real comparator this is the strongest validation
  available and it has not happened. The clinical arc, the vital-sign magnitudes, the drug choices
  and the note register are all plausible to a non-clinician and unverified by one.
- **Free-text leakage assessment could not be run validly** — see section 9. Verdict is "not
  established".
- **The rules that pass were written by the same agent that generated the data.** They encode the
  coherence the generator aimed at, so they cannot detect a class of error that was not anticipated.
  An independent reviewer is worth more than another rule.
- **Notes are LLM-clean.** Five misspellings were injected in total, across three of the four
  nursing and triage notes (SCN augmentation pattern; NOTE-007 two, NOTE-009 one, NOTE-010 two, and
  NOTE-001 none because no word from the fixed eight-word list appeared in it — the
  `typo_edits_applied` column records this per note). That is a token gesture at messiness: real
  records also contain contradictions between authors,
  copy-forward, missing entries, dictation errors and non-native phrasing. None of that is present.
  A model trained on this text will not have met the messiness of a real record.
- **Physiology is scripted, not simulated.** The vital-sign trajectory is a hand-written arc with
  jitter. No waveform, signal or imaging data exists for this patient — imaging in particular is
  explicitly unsupported by the generation skill, and the two radiology reports here are text
  describing radiographs that do not exist.
- **Only day 1.** The record ends at 09:00 on 18/02/2026, before the operation it spends all day
  planning. Anything needing an outcome, a length of stay or a follow-up is not in this dataset.
- **The 999-range NHS number is valid in format.** It is designed for synthetic use, but any system
  ingesting this data should be confirmed to treat the 999 range as test data.
