# patients — synthetic dataset report

## 1. Summary

A demographics-only table of 10 synthetic patients: `patient_id`, `name`, `address`,
`date_of_birth`. One modality (tabular), one file, `data/patients.csv`. No clinical content —
no conditions, medications, encounters or observations. Built as scaffolding for a PoC that
needs patient identity fields to exist, not as a clinical cohort.

Generated: 2026-07-29. Generator: synthetic-data-generation skill.
Reproduce with `scripts/generate_patients.py`.

## 2. Intended use

Scaffolding and UI/plumbing demos: something to populate a patient list, test an ingest path,
or render a record header. It is the spine other modalities would hang off if this dataset is
extended.

Not to be used for: anything clinical, any statistical or demographic claim, any model training
or evaluation, or as evidence about a real population. It carries no clinical fields at all,
and its demographic structure is asserted rather than fitted (see section 3).

## 3. Cohort definition

| Parameter | Value | Source |
| --- | --- | --- |
| Cohort size | 10 patients | User request |
| Age structure | One patient per band: 0–4, 5–14, 15–24, 25–34, 35–44, 45–54, 55–64, 65–74, 75–84, 85–95. Age uniform within band; realised ages 3, 14, 15, 32, 39, 49, 64, 69, 78, 88 | Assumed — stratified to force spread across the range, not to match any population pyramid |
| Sex structure | Binary female/male, drawn per patient at 50/50; realised split not controlled | Assumed, no source. Sex is sampled in the patient state to pick a name but is **not** an output column |
| Name origin mix | en_GB ×4, en_IN, bn_BD, pl_PL, en_NG, it_IT, ar_AA ×1 each | Assumed, no source. Chosen to give visible variety; the weights are invented and do not reflect any published UK ethnicity or surname distribution |
| Addresses | Faker `en_GB` locale for all 10 | Assumed — every patient is treated as UK-resident |
| Conditions and prevalence | None — not in scope | n/a |
| Comorbidities | None — not in scope | n/a |
| Severity mix | None — not in scope | n/a |
| Timeline span | No timeline. Ages computed against a fixed reference date of 2026-07-29 | Generation date |

## 4. Provenance

Seeding case: **from intelligence** — no real seed data was read, fitted to, or consulted. Per
`references/from-intelligence.md`, this is a recorded gap in the skill: the output is plausible,
and its fidelity to any real population is asserted, not measured.

| Modality | Files | Tool | Version | Seed | Key parameters |
| --- | --- | --- | --- | --- | --- |
| Tabular (demographics) | `data/patients.csv` | Faker | 40.36.0 | Master seed 20260729; per-patient seed = 20260729 + row index, applied to both the RNG and each Faker instance | Reference date 2026-07-29; age bands and locale mix as in section 3; `first_name_*` + `last_name` rather than `name()` |

No real seed data was used, so no permission question and no holdout exclusion applies.

Faker was chosen per `references/tabular.md`: it is the sanctioned tool for scaffolding names,
addresses and dates, pure-Python and pip-installable, so it clears the environment gate. It was
installed and run in `.venv/` — this dataset was actually generated, not described.

One correction made during generation: Faker's `name()` prefixes titles, which produced
"Dr Tom Jones" aged 3 and "Mr Scott Wilkinson" aged 14. This is the documented Faker limitation
(no inter-field logic) and was fixed by composing first + last name directly.

## 5. Labels

**There are no labels.** No field in this dataset is a target variable, and nothing here was
derived by an LLM. Every value is either sampled by a seeded `random.Random` or drawn from Faker.

The label-validity trap therefore does not apply to this dataset as it stands. It would apply
the moment clinical content is added: any label must be fixed in the patient state before the
content expressing it is generated.

## 6. Coherence

The patient state (`patient_state()` in `scripts/generate_patients.py`) fixes, per patient:
`patient_id`, `sex`, `date_of_birth` and the name locale. It is seeded deterministically from
the patient index, so any modality added later can be regenerated from the same state and stay
consistent with these rows.

Fields the state fixes and downstream modalities must respect: date of birth (hence age at any
encounter), sex, and patient identity.

Cross-modality links asserted: none — this is a single-modality dataset.

Fidelity traded for coherence: none yet, no trade arose. Two fidelity limitations were accepted
for other reasons, both recorded in section 10.

## 7. Evaluation — fidelity

