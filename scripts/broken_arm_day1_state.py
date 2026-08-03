"""Patient state and derived tables for the broken-arm day-1 dataset.

Everything here is sampled or computed in code with a seeded RNG. No LLM is
involved: labels and structured values are fixed before any note text exists.

Clinical arc (fixed by the scenario, not sampled): fall on outstretched hand at
home -> ED -> closed dorsally displaced extra-articular distal radius fracture
-> haematoma block and closed reduction in ED -> backslab -> residual
angulation on check film -> admitted to trauma ward, listed for ORIF day 2.
"""

import random
from datetime import datetime, timedelta

from faker import Faker

SEED = 20260217
ADMISSION_DAY = datetime(2026, 2, 17)  # arbitrary synthetic date, one clock for all tables
PATIENT_ID = "SYN-BA-0001"
ENCOUNTER_ID = "SYN-BA-0001-ENC-01"
HOSPITAL = "Northfield General Hospital"  # fictional
WARD = "Ward 12 — Trauma & Orthopaedics"


def _t(hour, minute, day_offset=0):
    return ADMISSION_DAY + timedelta(days=day_offset, hours=hour, minutes=minute)


def _nhs_number(rng):
    """Synthetic NHS number in the 999 test range, with a valid mod-11 check digit."""
    while True:
        digits = [9, 9, 9] + [rng.randint(0, 9) for _ in range(6)]
        total = sum(d * (10 - i) for i, d in enumerate(digits))
        check = 11 - (total % 11)
        if check == 11:
            check = 0
        if check != 10:
            return "".join(str(d) for d in digits + [check])


def news2(rr, spo2, on_oxygen, sbp, pulse, acvpu, temp):
    """NEWS2 aggregate score, SpO2 scale 1. Computed, never asserted by an LLM."""
    score = 0
    score += 3 if rr <= 8 else 1 if rr <= 11 else 0 if rr <= 20 else 2 if rr <= 24 else 3
    score += 3 if spo2 <= 91 else 2 if spo2 <= 93 else 1 if spo2 <= 95 else 0
    score += 2 if on_oxygen else 0
    score += 3 if sbp <= 90 else 2 if sbp <= 100 else 1 if sbp <= 110 else 0 if sbp <= 219 else 3
    score += 3 if pulse <= 40 else 1 if pulse <= 50 else 0 if pulse <= 90 else 1 if pulse <= 110 else 2 if pulse <= 130 else 3
    score += 0 if acvpu == "Alert" else 3
    score += 3 if temp <= 35.0 else 1 if temp <= 36.0 else 0 if temp <= 38.0 else 1 if temp <= 39.0 else 2
    return score


def ckd_epi_2021(creatinine_umol_l, age, sex):
    """eGFR from creatinine, so the two results cannot contradict each other.
    CKD-EPI 2021 race-free equation."""
    scr = creatinine_umol_l / 88.4  # mg/dL
    kappa, alpha = (0.7, -0.241) if sex == "Female" else (0.9, -0.302)
    egfr = 142 * min(scr / kappa, 1) ** alpha * max(scr / kappa, 1) ** -1.200 * 0.9938**age
    if sex == "Female":
        egfr *= 1.012
    return round(egfr)


