# AI Usage Disclosure

## Tool used

I used OpenAI Codex in the Codex desktop app with the GPT-5.6 Sol model, on November 10, 2026. I used it interactively while adapting my Lab 3 and Lab 4 work into a Snakemake workflow.

## Assistance received

Codex helped me:

- plan the four-stage DAG and write Snakemake rule syntax;
- declare the raw data, SQL files, and Python scripts as rule inputs;
- adapt the Lab 3 regex cleaner to command-line input and output paths;
- adapt the Lab 4 SQL and pandas reshape into a workflow stage;
- recognize that the two source datasets have no valid patient-level join key;
- implement and document a cohort-summary merge that avoids inventing links;
- generate a Markdown summary report and SVG figure;
- write validation checks for row counts, uniqueness, and merge grain;
- test a full clean run and a selective downstream re-run; and
- draft the reproducibility instructions and this disclosure.

## Human decisions and verification

I reviewed the workflow structure, source-data limitation, and final outputs.
The workflow was executed from a clean output state with two cores. That run
completed all four analysis rules plus the `all` target. I then made a temporary
content change to the Lab 3 raw input and verified that only `clean_samples`,
`merge_analytic_tables`, `summary_report`, and `all` ran; the independent
database query did not run.

I restored the original raw input after the test and regenerated the final
outputs. The complete console evidence is saved in `evidence/full_run.log` and
`evidence/partial_rerun.log`.

I also checked that the final outputs contain 60 unique sample rows, the
intermediate patient table contains 566 unique patient rows, and the report
describes the lack of patient-level linkage rather than presenting the two
datasets as matched.

After completing the lab, I asked Codex to create a review quiz covering what I had done so I could check my understanding.
