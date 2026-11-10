"""Combine samples with aggregate context from the unrelated patient cohort."""

import argparse
from pathlib import Path

import pandas as pd


GENES = ["tp53", "kras", "egfr", "stk11", "keap1"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", required=True, type=Path)
    parser.add_argument("--patients", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    samples = pd.read_csv(args.samples)
    patients = pd.read_csv(args.patients, na_values=["NA"])
    if len(samples) != 60 or samples["sample_id"].nunique() != 60:
        raise ValueError("clean samples table must contain 60 unique samples")
    if len(patients) != 566 or patients["patient_id"].nunique() != 566:
        raise ValueError("patient feature table must contain 566 unique patients")

    context = {
        "cohort_patient_count": len(patients),
        "cohort_median_age_at_diagnosis": patients["age_at_diagnosis"].median(),
        "cohort_mean_tmb_nonsynonymous": patients["tmb_nonsynonymous"].mean(),
    }
    for gene in GENES:
        column = f"{gene}_protein_altering_count"
        context[f"cohort_{gene}_mutated_proportion"] = patients[column].gt(0).mean()

    # These datasets have no shared identifier. A one-row cohort summary is the
    # only valid join target; patient records are never paired to synthetic samples.
    combined = samples.assign(_join_key=1).merge(
        pd.DataFrame([context]).assign(_join_key=1), on="_join_key", validate="many_to_one"
    ).drop(columns="_join_key")
    if len(combined) != len(samples):
        raise ValueError("merge changed the sample-level grain")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(args.output, index=False, na_rep="NA")
    print(f"Merged {len(samples)} samples with context from {len(patients)} patients")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