def build_state(seed=SEED):
    rng = random.Random(seed)
    fake = Faker("en_GB")
    fake.seed_instance(seed)

    sex = "Female" if rng.random() < 0.68 else "Male"
    age = max(52, min(88, int(rng.gauss(71, 8)))) if sex == "Female" else max(45, min(84, int(rng.gauss(66, 10))))
    name = fake.name_female() if sex == "Female" else fake.name_male()
    injured_side = "Right" if rng.random() < 0.55 else "Left"
    dominant_hand = "Right" if rng.random() < 0.9 else "Left"

    # Comorbidities: sampled from a weighted list, each carrying its own regular medication.
    candidates = [
        ("Essential hypertension", 0.55, ("Amlodipine", "5 mg", "PO", "Once daily", 8)),
        ("Osteoporosis", 0.45, ("Alendronic acid", "70 mg", "PO", "Once weekly (Mondays)", None)),
        ("Type 2 diabetes mellitus", 0.20, ("Metformin", "500 mg", "PO", "Twice daily", 8)),
        ("Hypothyroidism", 0.15, ("Levothyroxine", "75 microgram", "PO", "Once daily", 7)),
        ("Hypercholesterolaemia", 0.35, ("Atorvastatin", "20 mg", "PO", "Once daily", 22)),
        ("Osteoarthritis of the knees", 0.25, None),
    ]
    conditions, regular_meds = [], []
    for label, prevalence, med in candidates:
        if rng.random() < prevalence:
            conditions.append(label)
            if med:
                regular_meds.append(med)
    if "Osteoporosis" not in conditions and sex == "Female" and age >= 65:
        conditions.append("Osteopenia")  # bone-health context for a fragility fracture

    allergy = "No known drug allergies" if rng.random() < 0.6 else "Penicillin — rash"
    smoker = rng.choice(["Never smoked", "Ex-smoker", "Ex-smoker", "Current smoker"])
    alcohol_units = rng.choice([0, 2, 4, 6, 8, 10])
    lives_with = rng.choice(["Lives alone", "Lives alone", "Lives with spouse"])
    mobility = "Independently mobile, no walking aid" if age < 75 else rng.choice(
        ["Independently mobile, no walking aid", "Mobilises with a walking stick outdoors"]
    )

    state = {
        "patient_id": PATIENT_ID,
        "encounter_id": ENCOUNTER_ID,
        "nhs_number": _nhs_number(rng),
        "name": name,
        "sex": sex,
        "age": age,
        "date_of_birth": (ADMISSION_DAY - timedelta(days=age * 365 + rng.randint(0, 364))).date().isoformat(),
        "address": fake.street_address().replace("\n", ", "),
        "postcode": fake.postcode(),
        "gp_practice": "Brookvale Medical Centre",  # fictional
        "hospital": HOSPITAL,
        "ward": WARD,
        "injured_side": injured_side,
        "dominant_hand": dominant_hand,
        "conditions": conditions,
        "regular_meds": regular_meds,
        "allergy": allergy,
        "smoker": smoker,
        "alcohol_units": alcohol_units,
        "lives_with": lives_with,
        "mobility": mobility,
        "weight_kg": round(rng.uniform(55, 88), 1),
        "height_cm": rng.randint(152, 178),
        # Fixed clinical arc
        "mechanism": "Fall from standing height onto outstretched hand on an icy path outside her home"
        if sex == "Female"
        else "Fall from standing height onto outstretched hand on an icy path outside his home",
        "fall_time": _t(9, 20),
        "arrival_time": _t(10, 2),
        "arrival_mode": "Self-presented, brought by neighbour by car",
        "diagnosis": f"Closed dorsally displaced extra-articular fracture of the {injured_side.lower()} distal radius",
        "diagnosis_short": "Closed distal radius fracture (Colles'-pattern)",
        "radiographic_features": (
            "Dorsal displacement and dorsal angulation of the distal fragment, minimal comminution of the "
            "dorsal cortex, no intra-articular extension, carpal alignment maintained, associated ulnar "
            "styloid avulsion, soft tissue swelling"
        ),
        "ulnar_styloid": True,
        "open_fracture": False,
        "head_injury": False,
        "loss_of_consciousness": False,
        "paraesthesia_at_presentation": True,  # median nerve distribution, resolves after reduction
        "reduction_time": _t(12, 48),
        "reduction_method": "Haematoma block with 10 mL 1% lidocaine, closed manipulation, below-elbow dorsal backslab",
        "post_reduction_result": "Improved alignment but residual dorsal angulation of approximately 12 degrees with 2 mm radial shortening",
        "admitted": True,
        "plan": "Admit to trauma ward for elevation and neurovascular observation; list for ORIF (volar locking plate) on the day-2 trauma list; NBM from 02:00",
        "planned_operation": "Open reduction and internal fixation, volar locking plate",
        "planned_operation_date": (ADMISSION_DAY + timedelta(days=1)).date().isoformat(),
        "day1_end": _t(9, 0, day_offset=1),
    }
    state["rng"] = rng
    return state


