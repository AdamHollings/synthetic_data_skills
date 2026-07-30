"""Generate one semi-structured admission note in broken_Arm_data/data.csv.

Seeding case: from intelligence (no real seed data). The clinical scenario is fixed - a
fragility distal radius fracture admitted for fixation - and the per-patient detail is
sampled from a seeded RNG. The note is rendered from the state, so every clinical fact in
the prose comes from a field set before the prose existed. See broken_Arm_data/REPORT.md.
"""

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from faker import Faker

MASTER_SEED = 20260729
REFERENCE_DATE = date(2026, 7, 29)
OUT = Path(__file__).resolve().parents[1] / "broken_Arm_data" / "data.csv"


def patient_state(index):
    """The structured record. Everything the note says is fixed here first."""
    rng = random.Random(MASTER_SEED + index)
    fake = Faker("en_GB")
    fake.seed_instance(MASTER_SEED + index)

    age = rng.randint(65, 79)
    dob = REFERENCE_DATE - timedelta(days=age * 365 + rng.randint(0, 364))
    # Fall late afternoon, ED an hour later, manipulation, then clerking on the ward.
    injury = datetime.combine(REFERENCE_DATE, datetime.min.time()) + timedelta(
        hours=16, minutes=rng.randrange(0, 60, 5))

    return {
        "patient_id": f"BA{index + 1:03d}",
        "name": f"{fake.first_name_female()} {fake.last_name()}",
        "sex": "female",
        "date_of_birth": dob,
        "age": age,
        "hospital_number": f"{rng.randint(1000000, 9999999)}",

        # Injury and timeline. One clock: every time below derives from `injury`.
        "injury_datetime": injury,
        "ed_arrival": injury + timedelta(minutes=35),
        "xray_time": injury + timedelta(minutes=70),
        "manipulation_time": injury + timedelta(minutes=95),
        "clerking_time": injury + timedelta(minutes=130),
        "surgery_date": REFERENCE_DATE + timedelta(days=1),

        # Fracture. Dorsally displaced comminuted intra-articular distal radius fracture
        # with ulnar styloid involvement - the common fragility pattern in this age/sex.
        "side": "right",
        "hand_dominance": "right",
        "site": "distal radius",
        "pattern": "dorsally displaced, comminuted, intra-articular",
        "associated": "ulnar styloid",
        "open_fracture": False,
        "mechanism": "mechanical fall from standing height onto outstretched hand",
        "dorsal_tilt_pre": 26,
        "dorsal_tilt_post": 12,
        "radial_height_loss_mm": 5,
        "neurovascular_intact": True,
        "compartment_syndrome": False,

        # Management: reduction failed to hold, so this is an admission for fixation.
        "ed_procedure": "manipulation under haematoma block, dorsal below-elbow backslab",
        "reduction_stable": False,
        "management": "open reduction and internal fixation, volar locking plate",

        # Observations at clerking. NEWS 0 - no parameter scores.
        "hr": rng.randint(74, 90),
        "bp_systolic": rng.randint(138, 156),
        "bp_diastolic": rng.randint(78, 88),
        "rr": 16,
        "spo2": 97,
        "temp": 36.6,
        "news": 0,

        # Bloods, plausible for a well 65-79 year old woman.
        "hb": rng.randint(120, 138),
        "wcc": 8.4,
        "platelets": 254,
        "sodium": 139,
        "potassium": 4.2,
        "urea": 5.6,
        "creatinine": 78,

        "pmh": ["hypertension", "hypothyroidism", "osteoarthritis of both knees"],
        "meds": ["amlodipine 5mg OD", "atorvastatin 20mg ON", "levothyroxine 75mcg OD"],
        "allergy": "penicillin - rash",
        "social": "lives alone in a ground-floor flat, independent, no falls in the last year",
    }


