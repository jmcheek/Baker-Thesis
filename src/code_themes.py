"""Count candidate theme mentions and create paired search indicators and totals.

Run from the repository root: python -B src/code_themes.py
"""

import argparse
import csv
import json
from pathlib import Path
import re
import sys


def load_codebook(path):
    codebook = json.loads(path.read_text(encoding="utf-8-sig"))
    themes = codebook["themes"]
    keys = [theme["key"] for theme in themes]
    if not keys or len(keys) != len(set(keys)):
        raise ValueError("The codebook needs unique theme keys.")

    for theme in themes:
        if not re.fullmatch(r"[a-z][a-z_]*", theme["key"]):
            raise ValueError(f"Invalid theme key: {theme['key']}")
        if not theme["patterns"]:
            raise ValueError(f"No search patterns for {theme['name']}")
        theme["regex"] = re.compile(
            "|".join(f"(?:{pattern})" for pattern in theme["patterns"]),
            re.IGNORECASE,
        )
    return codebook


def statutory_text(text):
    """Exclude retrieval metadata, history, and explicit deletion markers."""
    _, heading, remainder = text.partition("FULL STATUTORY TEXT")
    if not heading:
        raise ValueError("Missing statutory-text heading")
    _, newline, body = remainder.partition("\n")
    if not newline or not body.strip():
        raise ValueError("Missing statutory text")

    body = re.sub(r"\[DELETED:.*?\]", " ", body, flags=re.DOTALL)
    body = re.sub(r"\[ADDED:(.*?)\]", r"\1", body, flags=re.DOTALL)
    body = body.replace("\u00ad", "")
    body = re.sub(r"([A-Za-z])-\s*\n\s*([a-z])", r"\1\2", body)
    return re.sub(r"\s+", " ", body).strip()


def code_statute(path, codebook):
    identity = re.fullmatch(r"([A-Z]{2})_([A-Z]+[0-9]+)_.+", path.stem)
    year = path.parent.parent.name
    if not identity or not re.fullmatch(r"[0-9]{4}", year):
        raise ValueError(f"Unexpected statute path: {path}")
    state, bill = identity.groups()
    raw = path.read_bytes()
    try:
        text = statutory_text(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeError) as error:
        raise ValueError(f"{path}: {error}") from error

    row = {"State": state, "Statute": f"{state}_{year}_{bill}"}
    for theme in codebook["themes"]:
        count = sum(1 for _ in theme["regex"].finditer(text))
        # An indicator records a search hit, not a substantive coding decision.
        row[theme["name"]] = int(count > 0)
        row[f"{theme['name']} - No. mentions"] = count

    return row


def create_counts(statutes, codebook_path, output):
    # Never replace an existing spreadsheet.
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}. Choose another --output.")
    codebook = load_codebook(codebook_path)
    paths = sorted(
        path for path in statutes.glob("*/*.txt")
        if path.is_file() and path.name != "Notes.txt"
    )
    if not paths:
        raise FileNotFoundError(f"No statute texts found in {statutes}")

    # Validate every input before creating the output file.
    rows = [code_statute(path, codebook) for path in paths]
    rows.sort(key=lambda row: (row["State"], row["Statute"]))
    identifiers = [row["Statute"] for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Duplicate statute IDs found; resolve them before coding.")

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--statutes", type=Path, default=Path("output/staging/2025"))
    parser.add_argument("--codebook", type=Path, default=Path("data/coding/themes.json"))
    parser.add_argument("--output", type=Path, default=Path("output/coding/theme_counts.csv"))
    args = parser.parse_args()
    count = create_counts(args.statutes, args.codebook, args.output)
    print(f"Saved {count} statutes to {args.output}")
    print("Indicators mean keyword matches found, not reviewed theme decisions.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, re.error) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
