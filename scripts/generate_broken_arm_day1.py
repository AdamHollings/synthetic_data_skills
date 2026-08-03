"""Generate the broken-arm day-1 dataset: structured tables (code) + clinical notes (LLM).

Order matters and is enforced here: the patient state is sampled, the structured
tables are built, the labels are derived, and only then is any prose generated.
Each note is prompted with the subset of the state that exists at its own
timestamp, so a note cannot reference a later event.

Run:  .venv/Scripts/python.exe scripts/generate_broken_arm_day1.py
"""

import asyncio
import csv
import random
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import call_llm as llm_module
from broken_arm_day1_state import (
    SEED,
    build_events,
    build_labs,
    build_limb_observations,
    build_medications,
    build_observations,
    build_state,
    derive_labels,
    _t,
)
from call_llm import call_llm_async

MODEL = "ri.language-model-service..language-model.gpt-5-1"
TEMP = 0.4
CONCURRENCY = 4
OUT_DIR = Path(__file__).parent.parent / "data" / "broken_arm_day1"

# (note_id, datetime, note_type, author_role, specialty, location, what the note must cover, author name)
# Author names are fixed here so the same person signs consistently and two roles never share a surname.
NOTE_SLOTS = [
    ("NOTE-001", _t(10, 11), "ED triage note", "Band 6 ED nurse", "Emergency Medicine", "ED Majors",
     "Brief triage entry: mechanism, presenting complaint, first observations, pain score, triage category, "
     "temporary splint and analgesia requested. Very short.",
     "S. Okafor"),
    ("NOTE-002", _t(10, 48), "ED clerking", "ED SHO", "Emergency Medicine", "ED Majors",
     "Full clerking: presenting complaint, history of presenting complaint, past medical history, drug history, "
     "allergies, social history, examination (including neurovascular findings of the injured limb and a clear "
     "statement that there was no head injury or loss of consciousness), impression and plan including X-ray and bloods.",
     "Dr M. Whitfield"),
    ("NOTE-003", _t(11, 52), "Radiology report", "Consultant radiologist", "Radiology", "Radiology",
     "Formal report on AP and lateral radiographs of the injured wrist taken before reduction. Clinical details, "
     "findings (dorsal displacement and angulation, ulnar styloid, no intra-articular extension, no other fracture), "
     "conclusion. Radiology house style, no plan.",
     "Dr J. Harcourt"),
    ("NOTE-004", _t(12, 55), "Procedure note — closed reduction", "ED registrar", "Emergency Medicine", "ED Majors",
     "Procedure note for haematoma block and closed manipulation: consent, block details and dose, technique, "
     "cast applied, immediate post-procedure neurovascular check, complications, and that a check film was requested.",
     "Dr A. Rennick"),
    ("NOTE-005", _t(13, 40), "Radiology report", "Consultant radiologist", "Radiology", "Radiology",
     "Formal report on post-reduction check radiographs in plaster. Comparison with the earlier study, residual "
     "deformity quantified, cast position. Conclusion only, no management plan.",
     "Dr J. Harcourt"),
    ("NOTE-006", _t(14, 20), "Orthopaedic review", "T&O registrar", "Trauma & Orthopaedics", "ED Majors",
     "Specialty review: summary of injury and what has been done, examination now, review of the check film, "
     "decision to admit, reasoning for surgical fixation rather than cast management, consent discussion in outline, "
     "and the plan including NBM timing and VTE prophylaxis.",
     "Dr P. Lindqvist"),
    ("NOTE-007", _t(16, 5), "Nursing admission assessment", "Staff nurse", "Trauma & Orthopaedics", "Ward 12",
     "Ward admission assessment: arrival on ward, orientation, observations, pain, limb observations and elevation, "
     "risk assessments (falls, pressure area, VTE, nutrition), mobility and social circumstances, personal care needs "
     "with the injured arm, next of kin informed.",
     "L. Brennan"),
    ("NOTE-008", _t(18, 30), "Pre-operative anaesthetic assessment", "Anaesthetic registrar", "Anaesthetics", "Ward 12",
     "Pre-op assessment: past medical history, drug history and allergies, airway and dental assessment, "
     "exercise tolerance, previous anaesthetics, relevant blood results, ASA grade, planned anaesthetic technique "
     "(general anaesthetic with regional block), fasting instructions.",
     "Dr N. Achebe"),
    ("NOTE-009", _t(21, 40), "Nursing progress note", "Staff nurse", "Trauma & Orthopaedics", "Ward 12",
     "Short evening entry: how the patient is, pain and what analgesia was given, limb observations, arm elevated, "
     "oral intake, mobility on the ward, mood and any concerns raised about the operation.",
     "D. Marsden"),
    ("NOTE-010", _t(2, 30, 1), "Night nursing note", "Staff nurse (night)", "Trauma & Orthopaedics", "Ward 12",
     "Very short night entry: sleep, the episode of pain and PRN analgesia, limb observation check, NBM commenced, "
     "observations stable.",
     "K. Tiernan"),
    ("NOTE-011", _t(8, 15, 1), "Consultant ward round", "Consultant orthopaedic surgeon", "Trauma & Orthopaedics", "Ward 12",
     "Ward round entry: overnight summary, examination, confirmation of the operative plan and listing for the "
     "afternoon trauma list, consent confirmed, bone health follow-up (DEXA / fracture liaison), and the plan for the day.",
     "Mr R. Ellery"),
]