def render_note(s):
    """Render the note. Reads only from `s` - no clinical fact originates here."""
    dt = lambda t: t.strftime("%d/%m/%Y %H:%M")
    hm = lambda t: t.strftime("%H:%M")
    limb = f"{s['side']} upper limb"
    dominance = "dominant" if s["side"] == s["hand_dominance"] else "non-dominant"
    # Not .capitalize() - that would lowercase the OD/ON dosing abbreviations.
    sentence = lambda parts: (lambda t: t[0].upper() + t[1:])("; ".join(parts))

    return f"""ADMISSION NOTE
Ward: Trauma & Orthopaedics
Admitted: {dt(s['clerking_time'])}
Clerked by: FY2 in Trauma & Orthopaedics

Patient: {s['name']}
DOB: {s['date_of_birth'].strftime('%d/%m/%Y')} ({s['age']}y)   Sex: {s['sex'].capitalize()}
Hospital no: {s['hospital_number']}

PRESENTING COMPLAINT
Pain and deformity of the {s['side']} wrist following a fall at home.

HISTORY OF PRESENTING COMPLAINT
{s['age']}y {s['sex']} brought to ED at {hm(s['ed_arrival'])} after a {s['mechanism']} at
approximately {hm(s['injury_datetime'])} today. Tripped on a rug indoors, fell forwards,
put the {s['side']} hand out to save herself. Immediate pain and obvious deformity of the
{s['side']} wrist, unable to use the arm since. No loss of consciousness, no head strike,
no preceding dizziness, chest pain or palpitations - a mechanical fall. No other injury;
no neck or back pain, no other limb pain, able to weight-bear normally. Denies numbness or
tingling in the hand at any point. {s['side'].capitalize()}-hand {dominance}.

PAST MEDICAL HISTORY
{sentence(s['pmh'])}. No previous fragility fracture. No previous surgery to
this limb.

DRUG HISTORY
{sentence(s['meds'])}. No anticoagulant or antiplatelet. Not on bone protection.
ALLERGIES: {s['allergy']}.

SOCIAL HISTORY
{s['social'].capitalize()}. Non-smoker. Minimal alcohol. Daughter lives nearby.

ON EXAMINATION
Obs: HR {s['hr']}, BP {s['bp_systolic']}/{s['bp_diastolic']}, RR {s['rr']},
  SpO2 {s['spo2']}% on air, temp {s['temp']}C. NEWS {s['news']}.
  Alert and orientated, comfortable at rest post-analgesia.
{limb.capitalize()}: dorsal angulation of the distal forearm with the classic dinner-fork
  deformity. Swelling and tenderness over the distal radius and over the ulnar styloid.
  Skin intact, no wound, no tenting, no blistering - closed injury.
Neurovascular: radial pulse present, capillary refill <2s, hand warm and well perfused.
  Sensation intact in median, ulnar and radial nerve distributions, including normal
  sensation over the volar thumb and index finger. Able to flex and extend all fingers.
  No pain on passive finger extension. No features of acute carpal tunnel syndrome and
  no features of compartment syndrome.
Elbow and shoulder on the same side: no tenderness, full passive range, no deformity.
Systemic: chest clear, heart sounds normal, abdomen soft. No head injury. C-spine
  non-tender. No other bony tenderness on secondary survey.

IMAGING
Plain radiographs {s['side']} wrist, AP and lateral, {hm(s['xray_time'])}:
  {s['pattern'].capitalize()} fracture of the {s['site']} with {s['dorsal_tilt_pre']} degrees
  of dorsal tilt and approximately {s['radial_height_loss_mm']}mm loss of radial height.
  Associated {s['associated']} fracture. No carpal fracture, no dislocation.

PROCEDURE IN ED
{s['ed_procedure'].capitalize()} at {hm(s['manipulation_time'])}.
Post-reduction radiographs: improved but not anatomical - residual dorsal tilt
{s['dorsal_tilt_post']} degrees with persisting articular step. Reduction not held.
Neurovascular status unchanged after manipulation and after casting.

INVESTIGATIONS
Hb {s['hb']}, WCC {s['wcc']}, platelets {s['platelets']}.
Na {s['sodium']}, K {s['potassium']}, urea {s['urea']}, creatinine {s['creatinine']}.
Group and save sent. ECG: sinus rhythm, no acute change.

IMPRESSION
1. Closed {s['pattern']} fracture of the {s['side']} {s['site']} with
   {s['associated']} fracture, neurovascularly intact, unstable after closed reduction.
2. Fragility fracture in a {s['age']}y {s['sex']} - low-energy mechanical fall.
For {s['management']}.

PLAN
1. Admit under Trauma & Orthopaedics. Consultant informed, listed for
   {s['management']} on the {s['surgery_date'].strftime('%d/%m/%Y')} trauma list.
2. Nil by mouth from midnight. IV fluids while fasting.
3. Elevate {limb} in a Bradford sling. Backslab checked - not circumferential,
   not tight.
4. Hourly neurovascular observations overnight. Escalate immediately for increasing pain,
   pain on passive finger extension, altered sensation in the thumb or index finger, or
   loss of the radial pulse.
5. Analgesia: regular paracetamol and PRN oral morphine. Avoid NSAIDs given age and
   antihypertensive use.
6. Continue usual medications.
7. Pre-op: anaesthetic review, consent, mark the {s['side']} arm. Group and save valid.
8. VTE risk assessment completed - mobile, mechanical prophylaxis; review chemical
   prophylaxis if mobility drops.
9. Fragility fracture pathway: bone profile and vitamin D, refer to the fracture liaison
   service for DXA and bone protection.
10. Falls assessment and lying/standing BP. Occupational therapy review re: coping at home
    alone with one arm before discharge.
"""


def main():
    state = patient_state(0)
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["patient_id", "note_text"])
        writer.writeheader()
        writer.writerow({"patient_id": state["patient_id"], "note_text": render_note(state)})
    print(f"wrote 1 row to {OUT}")


if __name__ == "__main__":
    main()