def build_events(s):
    """Timeline. Every note is anchored to one of these."""
    side = s["injured_side"].lower()
    return [
        (s["fall_time"], "Injury", "Home", f"Fall onto outstretched {side} hand"),
        (s["arrival_time"], "ED arrival", "Emergency Department", "Booked in at ED reception"),
        (_t(10, 11), "Triage", "ED Majors", "Nurse triage, first observations and pain score"),
        (_t(10, 22), "Analgesia", "ED Majors", "IV paracetamol and oral morphine given"),
        (_t(10, 48), "ED clerking", "ED Majors", "Assessed by ED doctor; wrist immobilised in temporary splint"),
        (_t(11, 5), "Phlebotomy", "ED Majors", "Bloods taken: FBC, U&E, bone profile, coagulation, group and save"),
        (_t(11, 30), f"Imaging — X-ray {side} wrist", "Radiology", "AP and lateral radiographs of the wrist"),
        (_t(11, 52), "Radiology report", "Radiology", "Report issued for pre-reduction radiographs"),
        (_t(12, 48), "Procedure — closed reduction", "ED Majors", "Haematoma block and manipulation; backslab applied"),
        (_t(13, 20), f"Imaging — check X-ray {side} wrist", "Radiology", "Post-reduction radiographs in plaster"),
        (_t(13, 40), "Radiology report", "Radiology", "Report issued for post-reduction radiographs"),
        (_t(14, 20), "Orthopaedic review", "ED Majors", "Reviewed by T&O registrar; decision to admit and list for ORIF"),
        (_t(15, 50), "Ward transfer", WARD, "Transferred to trauma ward, bed 6"),
        (_t(16, 5), "Nursing admission assessment", WARD, "Ward nursing admission, risk assessments completed"),
        (_t(16, 30), "VTE prophylaxis", WARD, "Enoxaparin given"),
        (_t(18, 30), "Pre-operative assessment", WARD, "Anaesthetic review ahead of day-2 list"),
        (_t(21, 40), "Nursing progress note", WARD, "Evening review and limb observations"),
        (_t(2, 0, 1), "Nil by mouth", WARD, "NBM commenced for theatre"),
        (_t(2, 30, 1), "Night nursing note", WARD, "Night observations and limb check"),
        (_t(8, 15, 1), "Consultant ward round", WARD, "Trauma consultant ward round; confirmed for afternoon list"),
    ]


def build_observations(s):
    """Vitals + pain, with NEWS2 computed from the vitals in code."""
    rng = s["rng"]
    base_hr = rng.randint(70, 80)
    base_sbp = rng.randint(128, 142)
    base_dbp = rng.randint(72, 84)
    # (time, hr offset, sbp offset, rr, spo2, temp, pain, context)
    arc = [
        (_t(10, 11), 24, 14, 20, 96, 36.6, 8, "Triage — in severe pain, deformed wrist"),
        (_t(10, 50), 16, 8, 18, 97, 36.5, 7, "Post first analgesia"),
        (_t(12, 45), 18, 10, 18, 97, 36.7, 8, "Pre-procedure"),
        (_t(13, 10), 2, -8, 15, 96, 36.4, 2, "Post reduction, post haematoma block"),
        (_t(14, 0), 0, -4, 16, 97, 36.6, 2, "Pre-transfer to ward"),
        (_t(16, 10), 1, 0, 16, 97, 36.8, 3, "Ward admission observations"),
        (_t(20, 0), 3, 2, 17, 97, 36.9, 4, "Evening round"),
        (_t(0, 0, 1), 6, 4, 17, 96, 37.0, 5, "Night — woken by pain, PRN analgesia requested"),
        (_t(4, 0, 1), -2, -2, 15, 97, 36.6, 2, "Night observations"),
        (_t(7, 0, 1), 0, 0, 16, 97, 36.7, 2, "Pre-theatre observations"),
    ]
    rows = []
    for i, (ts, dhr, dsbp, rr, spo2, temp, pain, context) in enumerate(arc, start=1):
        hr = base_hr + dhr + rng.randint(-3, 3)
        sbp = base_sbp + dsbp + rng.randint(-4, 4)
        dbp = base_dbp + round(dsbp / 2) + rng.randint(-4, 4)
        temp = round(temp + rng.uniform(-0.1, 0.1), 1)
        score = news2(rr, spo2, False, sbp, hr, "Alert", temp)
        rows.append(
            {
                "observation_id": f"OBS-{i:03d}",
                "patient_id": s["patient_id"],
                "encounter_id": s["encounter_id"],
                "observation_datetime": ts.isoformat(sep=" "),
                "respiratory_rate_per_min": rr,
                "spo2_percent": spo2,
                "supplemental_oxygen": "No",
                "systolic_bp_mmhg": sbp,
                "diastolic_bp_mmhg": dbp,
                "pulse_bpm": hr,
                "temperature_c": temp,
                "consciousness_acvpu": "Alert",
                "pain_score_0_10": pain,
                "news2_total": score,
                "context": context,
            }
        )
    return rows


