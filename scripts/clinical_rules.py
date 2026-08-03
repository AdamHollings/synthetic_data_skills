"""Declarative clinical-plausibility and internal-consistency checker.

Rules are data: each is (id, level, description, check function returning a list of
offending records). Deterministic, re-runnable, and the thing that a model eyeballing
the files would get wrong in both directions.

Level 2 = cross-modal agreement (notes vs the structured tables, everything vs the clock).
Level 3 = clinical logic a clinician would catch.

Run:  .venv/Scripts/python.exe scripts/clinical_rules.py data/broken_arm_day1
"""

import csv
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from broken_arm_day1_state import ckd_epi_2021, news2

PHYSIOLOGICAL_LIMITS = {
    "respiratory_rate_per_min": (4, 60),
    "spo2_percent": (50, 100),
    "systolic_bp_mmhg": (50, 260),
    "diastolic_bp_mmhg": (20, 150),
    "pulse_bpm": (20, 220),
    "temperature_c": (30.0, 43.0),
    "pain_score_0_10": (0, 10),
}

PENICILLINS = ["penicillin", "amoxicillin", "co-amoxiclav", "flucloxacillin", "benzylpenicillin", "piperacillin"]

# Regular medicine -> the condition that justifies it. A medicine with no matching
# condition on the record is the classic Faker-style incoherence.
MED_CONDITION = {
    "Amlodipine": ["hypertension"],
    "Atorvastatin": ["hypercholesterolaemia"],
    "Metformin": ["diabetes"],
    "Levothyroxine": ["hypothyroidism"],
    "Alendronic acid": ["osteoporosis", "osteopenia"],
}