# SCN pattern: real notes carry shorthand and typos. Applied only to nursing prose, only to
# these non-clinical words, never to numbers, drugs, doses or findings.
TYPOS = {
    "patient": "patinet",
    "reviewed": "reviwed",
    "comfortable": "comfortble",
    "reports": "reprots",
    "settled": "setled",
    "informed": "infomred",
    "assessment": "assesment",
    "observations": "observtions",
}


def augment(text, rng, max_edits=2):
    """Introduce at most `max_edits` misspellings of non-clinical words."""
    edits = 0
    for word, typo in rng.sample(list(TYPOS.items()), len(TYPOS)):
        if edits >= max_edits:
            break
        pattern = re.compile(rf"\b{word}\b")
        if pattern.search(text):
            text = pattern.sub(typo, text, count=1)
            edits += 1
    return text, edits


def facts_block(s, events, observations, limb_obs, labs, meds, cutoff):
    """Everything true at `cutoff`, and nothing after it."""
    def before(rows, key):
        return [r for r in rows if datetime.fromisoformat(r[key]) <= cutoff]

    lines = [
        "PATIENT (all synthetic):",
        f"  Name: {s['name']}   NHS number: {s['nhs_number']} (synthetic 999 test range)",
        f"  DOB: {s['date_of_birth']}   Age: {s['age']}   Sex: {s['sex']}",
        f"  Address: {s['address']}, {s['postcode']}   GP: {s['gp_practice']}",
        f"  Hospital: {s['hospital']}   Ward if admitted: {s['ward']}, bed 6",
        f"  Patient ID: {s['patient_id']}   Encounter ID: {s['encounter_id']}",
        f"  Weight {s['weight_kg']} kg, height {s['height_cm']} cm",
        f"  Past medical history: {', '.join(s['conditions']) if s['conditions'] else 'Nil of note'}",
        f"  Regular medicines: {', '.join(f'{m[0]} {m[1]} {m[2]} {m[3]}' for m in s['regular_meds']) or 'None'}",
        f"  Allergies: {s['allergy']}",
        f"  Social: {s['lives_with']}. {s['mobility']}. {s['smoker']}. Alcohol {s['alcohol_units']} units/week.",
        f"  Dominant hand: {s['dominant_hand']}",
        "",
        "INJURY:",
        f"  Mechanism: {s['mechanism']} at {s['fall_time']:%H:%M} on {s['fall_time']:%d/%m/%Y}",
        f"  Arrived ED {s['arrival_time']:%H:%M}. {s['arrival_mode']}.",
        f"  Diagnosis: {s['diagnosis']}, with ulnar styloid avulsion.",
        f"  Radiographic features (the only ones present — do not add others): {s['radiographic_features']}.",
        "  Closed injury. No head injury, no loss of consciousness, no other injury.",
        "  At presentation: paraesthesia in the median nerve distribution (thumb, index, middle finger),",
        "  radial pulse present, fingers warm and pink, capillary refill under 2 seconds.",
        "",
        "EVENTS SO FAR:",
    ]
    for ts, kind, loc, desc in events:
        if ts <= cutoff:
            lines.append(f"  {ts:%d/%m %H:%M}  {kind} ({loc}) — {desc}")

    lines.append("")
    lines.append("OBSERVATIONS SO FAR (use these exact numbers if you quote any):")
    for o in before(observations, "observation_datetime"):
        lines.append(
            f"  {o['observation_datetime'][5:16]}  RR {o['respiratory_rate_per_min']}, SpO2 {o['spo2_percent']}% on air, "
            f"BP {o['systolic_bp_mmhg']}/{o['diastolic_bp_mmhg']}, HR {o['pulse_bpm']}, temp {o['temperature_c']}C, "
            f"{o['consciousness_acvpu']}, pain {o['pain_score_0_10']}/10, NEWS2 {o['news2_total']} — {o['context']}"
        )

    lines.append("")
    lines.append("LIMB OBSERVATIONS SO FAR:")
    for lo in before(limb_obs, "observation_datetime"):
        lines.append(
            f"  {lo['observation_datetime'][5:16]}  {lo['limb']} in {lo['immobilisation'].lower()}: colour {lo['colour'].lower()}, "
            f"CRT {lo['capillary_refill_seconds']}s, radial pulse {lo['radial_pulse'].lower()}, sensation: {lo['sensation'].lower()}, "
            f"swelling {lo['swelling'].lower()}, movement: {lo['active_movement'].lower()}, elevated: {lo['elevated'].lower()}"
        )

    reported = before(labs, "reported_datetime")
    if reported:
        lines.append("")
        lines.append("BLOOD RESULTS AVAILABLE (exact values):")
        for r in reported:
            unit = f" {r['unit']}" if r["unit"] else ""
            lines.append(f"  {r['test_name']}: {r['value']}{unit} (ref {r['reference_range'] or 'n/a'}) [{r['abnormal_flag']}]")

    given = before(meds, "administration_datetime")
    if given:
        lines.append("")
        lines.append("MEDICINES GIVEN SO FAR:")
        for m in given:
            lines.append(
                f"  {m['administration_datetime'][5:16]}  {m['medication']} {m['dose']} {m['route']} — "
                f"{m['indication']} [{m['status']}]"
            )

    if cutoff >= s["reduction_time"]:
        lines += ["", "REDUCTION:", f"  {s['reduction_method']}."]
        if cutoff >= _t(13, 40):  # check film not reported until 13:40
            lines.append(
                f"  Post-reduction imaging: {s['post_reduction_result']}. Cast position satisfactory, no cast complications."
            )
        else:
            lines.append("  Check radiographs requested. NOT YET TAKEN OR REPORTED — their result is unknown to you.")
    if cutoff >= _t(14, 20):
        lines += [
            "",
            "DECISION AND PLAN (agreed at 14:20 by T&O):",
            f"  {s['plan']}.",
            f"  Planned operation: {s['planned_operation']} on {s['planned_operation_date']}.",
        ]
    return "\n".join(lines)


