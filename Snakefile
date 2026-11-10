"""Snakemake workflow for PUBH 6854 Lab 5."""

import sys


PYTHON = sys.executable

rule all:
    input:
        "results/combined_analytic_table.csv",
        "report/summary.md",
        "report/glucose_by_site.svg",


rule clean_samples:
    input:
        data="data/raw/messy_samples.csv",
        script="scripts/clean_samples.py",
    output:
        "results/clean_samples.csv",
    params:
        python=PYTHON,
    shell:
        "{params.python} {input.script} --input {input.data} --output {output}"


rule query_patient_features:
    input:
        database="data/raw/lab4-cbioportal-luad/cohort.db",
        query="sql/gene_counts.sql",
        script="scripts/query_patient_features.py",
    output:
        "results/patient_features.csv",
    params:
        python=PYTHON,
    shell:
        (
            "{params.python} {input.script} --database {input.database} "
            "--gene-query {input.query} --output {output}"
        )


rule merge_analytic_tables:
    input:
        samples="results/clean_samples.csv",
        patients="results/patient_features.csv",
        script="scripts/merge_tables.py",
    output:
        "results/combined_analytic_table.csv",
    params:
        python=PYTHON,
    shell:
        (
            "{params.python} {input.script} --samples {input.samples} "
            "--patients {input.patients} --output {output}"
        )


rule summary_report:
    input:
        table="results/combined_analytic_table.csv",
        script="scripts/make_report.py",
    output:
        report="report/summary.md",
        figure="report/glucose_by_site.svg",
    params:
        python=PYTHON,
    shell:
        (
            "{params.python} {input.script} --input {input.table} "
            "--report {output.report} --figure {output.figure}"
        )