Tool used: none. SynthGauge and synthcity both compare a synthetic set against a real reference
distribution; there is no real comparator here, so neither was applicable. The checks below were
run as a one-off script against `data/patients.csv` and are reported per level.

**Level 1 — univariate: did not run as a metric.** Requires a reference distribution. There is
none, and n=10 would not support a distributional comparison even if one existed. A second
evaluation pass did however find two implausibilities catchable from domain knowledge alone,
without a comparator — recorded under "Findings" below.

### Findings — second pass

**F1. Dwelling type is implausibly skewed. 7 of 10 addresses begin "Studio".** Faker's `en_GB`
address provider oversamples the studio/flat form; in a real UK population sample of ten, a
plain house number is the dominant form and seven studios would not occur. This is a univariate
implausibility in the address field, visible without any reference distribution. It is cosmetic
for scaffolding use but would be conspicuous in a demo, and it is exactly the kind of artefact
Faker's lack of inter-field logic produces. Remedy: compose the address from Faker's building
number, street, city and postcode components rather than calling `address()`, or reject-sample
the studio form down to a realistic rate. Not applied — the fix changes generator behaviour and
is the user's call.

**F2. Postcode areas bear no relation to the town names.** The postcode area letters and the town
names are drawn independently, so every row is internally incoherent as a location: "West
Peterborough, S14 7TD" places a Peterborough-named town in the Sheffield postcode area, "North
Dawn, B04 9AH" in Birmingham, "Staceytown, IM8Y 9GD" on the Isle of Man. Five of ten invented town
names also embed a real word or place fragment ("Peterborough", "Leonard", "Hugh", "Hazel",
"Dawn"), which makes the mismatch more noticeable than fully invented names would.

This is the address-field instance of the same root cause as F1 and as the age-vs-title problem
in section 4: Faker guarantees nothing across fields. It has no privacy consequence — see
section 9, where the invented, non-resolving addresses are the reason disclosure risk is low —
but any PoC that geocodes, maps, or routes on these addresses will produce nonsense. Remedy:
pick a real postcode area per patient and fix the town to match, which means adding a lookup
Faker does not provide. Not applied.

Neither finding was handed back to the generation skill, because neither is a defect in what was
asked for: both are documented Faker limitations, and the dataset was specified as scaffolding.
They are recorded here so a reader does not mistake the address field for usable geography.

**Level 2 — multivariate: did not run.** Same reason. Cross-modal coherence is not measurable
either — this is a single-modality dataset, so there is nothing to check agreement against.

**Level 3 — clinical plausibility: not applicable.** The dataset contains no clinical fields.
There are no conditions, medications, labs or encounters, so there is no domain logic to violate
and no rules layer to write. This is the one place the skill expects the primary evidence to sit
when there is no real comparator, and here it is empty — which is a statement about how little
this dataset asserts, not a pass.

**Internal consistency against the cohort definition (section 3): passed, all checks.**

| Check | Result |
| --- | --- |
| Row count = 10 | Pass |
| Columns as specified | Pass — `patient_id`, `name`, `address`, `date_of_birth` |
| No empty cells | Pass — 0 of 40 |
| `patient_id` unique | Pass — 10 distinct |
| Names unique | Pass — 10 distinct, no near-duplicates by inspection |
| Addresses unique | Pass — 10 distinct |
| Age falls in its declared band | Pass — 3, 14, 15, 32, 39, 49, 64, 69, 78, 88 against the ten bands in section 3 |
| All dates of birth in the past | Pass |
| Addresses end in a UK-format postcode | Pass — 10 of 10 match the UK postcode pattern (format only; see section 10 — these are not valid postcodes) |
| Regeneration is deterministic | Pass — re-running `scripts/generate_patients.py` reproduces the file byte-for-byte (SHA-256 `db9a66b09475a5f9…`) |

No published distributions were supplied for comparison, so none was used.

Fidelity result must be read beside section 9: this dataset is unfaithful to any real population
by construction, which is also why its disclosure risk is low. The two are the same fact.

## 8. Evaluation — utility

**TSTR did not run.** It is impossible here: train-on-synthetic/test-on-real requires a real
holdout, and this is the from-intelligence seeding case with no real data at all. There is also
no label and no prediction task in a demographics-only table, so there would be nothing to train
even if a holdout existed.

**Discriminator AUC did not run**, for the same reason — it requires real records to discriminate
against.

