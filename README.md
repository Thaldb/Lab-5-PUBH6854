# PUBH 6854 Lab 5: Scalable Analysis Workflow

## Project overview

This repository turns work from Labs 3 and 4 into a reproducible Snakemake
workflow. The directed acyclic graph (DAG) cleans messy sample records and
queries a SQLite cohort in parallel, combines their outputs, and produces a
Markdown report with an SVG figure.

## Workflow DAG

```text
messy_samples.csv + clean_samples.py
                └──> clean_samples.csv ──────────────┐
                                                     ├──> combined_analytic_table.csv
cohort.db + gene_counts.sql + query script           │                │
                └──> patient_features.csv ───────────┘                └──> summary.md
                                                                          glucose_by_site.svg
```

Every data, code, and SQL dependency used by a rule is declared in its
`input:` section. The final `all` rule declares the combined table, report,
and figure as workflow targets.

| Rule | Purpose | Main output |
|---|---|---|
| `clean_samples` | Reuse Lab 3 regex rules to normalize 60 records | `results/clean_samples.csv` |
| `query_patient_features` | Reuse Lab 4 SQL to build one row per TCGA patient | `results/patient_features.csv` |
| `merge_analytic_tables` | Add valid cohort-level context to each synthetic sample | `results/combined_analytic_table.csv` |
| `summary_report` | Summarize the combined table and draw a figure | `report/summary.md`, `report/glucose_by_site.svg` |

## Important integration decision

The synthetic Lab 3 samples and TCGA LUAD patients do not share an identifier
and do not represent the same population. Pairing rows by position or inventing
a join key would create false patient links. The merge stage therefore reduces
the 566-patient feature table to one cohort-context row (patient count, median
age, mean tumor mutation burden, and mutation prevalence for five genes) and
performs a validated many-to-one cross join onto the 60 synthetic samples.

The final table remains at the sample grain. Cohort columns are contextual
summaries only; they cannot be used to infer patient-level associations with
glucose.

## Repository structure

```text
.
├── Snakefile
├── environment.yml
├── README.md
├── AI_USAGE.md
├── data/raw/
│   ├── messy_samples.csv
│   └── lab4-cbioportal-luad/cohort.db
├── scripts/
│   ├── clean_samples.py
│   ├── query_patient_features.py
│   ├── merge_tables.py
│   └── make_report.py
├── sql/gene_counts.sql
├── results/
│   ├── clean_samples.csv
│   ├── patient_features.csv
│   └── combined_analytic_table.csv
├── report/
│   ├── summary.md
│   └── glucose_by_site.svg
└── evidence/
    ├── full_run.log
    └── partial_rerun.log
```

## Setup

From the repository root, create and activate the environment:

```bash
conda env create -f environment.yml
conda activate pubh6854-lab5
```

## Full clean run

Delete only workflow-generated outputs, then rebuild the entire DAG with two
cores:

```bash
snakemake --delete-all-output --cores 1
snakemake --cores 2 --printshellcmds
```

The first command removes outputs known to Snakemake while preserving raw data,
scripts, SQL, and evidence. The second command runs the independent cleaning and
database-query stages concurrently when two cores are available. A successful
run ends with `5 of 5 steps (100%) done`. The captured console output is in
`evidence/full_run.log`.

To preview planned jobs without changing files, run:

```bash
snakemake --dry-run --printshellcmds
```

## Partial re-run

To test incremental execution, make a harmless content change to an upstream
Lab 3 field—for example, add a note to the final CSV record—then rerun:

```bash
snakemake --cores 2 --printshellcmds
```

Snakemake runs only:

1. `clean_samples`
2. `merge_analytic_tables`
3. `summary_report`
4. the bookkeeping `all` target

It does **not** run `query_patient_features`, because neither `cohort.db`, the
SQL, nor the query script changed. `evidence/partial_rerun.log` records this
test. The temporary note used for the demonstration was removed afterward and
the final outputs were regenerated from the original raw data.

Current Snakemake versions compare file content, so changing only a timestamp
with `touch` may correctly result in “Nothing to be done.” Use a real content
change for this demonstration.

## Validation and outputs

The scripts fail with an error if expected table grain changes:

- cleaned samples: 60 rows and 60 unique sample IDs;
- patient features: 566 rows and 566 unique patient IDs;
- patient-gene query: 2,830 rows (566 patients × 5 genes);
- combined table: 60 sample-level rows after the many-to-one merge.

The final deliverables are:

- `results/combined_analytic_table.csv`
- `report/summary.md`
- `report/glucose_by_site.svg`

## Data provenance

- `messy_samples.csv` is the course-provided synthetic input reused from Lab 3.
- `cohort.db` is the course-provided TCGA LUAD-derived SQLite database reused
  from Lab 4. It contains de-identified patient, sample, mutation, and gene
  tables.
- The workflow does not modify either raw input.

AI assistance used to develop and verify the workflow is documented in
[`AI_USAGE.md`](AI_USAGE.md).
