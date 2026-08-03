"""Extraction smoke test — the utility substitute where TSTR cannot run.

Asks a model to extract the labelled facts from the notes alone, and compares the answer
against labels.csv, which was written before the notes existed.

This is NOT a utility result. It establishes only that the labelled facts are present and
readable in the prose. Both the notes and the extraction come from the same model, so a
high score partly measures a model reading its own output — the label-validity trap. Read
it as "the dataset supports the task at all", nothing stronger.

Run:  .venv/Scripts/python.exe scripts/extraction_smoke_test.py data/broken_arm_day1
"""

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from call_llm import call_llm

MODEL = "ri.language-model-service..language-model.gpt-5-1"

FIELDS = {
    "fracture_site": "the bone and side fractured",
    "fracture_pattern": "the fracture pattern",
    "open_fracture": "true or false",
    "comminution": "extent of comminution",
    "intra_articular_extension": "true or false",
    "median_nerve_paraesthesia_at_presentation": "true or false, at first presentation",
    "paraesthesia_resolved_after_reduction": "true or false",
    "closed_reduction_performed": "true or false",
    "reduction_adequate": "true or false — was the reduction good enough to avoid surgery",
    "admitted": "true or false",
    "planned_operation": "the operation planned",
    "peak_pain_score_day1": "highest pain score out of 10 recorded",
    "max_news2_day1": "highest NEWS2 score recorded",
    "vte_prophylaxis_given_day1": "true or false",
    "opioid_administered_day1": "true or false",
}


def main(data_dir):
    d = Path(data_dir)
    with open(d / "clinical_notes.csv", encoding="utf-8") as f:
        notes = list(csv.DictReader(f))
    with open(d / "labels.csv", encoding="utf-8") as f:
        truth = {r["label_name"]: r["label_value"] for r in csv.DictReader(f)}

    record = "\n\n".join(
        f"=== {n['note_id']} | {n['note_datetime']} | {n['note_type']} ===\n{n['note_text']}" for n in notes
    )
    schema = "\n".join(f'  "{k}": <{v}>' for k, v in FIELDS.items())
    prompt = (
        "Below is the complete free-text record for one hospital patient's first day. "
        "Read it and extract the following fields. Answer only from the notes. "
        "Return a single JSON object and nothing else.\n\n"
        f"{{\n{schema}\n}}\n\n{record}"
    )

    raw = call_llm(prompt, model=MODEL, temp=0)
    if raw is None:
        sys.exit("LLM call failed.")
    m = re.search(r"\{.*\}", raw, re.S)
    extracted = json.loads(m.group(0))

    print(f"{'field':<45} {'ground truth':<38} {'extracted'}")
    print("-" * 120)
    agree = 0
    for k in FIELDS:
        got = str(extracted.get(k, "<missing>"))
        exp = truth.get(k, "<no label>")
        match = got.strip().lower().rstrip(".") == exp.strip().lower().rstrip(".")
        agree += match
        print(f"{'OK ' if match else '?? '}{k:<42} {exp:<38} {got}")
    print(f"\n{agree}/{len(FIELDS)} exact string matches (non-matches may still be semantically correct — read them).")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/broken_arm_day1")
