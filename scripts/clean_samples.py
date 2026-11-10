"""Clean the Lab 3 sample records with explicit regular-expression rules."""

import argparse
import csv
import re
from datetime import date, datetime
from pathlib import Path


MMOL_L_TO_MG_DL = 18.0182
OUTPUT_FIELDS = [
    "sample_id",
    "patient_name",
    "dob",
    "sex",
    "enrollment_site",
    "glucose_mg_dl",
    "glucose_status",
    "notes",
]


def clean_sample_id(raw_value):
    match = re.fullmatch(r"[Ss]-?(\d{4})", raw_value.strip())
    if not match:
        raise ValueError(f"unrecognized sample ID: {raw_value!r}")
    return f"S{int(match.group(1)):04d}"


def clean_date(raw_value):
    value = raw_value.strip()
    patterns = [
        (r"\d{2}/\d{2}/\d{4}", "%m/%d/%Y"),
        (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
        (r"\d{2}-[A-Za-z]{3}-\d{4}", "%d-%b-%Y"),
    ]
    for regex, date_format in patterns:
        if re.fullmatch(regex, value):
            return datetime.strptime(value, date_format).date().isoformat()

    match = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{2})", value)
    if match:
        month, day, short_year = map(int, match.groups())
        year = 2000 + short_year if short_year <= 26 else 1900 + short_year
        return date(year, month, day).isoformat()
    raise ValueError(f"unrecognized date: {raw_value!r}")


def clean_sex(raw_value):
    value = raw_value.strip().lower()
    if re.fullmatch(r"m|male", value):
        return "Male"
    if re.fullmatch(r"f|female", value):
        return "Female"
    if re.fullmatch(r"u|unknown|", value):
        return "Unknown"
    raise ValueError(f"unrecognized sex value: {raw_value!r}")


def clean_site(raw_value):
    compact = re.sub(r"[\s_-]+", "", raw_value).lower()
    match = re.fullmatch(r"site([abc])", compact)
    if not match:
        raise ValueError(f"unrecognized site: {raw_value!r}")
    return f"Site {match.group(1).upper()}"


def clean_glucose(raw_value, raw_unit):
    value = raw_value.strip()
    unit = re.sub(r"\s+", "", raw_unit).lower()
    if re.fullmatch(r"n/?a", value, flags=re.IGNORECASE):
        return "", "missing"
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(\*)?", value)
    if not match:
        raise ValueError(f"unrecognized glucose value: {raw_value!r}")
    glucose = float(match.group(1))
    status = "annotated" if match.group(2) else "reported"
    if unit == "mmol/l":
        glucose *= MMOL_L_TO_MG_DL
    elif unit != "mg/dl":
        raise ValueError(f"unrecognized glucose unit: {raw_unit!r}")
    return f"{glucose:.1f}", status


def clean_row(row):
    glucose, status = clean_glucose(row["glucose_value"], row["glucose_unit"])
    return {
        "sample_id": clean_sample_id(row["sample_id"]),
        "patient_name": row["patient_name"].strip().title(),
        "dob": clean_date(row["dob"]),
        "sex": clean_sex(row["sex"]),
        "enrollment_site": clean_site(row["enrollment_site"]),
        "glucose_mg_dl": glucose,
        "glucose_status": status,
        "notes": row["notes"].strip(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with args.input.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        rows = []
        for line_number, row in enumerate(reader, start=2):
            try:
                rows.append(clean_row(row))
            except ValueError as error:
                raise ValueError(f"input line {line_number}: {error}") from error

    if len(rows) != 60 or len({row["sample_id"] for row in rows}) != 60:
        raise ValueError("expected 60 rows with 60 unique sample IDs")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Cleaned {len(rows)} samples -> {args.output}")


if __name__ == "__main__":
    main()
