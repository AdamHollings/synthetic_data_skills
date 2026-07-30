"""Generate the demographics-only patient table in data/patients.csv.

Seeding case: from intelligence (no real seed data). The cohort definition below is the
specification; see data/REPORT.md.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

MASTER_SEED = 20260729
REFERENCE_DATE = date(2026, 7, 29)
OUT = Path(__file__).resolve().parents[1] / "data" / "patients.csv"

# One patient per band, so 10 rows actually span the age range instead of clustering.
AGE_BANDS = [(0, 4), (5, 14), (15, 24), (25, 34), (35, 44),
             (45, 54), (55, 64), (65, 74), (75, 84), (85, 95)]

# Name locales, weighted towards en_GB. Assumed proportions - not fitted to any published
# population statistic. Addresses are always en_GB: every patient lives in the UK.
NAME_LOCALES = ["en_GB", "en_GB", "en_GB", "en_GB", "en_IN", "bn_BD", "pl_PL", "en_NG",
                "it_IT", "ar_AA"]


def patient_state(index):
    """Sample one patient's state. Seed is derived from the patient index."""
    rng = random.Random(MASTER_SEED + index)
    low, high = AGE_BANDS[index]
    age = rng.randint(low, high)
    dob = REFERENCE_DATE - timedelta(days=age * 365 + rng.randint(0, 364))
    return {
        "patient_id": f"P{index + 1:03d}",
        "sex": rng.choice(["female", "male"]),
        "date_of_birth": dob,
        "name_locale": NAME_LOCALES[index],
    }


def main():
    rows = []
    for index in range(len(AGE_BANDS)):
        state = patient_state(index)
        names = Faker(state["name_locale"])
        address = Faker("en_GB")
        names.seed_instance(MASTER_SEED + index)
        address.seed_instance(MASTER_SEED + index)

        # first + last rather than name(), which prefixes titles ("Dr", "Mr") that Faker
        # will happily attach to a 3-year-old.
        first = names.first_name_female() if state["sex"] == "female" else names.first_name_male()
        name = f"{first} {names.last_name()}"
        rows.append({
            "patient_id": state["patient_id"],
            "name": name,
            "address": address.address().replace("\n", ", "),
            "date_of_birth": state["date_of_birth"].isoformat(),
        })

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["patient_id", "name", "address", "date_of_birth"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