def build_limb_observations(s):
    """Neurovascular observations of the injured limb — the coherence spine for the
    paraesthesia thread that runs through the notes."""
    side = s["injured_side"]
    arc = [
        (_t(10, 15), "Temporary splint", "Pink", "<2", "Present", "Reduced — tingling in thumb, index and middle finger", "Moderate", "Able to flex fingers, limited by pain"),
        (_t(12, 45), "Temporary splint", "Pink", "<2", "Present", "Reduced — tingling in thumb, index and middle finger", "Moderate", "Able to flex fingers, limited by pain"),
        (_t(13, 15), "Below-elbow dorsal backslab", "Pink", "<2", "Present", "Improved — mild tingling in thumb only", "Moderate", "Full active finger flexion and extension"),
        (_t(16, 10), "Below-elbow dorsal backslab", "Pink", "<2", "Present", "Normal", "Mild", "Full active finger flexion and extension"),
        (_t(21, 40), "Below-elbow dorsal backslab", "Pink", "<2", "Present", "Normal", "Mild", "Full active finger flexion and extension"),
        (_t(2, 30, 1), "Below-elbow dorsal backslab", "Pink", "<2", "Present", "Normal", "Mild", "Full active finger flexion and extension"),
        (_t(7, 0, 1), "Below-elbow dorsal backslab", "Pink", "<2", "Present", "Normal", "Mild", "Full active finger flexion and extension"),
    ]
    rows = []
    for i, (ts, immob, colour, crt, pulse, sensation, swelling, movement) in enumerate(arc, start=1):
        rows.append(
            {
                "limb_observation_id": f"LIMB-{i:03d}",
                "patient_id": s["patient_id"],
                "encounter_id": s["encounter_id"],
                "observation_datetime": ts.isoformat(sep=" "),
                "limb": f"{side} forearm and hand",
                "immobilisation": immob,
                "colour": colour,
                "capillary_refill_seconds": crt,
                "radial_pulse": pulse,
                "sensation": sensation,
                "swelling": swelling,
                "active_movement": movement,
                "elevated": "Yes" if ts >= _t(13, 15) else "No",
            }
        )
    return rows


