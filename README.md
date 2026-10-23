# Baker-Thesis

A research collection of U.S. state legislation related to artificial intelligence,
with Python tools for parsing the source bill list, retrieving legislative text,
and checking the saved file inventory.

The collection starts with an NCSL export containing **192 records**. There are
**191 saved legislative texts in 44 state folders**. The historical unresolved list
contains one record: Puerto Rico HJR68, which could not be retrieved because its
session response was missing from the local cache.

## Repository contents

| Location | Contents |
| --- | --- |
| [src/read_ncsl.py](src/read_ncsl.py) | Parses the saved NCSL text export into a CSV bill list. |
| [src/legiscan.py](src/legiscan.py) | Matches bills through LegiScan and saves legislative text with source metadata and review notes. |
| [src/inventory.py](src/inventory.py) | Checks saved statute filenames and creates inventory and review CSVs. |
| [data/ncsl](data/ncsl) | Original NCSL PDF and text export, parsed bill list, and reviewed bill/document selections. |
| [output/staging/2025](output/staging/2025) | Saved legislative texts, organized by state. |
| [output/staging/retrieved.csv](output/staging/retrieved.csv) | Historical list of retrieved records and associated review notes. |
| [output/staging/unresolved.csv](output/staging/unresolved.csv) | Historical list of unresolved records. |
| [output/staging/reports](output/staging/reports) | Timestamped retrieval reports and a [summary of earlier runs](output/staging/reports/full-run-summary.md). |

The `2025` folder follows the NCSL dataset grouping. Some records refer to earlier
sessions or enactment dates; the saved metadata and review notes explain these
cases. The repository currently contains retrieval tools and source material;
a theme-analysis script and theme research report are not included.

## Requirements

- Python 3.9 or later. All three scripts use only the standard library; no Python
  packages or compilation are required.
- A LegiScan API key for online retrieval, stored in a UTF-8 `.env` file at the
  repository root:

  ```dotenv
  LEGISCAN_API_KEY=your-key
  ```

- For PDF conversion, the importer expects the Windows Xpdf executable at
  `tools/xpdf-tools-win-4.06/bin64/pdftotext.exe`. This distribution is not tracked
  by Git. The executable is required when processing a PDF, including offline.

Run all commands from the repository root. The parser and inventory do not need
an API key. Offline retrieval also does not need a key, but requires locally cached
responses and any supporting official documents. Those files are excluded from
Git, so a fresh clone does not contain everything needed for an offline run.

## Retrieve legislative text

The importer reads the existing `data/ncsl/ncsl_bills.csv`. To process one record:

```powershell
python -B src/legiscan.py --candidate CO_2025_SB4
```

Other available commands:

```powershell
# Process the example record: Alabama HB365.
python -B src/legiscan.py --example

# Process all records using only local cached responses.
python -B src/legiscan.py --offline

# Refresh session, master-list, and bill metadata from LegiScan.
python -B src/legiscan.py --refresh

# Process all records, reusing cached responses when applicable.
python -B src/legiscan.py

# Show command-line options.
python -B src/legiscan.py --help
```

`--offline` and `--refresh` cannot be combined. Either can be combined with
`--candidate` or `--example` to limit the run. Online requests are paced, and
rate-limit responses are retried up to twice.

The importer verifies bill identity and session, checks change hashes, and prefers
chaptered or enacted text over enrolled text. Reviewed selections in
`data/ncsl/legiscan_resolutions.json` resolve ambiguous identities or document
versions and can specify an official source when final API text is unavailable.
They still undergo identity and document checks.

**The current Python importer accepts PDF and UTF-8 plain text.** Some saved texts
and historical reports came from earlier workflows that also converted HTML.
HTML conversion is not implemented in the current scripts, so they cannot
reproduce every historical retrieval from scratch.

### Retrieval outputs

- Legislative text: `output/staging/<year>/<state>/<filename>.txt`.
- API response snapshots: `output/staging/cache/` (ignored by Git).
- Source documents and extracted PDF text: `output/staging/documents/` (ignored by Git).
- A new JSON run report: `output/staging/reports/`.

Each newly saved text includes source metadata, legislative history, the selected
text version, and review notes. Existing statute files are preserved rather than
replaced. A rerun can still update cached metadata and write a new run report.

The importer does **not** regenerate `retrieved.csv`, `unresolved.csv`, or the
historical summary. Use the new JSON report to assess a new run.

| Exit code | Meaning |
| --- | --- |
| `0` | Every selected record was staged or an existing file was preserved. Review notes may still remain. |
| `2` | Some selected records remain unresolved, or the selection was empty. |
| `1` | A startup or top-level error prevented completion. |

## Rebuild the NCSL bill list

```powershell
python -B src/read_ncsl.py
```

This reads `data/ncsl/NCSL-2025.txt` and **replaces**
`data/ncsl/ncsl_bills.csv`. It extracts the candidate ID, state code, bill number,
dataset year, title, status, act number, and last-action date. It flags incomplete
entries and warns if the export does not contain the expected 192 records.
The script reads the text export; it does not extract text from the PDF.

## Check the saved file inventory

```powershell
python -B src/inventory.py
```

This scans four-digit year folders under `output/staging/`, preserving the statute
texts and replacing two reports:

- `output/staging/inventory/law_inventory.csv`: recognized files and their identifiers.
- `output/staging/inventory/files_to_review.csv`: files with unexpected folder
  structures, unmatched filenames, or duplicate law IDs.

Recognized filenames follow `STATE_BILL_Act-NUMBER.txt` or
`STATE_BILL_Chapter-NUMBER.txt` inside `<year>/<state>/`. The scan skips `Notes.txt`,
files without the lowercase `.txt` extension, and supporting cache/report folders.
Paths are sorted, and the first matching file for each law ID is retained.

Some saved files deliberately use `Signed-YYYY-MM-DD` because no act number was
available. The current inventory flags these filenames for review; that does not
by itself mean retrieval failed. Inventory reports are excluded from Git.

## Using the texts for research

Saved text is a research aid. Check the review notes before interpreting a
provision: enrolled versions, source-date differences, PDF extraction, HTML
redlining from earlier runs, and final-act or veto comparisons may still need
attention. Dataset inclusion alone does not establish that a measure creates a
new AI obligation.

Credentials, API caches, downloaded source documents, the local Xpdf distribution,
and generated inventory reports are excluded from Git. The tracked statute texts
and historical reports retain their original source and processing information.