def build_prompt(s, slot, facts):
    note_id, ts, note_type, author, specialty, location, cover, author_name = slot
    return f"""You are writing one entry in a UK NHS hospital record. Everything below is synthetic test data for a proof-of-concept; no real person is involved.

Write the note text ONLY. No preamble, no markdown code fences, no commentary.

NOTE TO WRITE
  Type: {note_type}
  Written at: {ts:%H:%M on %d/%m/%Y}
  Author: {author_name}, {author}, {specialty}
  Location: {location}
  Must cover: {cover}

HARD RULES
1. Use only the facts below. Do not invent clinical findings, results, doses, times or people.
2. Nothing that happens after {ts:%H:%M on %d/%m/%Y} may appear. Do not anticipate results or decisions not yet made.
3. If you quote a number (observation, blood result, dose, angle), it must match the value below exactly.
4. Refer to the patient by name or as "the patient"; do not invent a different name, hospital number or address.
5. Write in the register of the stated author: UK clinical English, standard NHS abbreviations (PC, HPC, PMH, DH, NKDA, O/E, obs, NBM, ORIF, T&O, FOOSH, CRT, ROM), terse sentence fragments where a real author would use them. Do not write like a textbook or a letter to a patient.
6. Sign off in house style with exactly this author, their role and the time: "{author_name}, {author}, {location}, {ts:%H:%M}". Do not invent any other clinician name anywhere in the note.
7. No bullet-point markdown, no headings in title case with hashes; use the plain in-note headings a UK clinician would type.

FACTS AVAILABLE AT {ts:%H:%M on %d/%m/%Y}
{facts}
"""