**Downstream utility is unproven.** No check performed here provides evidence that a model
trained or demonstrated on this data would behave as it would on real data.

The label-validity trap does not apply: per section 5, there are no labels, and no LLM produced
any value in this dataset.

Clinician review is the strongest validation available when there is no real comparator. For this
dataset it would add little — there is no clinical content to review. It becomes necessary as soon
as clinical fields are added.

## 9. Evaluation — privacy and disclosure

The three checks the skill specifies for the no-real-seed-data case:

1. **Did any real record inform generation, including via a prompt?** No. Every value is produced
   by Faker or a seeded `random.Random` from the parameters in section 3. No real dataset was read,
   fitted to, or pasted into a prompt, and no LLM was involved in generating any field. The dataset
   is seed-free, so the full audit does not apply.
2. **Does LLM-generated free text surface memorised training content?** Not applicable — the
   dataset contains no free text and no LLM-generated content.
3. **Could invented records collide with a real person by chance?** Low but not zero, and it is the
   only residual risk worth naming. The names are common Faker forenames and surnames, and a
   name–DoB pair could coincide with a real person. The addresses cannot: they are invented town
   names with format-shaped, non-valid postcodes (section 10), so no row points at a real
   household. A collision would be coincidental and unverifiable rather than disclosive — nothing
   real was encoded to be recovered.

Checks that did not run, and why: exact-match and nearest-neighbour distance, membership inference,
attribute inference, and TAPAS adversarial auditing all require the real data the synthetic set was
derived from. There is none, so these are structurally inapplicable, not skipped. No real patient
data was loaded to run any check. PrivFingerprint's free-text scoring is not applicable — no text.

Note the general caveat from `references/privacy.md`: most of the strongest privacy tooling is
inspiration-only, so the runnable set is thinner than the asset list suggests. That did not bind
here, since nothing needed to run.

**Conclusion: safe to share.** This is a demographics-only table with no real-data provenance, no
clinical content and no free text — there is no real individual whose information could be
disclosed by it. The judgement rests on provenance, which is fully documented in section 4, rather
than on a privacy metric, and it holds only for this file as it stands: adding clinical fields, free
text, or any real seed data invalidates it and requires a fresh audit.

## 10. Limitations

- **Fidelity to any real population is unmeasured.** The from-intelligence seeding case means
  there is no comparator. Every number in section 3 is assumed; none is drawn from a published
  statistic. Do not read the age or name-origin mix as representative of anything.
- **Ten rows.** No distributional claim is meaningful at n=10, in either direction.
- **Faker supplies no inter-field logic.** Names, addresses and dates are drawn independently.
  Nothing in the tool enforces plausibility across fields — the age-vs-title problem in
  section 4 is the visible instance; others may remain.
- **Addresses are not real UK addresses and are not usable as geography.** Faker's `en_GB`
  provider composes plausible-looking street, town and postcode strings; the town names ("Port
  Denisechester", "West Vanessaview") are invented and the postcodes are format-shaped rather
  than real — at least one, `B04 9AH`, is not even structurally valid, as UK districts do not
  take a leading zero. No postcode database was consulted, so "not valid" is asserted from the
  format and from the invented town names, not verified against a register. The address field
  additionally carries findings F1 (7 of 10 are "Studio") and F2 (postcode area unrelated to
  town) in section 7. That the addresses do not resolve is a safety property, not a defect, but
  anything that geocodes, maps or validates them will fail.
- **Two names are in non-Latin script** (Bengali, Arabic). Realistic for a UK patient population
  in principle, but many patient administration systems store transliterated Latin-script names,
  and mixed scripts may break downstream tooling. Flag for the user; transliterating is a
  one-line change to the locale list.
- **Sex is sampled but not emitted.** The column was omitted because it was not requested. It
  exists in the patient state and can be added without regenerating anything else.
- **No clinical content whatsoever.** This is not a clinical cohort and cannot support any
  clinical PoC on its own.
- **Downstream utility is unproven**, in those words. TSTR could not run and no substitute
  evidence of utility exists (section 8).
- **Fidelity levels 1 and 2 never ran** and no fidelity metric was computed. The "passed" results
  in section 7 are internal-consistency checks — the data agrees with the specification it was
  generated from, which is a weaker claim than resembling real data.
- **The safe-to-share conclusion is scoped to this file as it stands.** It rests on provenance,
  not on a privacy metric. Adding clinical fields, free text, or any real seed data invalidates it.
