"""Create a Markdown summary and dependency-free SVG figure."""

import argparse
from html import escape
from pathlib import Path

import pandas as pd


def write_svg(site_summary, output_path):
    width, height = 720, 440
    left, top, plot_width, plot_height = 90, 45, 570, 300
    maximum = max(site_summary["mean"].max(), 1)
    bar_width = 100
    gap = (plot_width - bar_width * len(site_summary)) / (len(site_summary) + 1)
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#24292f}.title{font-size:22px;font-weight:700}.axis{font-size:13px}.value{font-size:13px;font-weight:700}</style>',
        '<text x="360" y="28" text-anchor="middle" class="title">Mean glucose by enrollment site</text>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#57606a"/>',
        f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#57606a"/>',
    ]
    for tick in range(0, int(maximum // 500 + 2) * 500, 500):
        y = top + plot_height - (tick / maximum) * plot_height
        if y < top:
            continue
        elements.extend([
            f'<line x1="{left - 5}" y1="{y:.1f}" x2="{left + plot_width}" y2="{y:.1f}" stroke="#d8dee4"/>',
            f'<text x="{left - 10}" y="{y + 5:.1f}" text-anchor="end" class="axis">{tick}</text>',
        ])
    colors = ["#2f81f7", "#3fb950", "#d29922"]
    for index, row in enumerate(site_summary.itertuples(index=False)):
        x = left + gap + index * (bar_width + gap)
        bar_height = row.mean / maximum * plot_height
        y = top + plot_height - bar_height
        elements.extend([
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width}" height="{bar_height:.1f}" rx="4" fill="{colors[index]}"/>',
            f'<text x="{x + bar_width / 2:.1f}" y="{y - 8:.1f}" text-anchor="middle" class="value">{row.mean:.1f}</text>',
            f'<text x="{x + bar_width / 2:.1f}" y="{top + plot_height + 24}" text-anchor="middle" class="axis">{escape(row.enrollment_site)}</text>',
            f'<text x="{x + bar_width / 2:.1f}" y="{top + plot_height + 43}" text-anchor="middle" class="axis">n={row.count}</text>',
        ])
    elements.append('<text transform="translate(22 240) rotate(-90)" text-anchor="middle" class="axis">Glucose (mg/dL)</text>')
    elements.append('</svg>')
    output_path.write_text("\n".join(elements) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--figure", required=True, type=Path)
    args = parser.parse_args()

    data = pd.read_csv(args.input, na_values=["NA"])
    site_summary = (
        data.groupby("enrollment_site", as_index=False)["glucose_mg_dl"]
        .agg(["count", "mean", "median"])
        .reset_index()
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.figure.parent.mkdir(parents=True, exist_ok=True)
    write_svg(site_summary, args.figure)

    context_columns = [column for column in data if column.startswith("cohort_")]
    context = data.iloc[0][context_columns]
    lines = [
        "# Lab 5 workflow summary",
        "",
        "## Inputs and analytic grain",
        "",
        f"The combined table contains **{len(data)} synthetic sample rows**. "
        f"Glucose is missing for **{data['glucose_mg_dl'].isna().sum()}** samples.",
        "",
        "The Lab 3 samples and Lab 4 TCGA patients have no shared identifier. "
        "The workflow therefore merges a one-row summary of the 566-patient cohort "
        "onto each synthetic sample. It does not assert patient-level linkage.",
        "",
        "## Sample glucose summary",
        "",
        "| Enrollment site | Non-missing n | Mean (mg/dL) | Median (mg/dL) |",
        "|---|---:|---:|---:|",
    ]
    for row in site_summary.itertuples(index=False):
        lines.append(
            f"| {row.enrollment_site} | {row.count} | {row.mean:.1f} | {row.median:.1f} |"
        )
    lines.extend([
        "",
        "![Mean glucose by enrollment site](glucose_by_site.svg)",
        "",
        "## Lab 4 cohort context",
        "",
        f"- Patients: {int(context['cohort_patient_count'])}",
        f"- Median age at diagnosis: {context['cohort_median_age_at_diagnosis']:.1f} years",
        f"- Mean nonsynonymous TMB: {context['cohort_mean_tmb_nonsynonymous']:.2f}",
        "",
        "Proportion of patients with at least one protein-altering mutation:",
        "",
        "| Gene | Proportion |",
        "|---|---:|",
    ])
    for gene in ["tp53", "kras", "egfr", "stk11", "keap1"]:
        lines.append(f"| {gene.upper()} | {context[f'cohort_{gene}_mutated_proportion']:.3f} |")
    lines.extend([
        "",
        "## Interpretation caution",
        "",
        "The synthetic glucose records and TCGA LUAD cohort describe different, "
        "unlinked populations. Cohort values are contextual summaries only and "
        "must not be used to infer associations with individual sample glucose values.",
    ])
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote report {args.report} and figure {args.figure}")


if __name__ == "__main__":
    main()