def clean(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```$", "", text.strip())
    return text.strip()


async def generate_notes(prompts):
    llm_module._loop_semaphore.set(asyncio.Semaphore(CONCURRENCY))
    return await asyncio.gather(*(call_llm_async(p, model=MODEL, temp=TEMP) for p in prompts))


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {path.name}: {len(rows)} rows")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. State and structured tables — code only, seeded RNG.
    s = build_state(SEED)
    events = build_events(s)
    observations = build_observations(s)
    limb_obs = build_limb_observations(s)
    labs = build_labs(s)
    meds = build_medications(s)
    labels = derive_labels(s, observations, limb_obs)

    # 2. Notes — LLM, constrained by the state at each timestamp.
    prompts = [
        build_prompt(s, slot, facts_block(s, events, observations, limb_obs, labs, meds, slot[1]))
        for slot in NOTE_SLOTS
    ]
    print(f"Generating {len(prompts)} notes ({MODEL.split('.')[-1]}, temp={TEMP})...")
    texts = asyncio.run(generate_notes(prompts))

    failed = [NOTE_SLOTS[i][0] for i, t in enumerate(texts) if t is None]
    if failed:
        raise SystemExit(f"LLM returned None for {failed} — not writing a partial dataset.")

    aug_rng = random.Random(SEED + 1)
    note_rows = []
    for slot, text in zip(NOTE_SLOTS, texts):
        note_id, ts, note_type, author, specialty, location, _, author_name = slot
        text = clean(text)
        edits = 0
        if "nursing" in note_type.lower() or "triage" in note_type.lower():
            text, edits = augment(text, aug_rng)
        note_rows.append(
            {
                "note_id": note_id,
                "patient_id": s["patient_id"],
                "encounter_id": s["encounter_id"],
                "note_datetime": ts.isoformat(sep=" "),
                "note_type": note_type,
                "author_name": author_name,
                "author_role": author,
                "specialty": specialty,
                "location": location,
                "note_text": text,
                "typo_edits_applied": edits,
            }
        )

    # 3. Write.
    print(f"Writing to {OUT_DIR}")
    write_csv(
        OUT_DIR / "patient.csv",
        [
            {
                "patient_id": s["patient_id"],
                "encounter_id": s["encounter_id"],
                "nhs_number": s["nhs_number"],
                "name": s["name"],
                "date_of_birth": s["date_of_birth"],
                "age_years": s["age"],
                "sex": s["sex"],
                "address": s["address"],
                "postcode": s["postcode"],
                "gp_practice": s["gp_practice"],
                "hospital": s["hospital"],
                "ward": s["ward"],
                "arrival_datetime": s["arrival_time"].isoformat(sep=" "),
                "arrival_mode": s["arrival_mode"],
                "injury_datetime": s["fall_time"].isoformat(sep=" "),
                "mechanism": s["mechanism"],
                "primary_diagnosis": s["diagnosis"],
                "injured_side": s["injured_side"],
                "dominant_hand": s["dominant_hand"],
                "height_cm": s["height_cm"],
                "weight_kg": s["weight_kg"],
                "allergies": s["allergy"],
                "smoking_status": s["smoker"],
                "alcohol_units_per_week": s["alcohol_units"],
                "social_circumstances": f"{s['lives_with']}. {s['mobility']}.",
                "admitted": "Yes",
                "planned_operation": s["planned_operation"],
                "planned_operation_date": s["planned_operation_date"],
            }
        ],
        [
            "patient_id", "encounter_id", "nhs_number", "name", "date_of_birth", "age_years", "sex",
            "address", "postcode", "gp_practice", "hospital", "ward", "arrival_datetime", "arrival_mode",
            "injury_datetime", "mechanism", "primary_diagnosis", "injured_side", "dominant_hand",
            "height_cm", "weight_kg", "allergies", "smoking_status", "alcohol_units_per_week",
            "social_circumstances", "admitted", "planned_operation", "planned_operation_date",
        ],
    )

    write_csv(
        OUT_DIR / "conditions.csv",
        [
            {"patient_id": s["patient_id"], "condition_id": f"COND-{i:03d}", "condition": c, "status": "Active", "onset": "Pre-existing"}
            for i, c in enumerate(s["conditions"], start=1)
        ]
        + [
            {
                "patient_id": s["patient_id"],
                "condition_id": f"COND-{len(s['conditions']) + 1:03d}",
                "condition": s["diagnosis"],
                "status": "Active",
                "onset": s["fall_time"].isoformat(sep=" "),
            }
        ],
        ["patient_id", "condition_id", "condition", "status", "onset"],
    )

    write_csv(
        OUT_DIR / "events.csv",
        [
            {
                "event_id": f"EVT-{i:03d}",
                "patient_id": s["patient_id"],
                "encounter_id": s["encounter_id"],
                "event_datetime": ts.isoformat(sep=" "),
                "event_type": kind,
                "location": loc,
                "description": desc,
            }
            for i, (ts, kind, loc, desc) in enumerate(events, start=1)
        ],
        ["event_id", "patient_id", "encounter_id", "event_datetime", "event_type", "location", "description"],
    )

    write_csv(OUT_DIR / "observations.csv", observations, list(observations[0].keys()))
    write_csv(OUT_DIR / "limb_observations.csv", limb_obs, list(limb_obs[0].keys()))
    write_csv(OUT_DIR / "labs.csv", labs, list(labs[0].keys()))
    write_csv(OUT_DIR / "medication_administrations.csv", meds, list(meds[0].keys()))
    write_csv(
        OUT_DIR / "regular_medications.csv",
        [
            {
                "patient_id": s["patient_id"],
                "medication": m[0],
                "dose": m[1],
                "route": m[2],
                "frequency": m[3],
                "source": "Pre-admission regular medicine",
            }
            for m in s["regular_meds"]
        ],
        ["patient_id", "medication", "dose", "route", "frequency", "source"],
    )
    write_csv(
        OUT_DIR / "labels.csv",
        [
            {"patient_id": s["patient_id"], "label_name": n, "label_value": v, "derivation": d, "derived_by": "code, before note text existed"}
            for n, v, d in labels
        ],
        ["patient_id", "label_name", "label_value", "derivation", "derived_by"],
    )
    write_csv(OUT_DIR / "clinical_notes.csv", note_rows, list(note_rows[0].keys()))

    print("Done.")


if __name__ == "__main__":
    main()