def build_labs(s):
    rng = s["rng"]
    drawn = _t(11, 5)
    reported = _t(12, 20)
    # (test, value, unit, ref range, flag)
    hb = rng.randint(108, 126) if s["sex"] == "Female" else rng.randint(125, 150)
    hb_ref = "115-165" if s["sex"] == "Female" else "130-180"
    creat = rng.randint(68, 96)
    egfr = ckd_epi_2021(creat, s["age"], s["sex"])
    results = [
        ("Haemoglobin", hb, "g/L", hb_ref, "Low" if (s["sex"] == "Female" and hb < 115) else "Normal"),
        ("White cell count", round(rng.uniform(6.2, 10.4), 1), "10^9/L", "4.0-11.0", "Normal"),
        ("Platelets", rng.randint(190, 340), "10^9/L", "150-400", "Normal"),
        ("Sodium", rng.randint(136, 143), "mmol/L", "133-146", "Normal"),
        ("Potassium", round(rng.uniform(3.7, 4.7), 1), "mmol/L", "3.5-5.3", "Normal"),
        ("Urea", round(rng.uniform(4.2, 7.4), 1), "mmol/L", "2.5-7.8", "Normal"),
        ("Creatinine", creat, "umol/L", "45-84" if s["sex"] == "Female" else "59-104", "High" if (s["sex"] == "Female" and creat > 84) else "Normal"),
        ("eGFR", egfr, "mL/min/1.73m2", ">90", "Low"),
        ("C-reactive protein", round(rng.uniform(1.0, 6.0), 1), "mg/L", "<5", "Normal"),
        ("Adjusted calcium", round(rng.uniform(2.20, 2.45), 2), "mmol/L", "2.20-2.60", "Normal"),
        ("Phosphate", round(rng.uniform(0.85, 1.35), 2), "mmol/L", "0.80-1.50", "Normal"),
        ("Alkaline phosphatase", rng.randint(58, 108), "U/L", "30-130", "Normal"),
        ("Vitamin D (25-OH)", rng.randint(28, 46), "nmol/L", ">50", "Low"),
        ("INR", round(rng.uniform(0.9, 1.1), 1), "ratio", "0.8-1.2", "Normal"),
        ("Group and save", "Sample received, group O RhD positive", "", "", "Normal"),
    ]
    rows = []
    for i, (test, value, unit, ref, flag) in enumerate(results, start=1):
        rows.append(
            {
                "result_id": f"LAB-{i:03d}",
                "patient_id": s["patient_id"],
                "encounter_id": s["encounter_id"],
                "collected_datetime": drawn.isoformat(sep=" "),
                "reported_datetime": reported.isoformat(sep=" "),
                "panel": "Pre-operative bloods",
                "test_name": test,
                "value": value,
                "unit": unit,
                "reference_range": ref,
                "abnormal_flag": flag,
            }
        )
    return rows


def build_medications(s):
    """Inpatient administrations across day 1, plus regular medicines continued in hospital."""
    admin = [
        (_t(10, 22), "Paracetamol", "1 g", "IV", "Acute pain", "Given"),
        (_t(10, 25), "Morphine sulfate oral solution", "5 mg", "PO", "Acute pain (age-adjusted dose)", "Given"),
        (_t(12, 48), "Lidocaine 1%", "10 mL", "Haematoma block", "Local anaesthesia for closed reduction", "Given"),
        (_t(13, 10), "Ondansetron", "4 mg", "IV", "Nausea after opioid", "Given"),
        (_t(16, 30), "Enoxaparin sodium", "40 mg", "SC", "VTE prophylaxis", "Given"),
        (_t(18, 0), "Paracetamol", "1 g", "PO", "Regular analgesia", "Given"),
        (_t(22, 0), "Paracetamol", "1 g", "PO", "Regular analgesia", "Given"),
        (_t(0, 5, 1), "Morphine sulfate oral solution", "5 mg", "PO", "PRN analgesia, pain score 5/10", "Given"),
        (_t(6, 0, 1), "Paracetamol", "1 g", "IV", "Regular analgesia — IV route as nil by mouth from 02:00", "Given"),
    ]
    rows = []
    for i, (ts, drug, dose, route, indication, status) in enumerate(admin, start=1):
        rows.append(
            {
                "administration_id": f"MED-{i:03d}",
                "patient_id": s["patient_id"],
                "encounter_id": s["encounter_id"],
                "administration_datetime": ts.isoformat(sep=" "),
                "medication": drug,
                "dose": dose,
                "route": route,
                "indication": indication,
                "status": status,
            }
        )
    # Regular home medicines continued on the ward, given at their usual times.
    n = len(rows)
    for j, (drug, dose, route, freq, hour) in enumerate(s["regular_meds"], start=1):
        if hour is None:
            continue
        morning = hour < 12  # falls on day 2, after NBM started at 02:00
        ts = _t(hour, 0, 1) if morning else _t(hour, 0)
        if not morning:
            status = "Given"
        elif drug == "Metformin":
            status = "Withheld — nil by mouth for theatre"
        else:
            status = "Given with sips of water (pre-operative)"
        rows.append(
            {
                "administration_id": f"MED-{n + j:03d}",
                "patient_id": s["patient_id"],
                "encounter_id": s["encounter_id"],
                "administration_datetime": ts.isoformat(sep=" "),
                "medication": drug,
                "dose": dose,
                "route": route,
                "indication": f"Regular medicine continued in hospital ({freq})",
                "status": status,
            }
        )
    rows.sort(key=lambda r: r["administration_datetime"])
    return rows


