"""Convert the saved NCSL export into the bill list used by legiscan.py."""

import csv
from pathlib import Path
import re
import sys

FIELDS = (
    "candidate_id",
    "state_code",
    "bill_number",
    "ncsl_year",
    "title",
    "status",
    "act_number",
    "last_action_date",
)


def read_ncsl_file(lines):
    """Parse bill headings, titles, and status fields from the saved NCSL export."""
    bills = []
    current = None
    reading_title = False
    chambers = {"H": "HB", "S": "SB", "A": "AB", "L": "LB"}

    for line in lines:
        line = line.replace("\f", "").strip()
        if not line:
            continue
        heading = re.fullmatch(r"([A-Z]{2})[ \t]+([A-Z]+)[ \t]+([0-9]+)", line)
        if heading:
            if current is not None:
                bills.append(current)
            state, chamber, number = heading.groups()
            current = dict.fromkeys(FIELDS, "")
            current.update(
                state_code=state, bill_number=chambers.get(chamber, chamber) + number
            )
            reading_title = False
        elif current is None:
            continue
        elif not current["ncsl_year"] and re.fullmatch(r"[0-9]{4}", line):
            # The export puts the year immediately before the title.
            current["ncsl_year"] = line
            reading_title = True
        elif line.startswith("Status:"):
            reading_title = False
            current["status"] = line.removeprefix("Status:").strip()
            if "Act No." in current["status"]:
                current["act_number"] = current["status"].split("Act No.", 1)[1].strip()
        elif line.startswith("Date of Last Action:"):
            current["last_action_date"] = (
                line.removeprefix("Date of Last Action:").strip().split(" - ", 1)[0]
            )
        elif reading_title:
            current["title"] = (current["title"] + " " + line).strip()

    if current is not None:
        bills.append(current)
    for bill in bills:
        bill["candidate_id"] = "_".join(
            bill[key] for key in ("state_code", "ncsl_year", "bill_number")
        )
    return bills


def main():
    source = Path("data/ncsl/NCSL-2025.txt")
    destination = Path("data/ncsl/ncsl_bills.csv")
    with source.open(encoding="utf-8") as stream:
        bills = read_ncsl_file(stream)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream, FIELDS, quoting=csv.QUOTE_ALL, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(bills)
    incomplete = 0
    for bill in bills:
        if any(
            not bill[key]
            for key in ("ncsl_year", "title", "status", "last_action_date")
        ):
            print(f"Check incomplete entry: {bill['candidate_id']}", file=sys.stderr)
            incomplete += 1
    print(
        f"Bills extracted: {len(bills)}\n"
        f"Incomplete entries: {incomplete}\n"
        f"CSV saved to: {destination.resolve()}"
    )
    if len(bills) != 192:
        print("Warning: expected 192 bills in this export.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, UnicodeError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
