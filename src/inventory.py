"""Inventory statute filenames without modifying the statute texts."""

import csv
from pathlib import Path
import re
import sys

FIELDS = (
    "law_id",
    "year_folder",
    "state_folder",
    "state_code",
    "bill_number",
    "document_type",
    "document_number",
    "relative_path",
)
BILL_NAME = re.compile(r"([A-Z]{2})_([A-Z]+[0-9]+)_(Act|Chapter)-(.+)\.txt", re.I)


def inventory(folder):
    """Return recognized statutes and files needing a filename or folder review."""
    laws = []
    review = []
    seen = set()
    # Only year folders contain statutes. Ignore cached documents and reports.
    for year_folder in sorted(folder.iterdir()):
        if not year_folder.is_dir() or not re.fullmatch(r"[0-9]{4}", year_folder.name):
            continue
        for path in sorted(year_folder.rglob("*")):
            if not path.is_file() or path.suffix != ".txt" or path.name == "Notes.txt":
                continue
            relative = path.relative_to(folder)
            match = BILL_NAME.fullmatch(path.name)
            if len(relative.parts) != 3:
                review.append(
                    (str(relative), "Expected year/state/filename folder structure")
                )
                continue
            if not match:
                review.append(
                    (str(relative), "Filename does not match expected bill pattern")
                )
                continue
            state, bill, kind, number = match.groups()
            law_id = f"{state}_{year_folder.name}_{bill}"
            if law_id in seen:
                review.append((str(relative), f"Duplicate law ID: {law_id}"))
                continue
            seen.add(law_id)
            laws.append(
                (
                    law_id,
                    year_folder.name,
                    path.parent.name,
                    state,
                    bill,
                    kind,
                    number,
                    str(relative),
                )
            )
    return laws, review


def main():
    folder = Path("output/staging")
    if not folder.is_dir():
        raise FileNotFoundError(f"Cannot find folder: {folder}")
    laws, review = inventory(folder)
    destination = folder / "inventory"
    destination.mkdir(parents=True, exist_ok=True)
    for name, fields, rows in (
        ("law_inventory.csv", FIELDS, laws),
        ("files_to_review.csv", ("relative_path", "reason"), review),
    ):
        with (destination / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(fields)
            writer.writerows(rows)
    print(
        f"Laws inventoried: {len(laws)}\n"
        f"Files needing review: {len(review)}\n"
        f"Output folder: {destination.resolve()}"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
