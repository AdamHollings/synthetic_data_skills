"""Deterministic identifier scan over free text.

Substitutes for the entity-extraction stage of the PrivFingerprint pattern
(`references/privacy.md`) when a second LLM is unavailable. It answers a narrower
question than that pattern does: which direct identifiers appear in the prose, and is
each one accounted for in the structured record. It does not score how identifying the
combination is, and it does not detect memorised training content.

Run:  .venv/Scripts/python.exe scripts/text_identifier_scan.py data/broken_arm_day1
"""

import csv
import re
import sys
from pathlib import Path

PATTERNS = {
    "NHS-number-like (10 digits)": r"\b\d{3}[ -]?\d{3}[ -]?\d{4}\b",
    "UK postcode": r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b",
    "date of birth style": r"\b\d{1,2}[/-]\d{1,2}[/-](?:19|20)\d{2}\b",
    "UK phone number": r"\b0\d{3,4}\s?\d{3}\s?\d{3,4}\b",
    "email address": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
    "hospital/MRN style": r"\b(?:MRN|hospital (?:no|number))\.?[: ]\s*\w+\b",
    "person name (Title Surname)": r"\b(?:Mr|Mrs|Ms|Miss|Dr|Prof)\.? [A-Z]\w+\b",
}


def main(data_dir):
    d = Path(data_dir)
    with open(d / "clinical_notes.csv", encoding="utf-8") as f:
        notes = list(csv.DictReader(f))
    with open(d / "patient.csv", encoding="utf-8") as f:
        patient = list(csv.DictReader(f))[0]

    # Identifiers the structured record already accounts for.
    known = {patient["nhs_number"], patient["postcode"], patient["address"], patient["name"]}
    known |= set(patient["name"].split())
    known |= {n["author_name"] for n in notes}
    known |= {n["author_name"].replace("Dr ", "").replace("Mr ", "") for n in notes}

    print(f"Scanning {len(notes)} notes for direct identifiers.\n")
    total = 0
    for label, pattern in PATTERNS.items():
        hits = []
        for n in notes:
            for m in re.finditer(pattern, n["note_text"]):
                value = m.group(0)
                accounted = any(value in k or k in value for k in known if k)
                hits.append((n["note_id"], value, accounted))
        total += len(hits)
        print(f"{label}: {len(hits)} match(es)")
        for note_id, value, accounted in hits:
            status = "accounted for in patient.csv/author list" if accounted else "NOT ACCOUNTED FOR"
            print(f"    {note_id}  {value!r}  — {status}")
    # The patterns above catch identifiers with a recognisable shape; a bare personal name
    # has none, so count the known names explicitly rather than implying they were absent.
    print("\nKnown names appearing in the text (expected — they are in patient.csv):")
    for name in sorted({patient["name"]} | {n["author_name"] for n in notes}):
        count = sum(n["note_text"].count(name) for n in notes)
        if count:
            print(f"    {name!r}: {count} occurrence(s)")

    print(f"\n{total} patterned identifier-like strings found in total.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/broken_arm_day1")