def derive_labels(s, observations, limb_obs):
    """Ground truth for downstream extraction/prediction PoCs.

    Derived from the state and the code-built tables only. Fixed before any note
    text exists, so a model that reads the notes is not being scored against
    something an LLM also wrote.
    """
    max_news = max(o["news2_total"] for o in observations)
    peak_pain = max(o["pain_score_0_10"] for o in observations)
    pain_after = [o["pain_score_0_10"] for o in observations if o["observation_datetime"] > s["reduction_time"].isoformat(sep=" ")]
    return [
        ("fracture_present", "True", "Scenario definition (fixed)"),
        ("fracture_site", f"{s['injured_side']} distal radius", "Scenario definition (fixed)"),
        ("fracture_pattern", "Extra-articular, dorsally displaced (Colles'-pattern)", "Scenario definition (fixed)"),
        ("associated_injury", "Ulnar styloid avulsion" if s["ulnar_styloid"] else "None", "Scenario definition (fixed)"),
        ("intra_articular_extension", "False", "Scenario definition (fixed)"),
        ("comminution", "Minimal, dorsal cortex only", "Scenario definition (fixed)"),
        ("open_fracture", str(s["open_fracture"]), "Scenario definition (fixed)"),
        ("injured_side", s["injured_side"], "Sampled in code, seeded RNG"),
        ("dominant_hand_injured", str(s["injured_side"] == s["dominant_hand"]), "Comparison of two sampled fields"),
        ("mechanism_category", "Fall from standing height (fragility mechanism)", "Scenario definition (fixed)"),
        ("median_nerve_paraesthesia_at_presentation", str(s["paraesthesia_at_presentation"]), "Scenario definition (fixed)"),
        ("paraesthesia_resolved_after_reduction", "True", f"limb_observations.csv sensation field at {limb_obs[3]['observation_datetime']}"),
        ("closed_reduction_performed", "True", "Scenario definition (fixed)"),
        ("anaesthetic_for_reduction", "Haematoma block, 10 mL 1% lidocaine", "medication_administrations.csv MED-003"),
        ("reduction_adequate", "False", "Scenario definition (fixed) — residual dorsal angulation"),
        ("admitted", str(s["admitted"]), "Scenario definition (fixed)"),
        ("planned_operation", s["planned_operation"], "Scenario definition (fixed)"),
        ("planned_operation_date", s["planned_operation_date"], "Scenario definition (fixed)"),
        ("opioid_administered_day1", "True", "medication_administrations.csv"),
        ("vte_prophylaxis_given_day1", "True", "medication_administrations.csv MED-005"),
        ("peak_pain_score_day1", str(peak_pain), "max of observations.csv pain_score_0_10"),
        ("pain_controlled_after_reduction", str(max(pain_after) <= 5), "observations.csv, post-reduction rows"),
        ("max_news2_day1", str(max_news), "max of observations.csv news2_total (computed by news2())"),
        ("escalation_of_care_required", str(max_news >= 5), "Threshold applied to max_news2_day1"),
        ("compartment_syndrome", "False", "limb_observations.csv — all rows perfused, no escalating pain"),
        ("length_of_stay_days_at_day1_end", "1", "Timeline: still an inpatient at end of day 1"),
    ]