def load(d, name):
    with open(d / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def dt(value):
    return datetime.fromisoformat(value)


def check_physiological_ranges(t):
    bad = []
    for row in t["observations"]:
        for field, (lo, hi) in PHYSIOLOGICAL_LIMITS.items():
            v = float(row[field])
            if not lo <= v <= hi:
                bad.append(f"{row['observation_id']} {field}={v} outside {lo}-{hi}")
    return bad


def check_news2_recomputed(t):
    bad = []
    for row in t["observations"]:
        expected = news2(
            int(row["respiratory_rate_per_min"]),
            int(row["spo2_percent"]),
            row["supplemental_oxygen"] == "Yes",
            int(row["systolic_bp_mmhg"]),
            int(row["pulse_bpm"]),
            row["consciousness_acvpu"],
            float(row["temperature_c"]),
        )
        if expected != int(row["news2_total"]):
            bad.append(f"{row['observation_id']} recorded NEWS2 {row['news2_total']}, recomputed {expected}")
    return bad


def check_bp_ordering(t):
    return [
        f"{r['observation_id']} systolic {r['systolic_bp_mmhg']} <= diastolic {r['diastolic_bp_mmhg']}"
        for r in t["observations"]
        if int(r["systolic_bp_mmhg"]) <= int(r["diastolic_bp_mmhg"])
    ]


def check_egfr_creatinine(t):
    labs = {r["test_name"]: r["value"] for r in t["labs"]}
    p = t["patient"][0]
    if "Creatinine" not in labs or "eGFR" not in labs:
        return ["creatinine or eGFR missing"]
    expected = ckd_epi_2021(float(labs["Creatinine"]), int(p["age_years"]), p["sex"])
    if abs(expected - float(labs["eGFR"])) > 3:
        return [f"eGFR {labs['eGFR']} inconsistent with creatinine {labs['Creatinine']} (expected ~{expected})"]
    return []


def check_lab_flags(t):
    bad = []
    for r in t["labs"]:
        ref, flag = r["reference_range"], r["abnormal_flag"]
        m = re.fullmatch(r"([\d.]+)-([\d.]+)", ref)
        if not m:
            continue
        lo, hi = float(m.group(1)), float(m.group(2))
        v = float(r["value"])
        expected = "Low" if v < lo else "High" if v > hi else "Normal"
        if expected != flag:
            bad.append(f"{r['test_name']} {v} vs ref {ref} flagged {flag}, expected {expected}")
    return bad


def check_allergy_respected(t):
    allergies = t["patient"][0]["allergies"].lower()
    bad = []
    for r in t["medication_administrations"]:
        drug = r["medication"].lower()
        if "penicillin" in allergies and any(p in drug for p in PENICILLINS):
            bad.append(f"{r['administration_id']} {r['medication']} given despite {t['patient'][0]['allergies']}")
    return bad


def check_med_has_indication(t):
    conditions = " ".join(c["condition"].lower() for c in t["conditions"])
    return [
        f"{r['medication']} on the regular list with no matching condition recorded"
        for r in t["regular_medications"]
        if r["medication"] in MED_CONDITION
        and not any(c in conditions for c in MED_CONDITION[r["medication"]])
    ]


def check_paracetamol_dosing(t):
    doses = [r for r in t["medication_administrations"] if r["medication"] == "Paracetamol" and r["status"].startswith("Given")]
    bad = []
    for a, b in zip(doses, doses[1:]):
        gap = dt(b["administration_datetime"]) - dt(a["administration_datetime"])
        if gap < timedelta(hours=4):
            bad.append(f"paracetamol doses {gap} apart ({a['administration_id']} -> {b['administration_id']})")
    for day in {dt(r["administration_datetime"]).date() for r in doses}:
        grams = sum(float(r["dose"].split()[0]) for r in doses if dt(r["administration_datetime"]).date() == day)
        if grams > 4:
            bad.append(f"paracetamol {grams} g on {day}, exceeds 4 g/24h")
    return bad


def check_opioid_dose_for_age(t):
    age = int(t["patient"][0]["age_years"])
    return [
        f"{r['administration_id']} oral morphine {r['dose']} in a {age}-year-old (expect <=10 mg per dose over 65)"
        for r in t["medication_administrations"]
        if "morphine" in r["medication"].lower() and age >= 65 and float(r["dose"].split()[0]) > 10
    ]


def check_nbm_respected(t):
    """Nothing oral after the nil-by-mouth event."""
    nbm = [e for e in t["events"] if e["event_type"] == "Nil by mouth"]
    if not nbm:
        return []
    start = dt(nbm[0]["event_datetime"])
    return [
        f"{r['administration_id']} {r['medication']} PO at {r['administration_datetime']} after NBM at {start}"
        for r in t["medication_administrations"]
        if r["route"] == "PO" and dt(r["administration_datetime"]) > start and r["status"] == "Given"
    ]


def check_limb_perfusion(t):
    """Fracture-specific: a limb in plaster must stay perfused, and the compartment
    syndrome label must agree with the limb observations."""
    bad = []
    for r in t["limb_observations"]:
        if r["radial_pulse"].lower() != "present" or r["colour"].lower() != "pink":
            bad.append(f"{r['limb_observation_id']} perfusion compromised: pulse {r['radial_pulse']}, colour {r['colour']}")
        if not r["capillary_refill_seconds"].startswith("<"):
            bad.append(f"{r['limb_observation_id']} CRT {r['capillary_refill_seconds']}")
    label = {r["label_name"]: r["label_value"] for r in t["labels"]}
    if label.get("compartment_syndrome") == "False" and bad:
        bad.append("compartment_syndrome label False but perfusion findings above disagree")
    return bad


def check_cast_before_limb_obs(t):
    """No note or observation may describe a backslab before it was applied."""
    reduction = [e for e in t["events"] if "closed reduction" in e["event_type"].lower()][0]
    applied = dt(reduction["event_datetime"])
    return [
        f"{r['limb_observation_id']} records a backslab at {r['observation_datetime']}, applied {applied}"
        for r in t["limb_observations"]
        if "backslab" in r["immobilisation"].lower() and dt(r["observation_datetime"]) < applied
    ]


def check_event_ordering(t):
    """The clinical arc must run in the only order it can happen in."""
    seq = [
        ("Injury", "ED arrival"),
        ("ED arrival", "Triage"),
        ("Triage", "ED clerking"),
        ("ED clerking", "Procedure — closed reduction"),
        ("Procedure — closed reduction", "Ward transfer"),
    ]
    times = {}
    for e in t["events"]:
        times.setdefault(e["event_type"], dt(e["event_datetime"]))
    bad = []
    for earlier, later in seq:
        if earlier in times and later in times and times[earlier] >= times[later]:
            bad.append(f"{earlier} ({times[earlier]}) not before {later} ({times[later]})")
    # Imaging must precede its own report.
    for kind in ["", "check "]:
        img = [e for e in t["events"] if e["event_type"].startswith(f"Imaging — {kind}X-ray") or (kind and "check X-ray" in e["event_type"])]
        if img:
            reports = sorted(dt(e["event_datetime"]) for e in t["events"] if e["event_type"] == "Radiology report")
            if reports and dt(img[0]["event_datetime"]) > reports[-1]:
                bad.append("an X-ray is timestamped after the last radiology report")
    return bad


def check_all_within_encounter(t):
    """One clock: every timestamp in every file sits inside the encounter window."""
    start = dt(t["patient"][0]["injury_datetime"])
    end = start + timedelta(days=1, hours=1)
    bad = []
    for table, key in [
        ("observations", "observation_datetime"),
        ("limb_observations", "observation_datetime"),
        ("labs", "collected_datetime"),
        ("medication_administrations", "administration_datetime"),
        ("events", "event_datetime"),
        ("clinical_notes", "note_datetime"),
    ]:
        for r in t[table]:
            if not start <= dt(r[key]) <= end:
                bad.append(f"{table} {r[key]} outside encounter window {start} to {end}")
    return bad


# --- Level 2: notes against the structured tables --------------------------------

VITAL_PATTERNS = [
    (r"\bRR (\d{1,2})\b", "respiratory_rate_per_min"),
    (r"\bSpO2 (\d{2,3})\s?%", "spo2_percent"),
    (r"\bHR (\d{2,3})\b", "pulse_bpm"),
    (r"\bBP (\d{2,3})/(\d{2,3})\b", "bp"),
    (r"\bNEWS2\s*=?\s*(\d)\b", "news2_total"),
    (r"\bpain (?:score )?(\d{1,2})/10\b", "pain_score_0_10"),
    (r"\bTemp?\.? (\d{2}\.\d)", "temperature_c"),
]

LAB_PATTERNS = [
    (r"\bHb (\d{2,3})\b", "Haemoglobin"),
    (r"\bWCC (\d{1,2}\.\d)\b", "White cell count"),
    (r"\bPlt (\d{2,3})\b", "Platelets"),
    (r"\bNa (\d{3})\b", "Sodium"),
    (r"\bK (\d\.\d)\b", "Potassium"),
    (r"\bUrea (\d\.\d)\b", "Urea"),
    (r"\bCr (\d{2,3})\b", "Creatinine"),
    (r"\beGFR (\d{2,3})\b", "eGFR"),
    (r"\bCRP (\d{1,2}\.\d)\b", "C-reactive protein"),
    (r"\bINR (\d\.\d)\b", "INR"),
    (r"[Vv]it(?:amin)? D (\d{2,3})\b", "Vitamin D (25-OH)"),
    (r"\bALP (\d{2,3})\b", "Alkaline phosphatase"),
]


def check_notes_quote_real_vitals(t):
    """Every vital sign quoted in prose must be a value that exists in observations.csv."""
    allowed = {}
    for field in ["respiratory_rate_per_min", "spo2_percent", "pulse_bpm", "news2_total", "pain_score_0_10"]:
        allowed[field] = {r[field] for r in t["observations"]}
    allowed["temperature_c"] = {r["temperature_c"] for r in t["observations"]}
    allowed["bp"] = {(r["systolic_bp_mmhg"], r["diastolic_bp_mmhg"]) for r in t["observations"]}

    bad = []
    for note in t["clinical_notes"]:
        for pattern, field in VITAL_PATTERNS:
            for m in re.finditer(pattern, note["note_text"]):
                value = (m.group(1), m.group(2)) if field == "bp" else m.group(1)
                if field == "temperature_c":
                    value = f"{float(value):.1f}"
                if value not in allowed[field]:
                    bad.append(f"{note['note_id']} quotes {field}={value}, not in observations.csv")
    return bad


def check_notes_quote_real_labs(t):
    values = {r["test_name"]: str(r["value"]) for r in t["labs"]}
    bad = []
    for note in t["clinical_notes"]:
        for pattern, test in LAB_PATTERNS:
            for m in re.finditer(pattern, note["note_text"]):
                if test in values and m.group(1) != values[test]:
                    bad.append(f"{note['note_id']} quotes {test}={m.group(1)}, table says {values[test]}")
    return bad


def check_notes_no_future_times(t):
    """A note may not cite a clock time later than its own timestamp on the same day."""
    bad = []
    for note in t["clinical_notes"]:
        ts = dt(note["note_datetime"])
        for m in re.finditer(r"\b([0-2]\d):([0-5]\d)\b", note["note_text"]):
            h, mi = int(m.group(1)), int(m.group(2))
            if h > 23:
                continue
            cited = ts.replace(hour=h, minute=mi)
            # Times before 09:00 on a note written after midnight refer to the same night.
            if cited > ts + timedelta(minutes=1):
                bad.append(f"{note['note_id']} ({ts:%d/%m %H:%M}) cites {m.group(0)}")
    return bad


def check_notes_no_unreported_imaging(t):
    """The post-reduction measurements may not appear before the report was issued."""
    report_times = sorted(dt(e["event_datetime"]) for e in t["events"] if e["event_type"] == "Radiology report")
    second_report = report_times[1] if len(report_times) > 1 else None
    if not second_report:
        return []
    bad = []
    for note in t["clinical_notes"]:
        if dt(note["note_datetime"]) < second_report and re.search(r"12\s?(?:degrees|°)|2\s?mm", note["note_text"]):
            bad.append(f"{note['note_id']} cites post-reduction measurements before the {second_report:%H:%M} report")
    return bad


def check_notes_side_consistent(t):
    """The uninjured side may be mentioned — it is the working hand — but never as the
    fractured, casted or reduced one."""
    injured = t["patient"][0]["injured_side"].lower()
    other = "right" if injured == "left" else "left"
    injury_words = r"(fracture|#|distal radius|backslab|cast|plaster|reduction|deformity|injur\w+)"
    bad = []
    for n in t["clinical_notes"]:
        for m in re.finditer(rf"\b{other}\b[^.\n]{{0,40}}?{injury_words}", n["note_text"], re.I):
            bad.append(f"{n['note_id']} attributes '{m.group(0).strip()}' to the uninjured {other} side")
    return bad


def check_notes_author_consistent(t):
    """The author named in the signature is the one on the record."""
    return [
        f"{n['note_id']} signature does not contain {n['author_name']}"
        for n in t["clinical_notes"]
        if n["author_name"] not in n["note_text"]
    ]


def check_labels_agree_with_tables(t):
    label = {r["label_name"]: r["label_value"] for r in t["labels"]}
    bad = []
    peak = max(int(r["pain_score_0_10"]) for r in t["observations"])
    if label["peak_pain_score_day1"] != str(peak):
        bad.append(f"peak_pain_score_day1 {label['peak_pain_score_day1']} vs observations max {peak}")
    news = max(int(r["news2_total"]) for r in t["observations"])
    if label["max_news2_day1"] != str(news):
        bad.append(f"max_news2_day1 {label['max_news2_day1']} vs observations max {news}")
    opioid = any("morphine" in r["medication"].lower() for r in t["medication_administrations"])
    if label["opioid_administered_day1"] != str(opioid):
        bad.append(f"opioid_administered_day1 {label['opioid_administered_day1']} vs medication table {opioid}")
    vte = any("enoxaparin" in r["medication"].lower() for r in t["medication_administrations"])
    if label["vte_prophylaxis_given_day1"] != str(vte):
        bad.append(f"vte_prophylaxis_given_day1 {label['vte_prophylaxis_given_day1']} vs medication table {vte}")
    if label["injured_side"] != t["patient"][0]["injured_side"]:
        bad.append("injured_side label disagrees with patient.csv")
    return bad


RULES = [
    ("R01", 3, "Vital signs within physiologically possible ranges", check_physiological_ranges),
    ("R02", 3, "NEWS2 recomputed from the recorded vitals matches the recorded score", check_news2_recomputed),
    ("R03", 3, "Systolic BP exceeds diastolic", check_bp_ordering),
    ("R04", 3, "eGFR consistent with creatinine, age and sex (CKD-EPI 2021)", check_egfr_creatinine),
    ("R05", 3, "Abnormal flags agree with the stated reference ranges", check_lab_flags),
    ("R06", 3, "No drug given that the recorded allergy contraindicates", check_allergy_respected),
    ("R07", 3, "Every regular medicine has a condition on the record that justifies it", check_med_has_indication),
    ("R08", 3, "Paracetamol dosing interval >=4h and <=4 g/24h", check_paracetamol_dosing),
    ("R09", 3, "Oral morphine dose age-appropriate", check_opioid_dose_for_age),
    ("R10", 3, "Nothing given orally after nil-by-mouth started", check_nbm_respected),
    ("R11", 3, "Limb in plaster remains perfused; compartment syndrome label agrees", check_limb_perfusion),
    ("R12", 3, "No backslab recorded before it was applied", check_cast_before_limb_obs),
    ("R13", 3, "Clinical events occur in a possible order", check_event_ordering),
    ("R14", 2, "One clock: every timestamp inside the encounter window", check_all_within_encounter),
    ("R15", 2, "Vitals quoted in notes exist in observations.csv", check_notes_quote_real_vitals),
    ("R16", 2, "Lab values quoted in notes match labs.csv", check_notes_quote_real_labs),
    ("R17", 2, "No note cites a clock time later than its own timestamp", check_notes_no_future_times),
    ("R18", 2, "No note cites imaging measurements before the report was issued", check_notes_no_unreported_imaging),
    ("R19", 2, "No note attributes the injury to the uninjured side", check_notes_side_consistent),
    ("R20", 2, "Note signature matches the recorded author", check_notes_author_consistent),
    ("R21", 2, "Derived labels agree with the tables they were derived from", check_labels_agree_with_tables),
]


def main(data_dir):
    d = Path(data_dir)
    tables = {p.stem: load(d, p.name) for p in d.glob("*.csv")}

    failed = 0
    for rule_id, level, description, check in RULES:
        offenders = check(tables)
        status = "PASS" if not offenders else "FAIL"
        failed += bool(offenders)
        print(f"{rule_id}  L{level}  {status}  {description}")
        for o in offenders:
            print(f"          - {o}")
    print(f"\n{len(RULES) - failed}/{len(RULES)} rules passed.")
    return failed


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1] if len(sys.argv) > 1 else "data/broken_arm_day1") else 0)
