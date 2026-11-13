# Theme keyword counts

`themes.json` contains ten researcher-selected subject themes, provisional
review definitions, and AI-assisted search patterns. This is a pilot search
dictionary, not a validated scholarly coding scheme. No policy-mechanism
framework has been implemented.

## Create the CSV

From the repository root:

```powershell
python -B src/code_themes.py
```

The script reads saved texts under `output/staging/2025/` and creates
`output/coding/theme_counts.csv` directly. It uses only the Python standard
library, makes no network requests, and does not modify source texts.

Each row identifies a statute by state, dataset year, and bill number. State codes
repeat on every row. Each theme has two columns:

| Column | Meaning |
| --- | --- |
| Full theme name | `1` if at least one keyword match was found; `0` if none were found. |
| Theme name followed by `No. mentions` | Number of non-overlapping keyword matches within that theme. |

These indicators are automatic search results, not reviewed presence decisions.
Searches include all available saved bills, without the earlier exploratory
analysis's exclusions. Missing texts, such as Puerto Rico HJR68, do not get rows
and must be accounted for separately.

## Interpret the counts

Searches cover the full statutory body, excluding retrieval metadata, legislative
history, and explicitly marked deletions. Explicit additions are retained.
Line-break hyphenation and whitespace are normalized. PDF layout problems,
unmarked deletions, explanatory comments, and prior-law comparisons are not resolved.

Terms can occur in unrelated sections of large bills. Repeated matches do not
count distinct provisions or new duties, and overlapping themes should not be
summed as independent findings. Zero matches do not establish that a theme is
absent. Human reading is needed before assigning substantive codes.
These totals do not reproduce the earlier focused-passage analysis.

## Regenerate safely

Existing outputs are never overwritten. Choose a new filename for another run:

```powershell
python -B src/code_themes.py --output output/coding/theme_counts_pilot2.csv
```

Use `--statutes` or `--codebook` to choose other inputs. Relative paths resolve
from the current working directory. Change the codebook version when revising
its definitions or patterns, and retain the matching codebook with research results.
Generated outputs under `output/coding/` are ignored by Git.

## Formatted Excel workbook

For bordered tables, shaded headers, frozen identifier columns, and a chart:

```powershell
python -m pip install openpyxl
python -B src/export_theme_workbook.py
```

This reads `theme_counts.csv` and creates `output/coding/theme_counts.xlsx`.
It includes an overview chart, a combined table, and ten individual theme tabs.
The CSV is unchanged. The exporter refuses to replace an existing workbook;
use `--output` for a new filename. Only the Excel exporter requires `openpyxl`.
