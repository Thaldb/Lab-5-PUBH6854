"""Query the Lab 4 SQLite database into a validated patient feature table."""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


GENES = ["TP53", "KRAS", "EGFR", "STK11", "KEAP1"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--gene-query", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    base_query = """
        SELECT p.patient_id, p.sex, p.age_at_diagnosis, p.stage,
               s.tissue_source_site, s.tmb_nonsynonymous
        FROM patients AS p
        LEFT JOIN samples AS s ON s.patient_id = p.patient_id
        ORDER BY p.patient_id
    """
    with sqlite3.connect(args.database) as connection:
        base = pd.read_sql_query(base_query, connection)
        gene_long = pd.read_sql_query(args.gene_query.read_text(), connection)

    if len(base) != 566 or base["patient_id"].nunique() != 566:
        raise ValueError("expected exactly 566 unique patients")
    if len(gene_long) != 566 * len(GENES):
        raise ValueError("unexpected number of patient-gene rows")

    gene_wide = gene_long.pivot(
        index="patient_id", columns="gene_symbol", values="protein_altering_count"
    ).reset_index()
    gene_wide.columns.name = None
    gene_wide = gene_wide.rename(
        columns={gene: f"{gene.lower()}_protein_altering_count" for gene in GENES}
    )
    features = base.merge(gene_wide, on="patient_id", validate="one_to_one")
    if len(features) != 566 or features["patient_id"].duplicated().any():
        raise ValueError("patient-level grain was not preserved")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(args.output, index=False, na_rep="NA")
    print(f"Queried {len(features)} patients -> {args.output}")


if __name__ == "__main__":
    main()
