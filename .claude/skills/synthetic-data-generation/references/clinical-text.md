# Clinical text

## Applies to

Clinical notes, discharge summaries, referral and clinic letters, consultation write-ups,
semi-structured text. For spoken dialogue or audio, use `audio-speech.md`.

Clarify two axes with the user before starting: semi-structured vs unstructured, and
computer-written vs handwritten. The second determines whether the request is supported at all.

## Tools

| Asset | Use for | Verdict | Constraints |
| --- | --- | --- | --- |
| SCN (`nhsengland/synthetic_clinical_notes`) | LLM pipeline generating patient pathways with matching clinical notes | Runnable — see entry below | MIT, Python 3.12, needs an LLM API. Audit also records it as easy to set up on FDP |
| NoteChat pattern (arXiv `arxiv.org/abs/2310.15959`, ACL Anthology) | Cooperative doctor/patient LLM agents conditioned on clinical notes | Inspiration | Not a library — an architecture implemented with your own agent framework |
| Faker / Mimesis | Identifiers, names, addresses and dates inside letter templates | Use | No clinical content; see `tabular.md` |
| MIMIC-IV v3.1 | Comparator for note style, structure and length | Reference only | Real patient data — not a generation input, and not to be pasted into a prompt, without permission and governance confirmation |

SCN and NoteChat share the property that matters: text is conditioned on a structured patient
state or an existing note, not generated free-standing. Notes written independently of the labs
and diagnoses they describe are the standard way a synthetic patient becomes incoherent.

## Inspiration entries

Read the source before reimplementing. Entries written from the sources on 2026-07-29. If a task
needs detail these do not cover, ask the user or fetch the URL — but the target environment may
have no outbound network, so do not make a fetch a dependency.

### SCN — synthetic clinical notes

`github.com/nhsengland/synthetic_clinical_notes` — MIT, Python 3.12, actively maintained by the
NHS England Data Science team. Full entry in `healthcare-ehr.md`; the note-specific points:

- **Pattern:** one note per journey stage, generated after the stage exists, then augmented with
  typos and medical abbreviations.
- **Copy:** the augmentation stage. Real notes contain errors, shorthand and inconsistency; clean
  LLM prose is a recognisable tell and trains models on the wrong distribution. This is the only
  asset in the audit that addresses it.
- **Substitute:** the LLM, via `call_llm` in `src/processing.py`. Prompts, document templates and
  schemas are separated into `src/prompts.py`, `src/doc_templates.py` and `src/schemas.py` — copy
  that separation, since note realism lives in the templates rather than the model.
- **Don't inherit:** Palantir Foundry assumptions, confined to `call_llm` and `read_write_data`.
- **Caveats:** an LLM generates both the journey and the note, so any downstream label must be
  derived from the structured state independently. Augmentation must not corrupt clinically
  meaningful content — a typo in a drug dose is a data error, not realism.

### NoteChat

arXiv `arxiv.org/abs/2310.15959`, ACL Anthology. A dataset and a method, not a library.

- **Pattern:** an ensemble of role-specific LLM agents (doctor, patient) using structured
  role-play and strategic prompting, generating dialogue conditioned on a clinical note.
- **Copy:** role-specific agents outperform a single model asked to write both sides. The
  conditioning direction — note first, dialogue derived from it — is the transferable idea, and it
  inverts cleanly: generate the structured record, then derive the conversation.
- **Substitute:** the models, and the roles themselves (nurse, carer, interpreter).
- **Don't inherit:** nothing to install.
- **Caveats:** evaluated on the MTS-dialogue benchmark against ChatGPT and GPT-4, with reported
  improvements up to 22.78% for models trained on NoteChat dialogues — those are claims about
  their data, not a guarantee for ours. Architecture detail and pipeline stages are in the PDF
  only; fetch it if the implementation depends on specifics. Their direction is note → dialogue;
  using dialogue → note for a PoC that summarises consultations means the note is LLM-derived and
  cannot serve as ground truth.

## Gaps

- **Handwritten and scanned letters.** An explicit gap; no tool has been assessed for it. If a PoC needs scanned correspondence or image-of-text, state that it is not
  supported and confirm the approach with the user.
- No tool in the audit generates clinical text without an LLM, which makes the label-validity trap
  the dominant risk for this modality.
- Atypical written language (dictation errors, abbreviation-heavy notes, non-native phrasing) is
  not addressed by any assessed asset.

## Label-validity trap

Highest risk modality. If an LLM writes the note and assigns the diagnosis, acuity or outcome the
PoC extracts or predicts, the demo may only show that an LLM can read its own output.

- Derive the label from the structured patient state, then generate prose expressing it.
- For information-extraction PoCs, keep extraction targets as structured fields written before the
  text exists; the note is a rendering of them.
- Validate against real holdout text where it exists and is permitted.

See `from-intelligence.md`.

## Privacy

Free text leaks differently from tables: an unusual combination of narrative details can
re-identify someone when every field looks generic. The audit's tooling is PrivFingerprint
(`nhsengland/privfp-experiments`, scores privacy risk of free-text data) and PrivacyLeakage
(`nhsengland/priv-lm-health-extended`). PrivFingerprint required WSL because of Julia and OpenJDK;
both are inspiration-only.

Do not run either against real data unprompted. Route free-text leakage through
`synthetic-data-evaluation`, `references/privacy.md`.

## Coherence

Prose can assert anything, so constrain it:

- Generate from the patient state (`healthcare-ehr.md`), passing the state into the prompt.
- Every clinical fact in the note must exist in the structured data. If the note states a value, it
  is the value in the labs table.
- Respect the timeline: a note cannot reference later events.
- Keep author, department and letter format consistent across a patient's correspondence.

## Report

Contributes to report sections 4 (model and prompt strategy used), 5 (label derivation — critical
here) and 6 (which structured fields constrained the text).

## Evaluation

Note-versus-structured-data agreement and clinical plausibility — `synthetic-data-evaluation`,
`references/fidelity.md`. Free-text leakage — `references/privacy.md`, mandatory before any text
dataset leaves the environment.
