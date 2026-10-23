"""Retrieve NCSL-listed legislation through LegiScan, preserving existing statutes."""

import argparse
import base64
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPRedirectHandler

from read_ncsl import FIELDS

STAGING = Path("output/staging")
BILLS = Path("data/ncsl/ncsl_bills.csv")
RESOLUTIONS = Path("data/ncsl/legiscan_resolutions.json")
PDF_TOOL = Path("tools/xpdf-tools-win-4.06/bin64/pdftotext.exe")
STATE_NAMES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_new(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents overwriting statutes or another run's files.
    with path.open("xb") as stream:
        try:
            stream.write(
                content.encode("utf-8") if isinstance(content, str) else content
            )
        except Exception:
            stream.close()
            path.unlink()
            raise


def load_api_key():
    for line in Path(".env").read_text(encoding="utf-8").splitlines():
        name, separator, value = line.strip().partition("=")
        if separator and name.strip() == "LEGISCAN_API_KEY":
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            if value:
                return value
    raise ValueError("Missing LEGISCAN_API_KEY in .env.")


class NoRedirects(HTTPRedirectHandler):
    # A redirect must not carry the API key to another address.
    def redirect_request(self, request, file, code, message, headers, url):
        return None


class LegiScan:
    def __init__(self, run_id, offline=False, refresh=False):
        self.run_id = run_id
        self.offline = offline
        self.refresh = refresh
        self.api_key = "" if offline else load_api_key()
        self.loaded = {}
        self.opener = build_opener(NoRedirects())

    def cached_file(self, key):
        return max((STAGING / "cache" / key).glob("*.json"), default=None)

    def checked(self, response):
        if response.get("status") != "OK":
            raise ValueError(
                "LegiScan returned ERROR or an unexpected status. Check your API key and account access."
            )
        return response

    def request(self, key, operation, update=False, **parameters):
        """Reuse a cached response or fetch and preserve a paced API response."""
        if key in self.loaded:
            return self.loaded[key]
        cached = self.cached_file(key)
        if cached and (not update or self.offline):
            response = self.checked(read_json(cached))
        else:
            if self.offline:
                raise ValueError(f"Offline cache miss: {key}")
            query = urlencode(dict(key=self.api_key, op=operation, **parameters))
            for attempt in range(3):
                time.sleep(1.1)
                try:
                    with self.opener.open(
                        "https://api.legiscan.com/?" + query, timeout=30
                    ) as stream:
                        response = self.checked(json.load(stream))
                    break
                except HTTPError as error:
                    if error.code != 429 or attempt == 2:
                        raise ValueError(f"HTTP error: {error.code}") from None
                    time.sleep(5 * (attempt + 1))
                except URLError:
                    # Network exceptions may contain the request URL, including the key.
                    raise ValueError(
                        "HTTPS request failed; check your connection and certificates."
                    ) from None
            save_new(
                STAGING / "cache" / key / f"{self.run_id}.json",
                json.dumps(response, indent=2),
            )
        self.loaded[key] = response
        return response


def normalize_bill(value):
    letters = "".join(re.findall(r"[A-Za-z]", value)).upper()
    digits = "".join(re.findall(r"[0-9]", value)).lstrip("0") or "0"
    return letters + digits


def iso_date(value):
    if re.fullmatch(r"[0-9]{2}/[0-9]{2}/[0-9]{4}", value):
        return value[6:] + "-" + value[:2] + "-" + value[3:5]
    return value


def read_bills():
    with BILLS.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader, [])
        if len(header) != len(set(header)) or not set(FIELDS).issubset(header):
            raise ValueError("Missing or duplicate CSV columns.")
        bills = []
        for row in reader:
            if not row or row == [""]:
                continue
            if len(row) != len(header):
                raise ValueError("CSV column count mismatch.")
            bills.append(dict(zip(header, row)))
    return bills


def find_bill(row, api, review):
    """Find one matching bill and session, then verify identity and change hashes."""
    state, bill_number = row["state_code"], row["bill_number"]
    year = int(row["ncsl_year"])
    resolution = (
        read_json(RESOLUTIONS).get(row["candidate_id"], {})
        if RESOLUTIONS.exists()
        else {}
    )
    if resolution:
        review["match_resolution"] = resolution
    if "session_year" in resolution:
        year = int(resolution["session_year"])
        review["notes"].append(
            f"Reviewed session year {year} differs from NCSL dataset year; original input and output folder retained."
        )
    matched_number = resolution.get("api_bill_number", bill_number)
    sessions = api.request(
        "sessions_" + state, "getSessionList", api.refresh, state=state
    )["sessions"]
    matches = {}
    for session in sessions:
        if not int(session["year_start"]) <= year <= int(session["year_end"]):
            continue
        session_id = int(session["session_id"])
        if resolution and session_id != int(resolution["session_id"]):
            continue
        master = api.request(
            f"master_{session_id}", "getMasterList", api.refresh, id=session_id
        )["masterlist"]
        entries = master.values() if isinstance(master, dict) else master
        for entry in entries:
            if not isinstance(entry, dict) or "bill_id" not in entry:
                continue
            if normalize_bill(entry.get("number", "")) != normalize_bill(
                matched_number
            ):
                continue
            if resolution and int(entry["bill_id"]) != int(resolution["bill_id"]):
                continue
            matches[int(entry["bill_id"])] = dict(entry, session_id=session_id)
    if len(matches) != 1:
        raise ValueError(
            f"Exact bill/session matches: {len(matches)}; review required."
        )
    bill_id, match = next(iter(matches.items()))
    key = f"bill_{bill_id}"
    previous = api.cached_file(key)
    old_hash = (
        api.checked(read_json(previous))["bill"].get("change_hash", "")
        if previous
        else ""
    )
    listed_hash = match.get("change_hash", "")
    bill = api.request(
        key, "getBill", api.refresh or old_hash != listed_hash, id=bill_id
    )["bill"]
    session = bill["session"]
    if (
        int(bill["bill_id"]) != bill_id
        or bill["state"] != state
        or normalize_bill(bill["bill_number"]) != normalize_bill(matched_number)
        or not int(session["year_start"]) <= year <= int(session["year_end"])
        or bill["session_id"] != session["session_id"]
        or int(session["session_id"]) != match["session_id"]
    ):
        raise ValueError("Bill state, number or session does not match.")
    current_hash = bill.get("change_hash", "")
    comparison = "no previous record" if not old_hash else "unchanged"
    if old_hash and old_hash != current_hash:
        comparison = "changed"
        review["notes"].append("Change hash changed; previous record preserved.")
    review.update(
        previous_change_hash=old_hash,
        change_hash=current_hash,
        change_hash_comparison=comparison,
    )
    if not current_hash or listed_hash != current_hash:
        review["notes"].append("Missing or inconsistent master-list/bill change hash.")
    if int(session.get("special", 0)):
        review["notes"].append("Special session: confirm against NCSL year-only input.")
    return bill


def select_text(row, bill, resolution, notes):
    """Prefer final legislative text, applying reviewed selections when provided."""
    preferred = []
    best_rank = 0
    for text in bill["texts"]:
        rank = {"Chaptered": 3, "Enacted": 3, "Enrolled": 2}.get(text.get("type"), 1)
        if rank == 1:
            selection = "verified_doc_id"
        elif rank == 2:
            selection = "selected_doc_id"
        else:
            selection = None
        if selection in resolution and int(text["doc_id"]) != int(
            resolution[selection]
        ):
            continue
        if rank > best_rank:
            best_rank, preferred = rank, []
        if rank == best_rank:
            preferred.append(text)
    if "official_text" in resolution:
        text = resolution["official_text"]
        if not re.fullmatch(r"official_[A-Za-z0-9_]+", text["document_key"]):
            raise ValueError("Invalid official document key.")
        if int(bill["status"]) != 4 or text["date"] != iso_date(
            row["last_action_date"]
        ):
            raise ValueError("Official chapter status/date does not match NCSL.")
        notes.append(
            "Official chapter source used; API has only earlier bill texts. Visual review pending."
        )
        return text
    if len(preferred) != 1:
        raise ValueError(
            "Missing or ambiguous preferred text; inspect cached bill texts."
        )
    text = preferred[0]
    if best_rank < 2:
        if (
            "verified_doc_id" not in resolution
            or int(resolution["verified_doc_id"]) != int(text["doc_id"])
            or int(bill["status"]) != 4
            or bill.get("status_date", "") != iso_date(row["last_action_date"])
        ):
            raise ValueError(
                "Only earlier text available; enacted/enrolled text needs review."
            )
        verification = resolution.get(
            "verification_note",
            "legislative provisions compared against official session law",
        )
        notes.append(
            f"API text labelled {text.get('type', '')}; {verification}: {resolution['official_source_url']}"
        )
    if best_rank == 2:
        notes.append("Enrolled fallback; official act comparison pending.")
    return text


def document_text(text, doc_id, official):
    """Preserve the source and return UTF-8 text, converting PDFs as needed."""
    extension = {"application/pdf": ".pdf", "text/plain": ".txt"}.get(text["mime"])
    if not extension:
        raise ValueError("Unsupported document MIME type.")
    document = STAGING / "documents" / f"text_{doc_id}{extension}"
    raw = document.read_bytes() if official else base64.b64decode(text["doc"])
    if extension == ".pdf" and not raw.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF header.")
    if not document.exists():
        save_new(document, raw)
    elif document.read_bytes() != raw:
        raise ValueError("Existing document differs; preserved for review.")
    processing = "Plain UTF-8 text preserved"
    if extension == ".pdf":
        extracted = document.with_name(f"text_{doc_id}_xpdf.txt")
        if not PDF_TOOL.is_file():
            raise ValueError("Cannot find pdftotext.exe or the source PDF.")
        if not extracted.exists() or not extracted.stat().st_size:
            try:
                subprocess.run(
                    [
                        str(PDF_TOOL.resolve()),
                        "-layout",
                        "-enc",
                        "UTF-8",
                        str(document.resolve()),
                        str(extracted.resolve()),
                    ],
                    check=True,
                    timeout=60,
                    capture_output=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except (subprocess.SubprocessError, OSError):
                extracted.unlink(missing_ok=True)
                raise ValueError(
                    "PDF conversion failed or exceeded 60 seconds."
                ) from None
        raw = extracted.read_bytes()
        processing = "PDF converted to UTF-8 text using Xpdf pdftotext -layout"
    content = raw.decode("utf-8")
    if not content.strip() or "\0" in content:
        raise ValueError("Empty or non-UTF-8 text; encoding/OCR review required.")
    return content, processing


def process_bill(row, api, review):
    """Stage one validated bill with source metadata and review notes."""
    state, number, year = row["state_code"], row["bill_number"], row["ncsl_year"]
    if not (
        re.fullmatch(r"[A-Z]{2}", state)
        and re.fullmatch(r"[A-Z]+[0-9]+", number)
        and re.fullmatch(r"20[0-9]{2}", year)
    ):
        raise ValueError("Invalid CSV bill identity.")
    name = STATE_NAMES[state]
    bill = find_bill(row, api, review)
    resolution = review.get("match_resolution", {})
    official = "official_text" in resolution
    selected = select_text(row, bill, resolution, review["notes"])
    review["bill_id"] = bill["bill_id"]
    notes = review["notes"]
    if int(bill["status"]) != 4:
        notes.append("LegiScan status is not passed; verify NCSL enactment.")
    ncsl_date = iso_date(row["last_action_date"])
    status_date = bill.get("status_date", "")
    review.update(ncsl_date=row["last_action_date"], legiscan_date=status_date)
    if ncsl_date != status_date:
        notes.append("NCSL and LegiScan dates differ; neither supersedes the other.")
    doc_id = selected["document_key"] if official else str(int(selected["doc_id"]))
    text = (
        selected
        if official
        else api.request(f"text_{doc_id}", "getBillText", id=doc_id)["text"]
    )
    if official:
        review["official_document"] = text
    else:
        for field in ("doc_id", "type", "mime", "text_hash"):
            if text[field] != selected[field]:
                raise ValueError(f"Document metadata mismatch: {field}")
        if text["bill_id"] != bill["bill_id"]:
            raise ValueError("Document bill ID mismatch.")
        review["doc_id"] = text["doc_id"]
    content, processing = document_text(text, doc_id, official)
    review["processing"] = processing
    act = row["act_number"]
    official_act = not act and "official_act_number" in resolution
    if official_act:
        act = resolution["official_act_number"]
        notes.append(
            "Act number supplied by reviewed official source; NCSL act number was blank."
        )
    filename = f"{state}_{number}_Act-{act}.txt"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", act):
        filename = resolution.get("reviewed_filename", "")
        if act or not re.fullmatch(
            state + "_" + number + r"_Signed-[0-9]{4}-[0-9]{2}-[0-9]{2}\.txt", filename
        ):
            raise ValueError("Missing/unsafe act number; filename needs review.")
        notes.append(
            "Act number unavailable; reviewed bill/signature-date filename used."
        )
    destination = STAGING / year / name / filename
    review["file"] = destination.as_posix()
    text_date, version = text.get("date", ""), text.get("type", "")
    if not text_date or text_date == "0000-00-00":
        notes.append("Document date not supplied.")
    if destination.exists():
        review["result"] = "existing_preserved"
        notes.append("Existing statute preserved; compare current metadata before use.")
        return
    date_check = (
        "Source dates agree"
        if ncsl_date == status_date
        else "Pending; source dates differ"
    )
    displayed_date = (
        text_date
        if text_date and text_date != "0000-00-00"
        else f"Not supplied (API value: {text_date})"
    )
    metadata = [
        ("State", name),
        ("Bill", bill.get("bill_number", "")),
        ("NCSL result year", year),
        ("Session", bill["session"].get("session_name", "")),
        ("NCSL title", row["title"]),
        ("LegiScan title", bill.get("title", "")),
        (
            "Act number (official source)" if official_act else "Act number (NCSL)",
            act or "Not supplied",
        ),
        ("NCSL last-action date", ncsl_date),
        ("LegiScan status date", status_date),
        ("Date verification", date_check),
        ("Text version", version),
        ("Text date", displayed_date),
        ("LegiScan bill ID", bill["bill_id"]),
        (
            "LegiScan document ID",
            "Not applicable (official chapter source)" if official else doc_id,
        ),
        ("Bill source", bill.get("url", "")),
        ("Text source", text.get("url", "")),
        ("Official bill source", bill.get("state_link", "")),
        ("Attribution", "Bill metadata and history supplied by LegiScan"),
        ("License", "https://creativecommons.org/licenses/by/4.0/"),
        ("Processing", processing),
        (
            "Review",
            "; ".join(
                ["Visual verification and official act comparison pending"] + notes
            ),
        ),
    ]
    output = "\n".join(f"{label}: {value}" for label, value in metadata)
    output += "\n\nLEGISLATIVE HISTORY\n\n"
    for action in bill["history"]:
        output += f"{action.get('date', '')} | {action.get('action', '')}\n"
    output += f"\nFULL STATUTORY TEXT — {version.upper()} VERSION\n\n{content}"
    save_new(destination, output)
    review["result"] = "staged_needs_review" if notes else "staged"


def check_output_paths():
    """Reject redirected output folders before writing staged files."""
    paths = [Path("output"), STAGING]
    if STAGING.exists():
        paths.extend(STAGING.rglob("*"))
    for path in paths:
        if path.exists() or path.is_symlink():
            attributes = getattr(path.lstat(), "st_file_attributes", 0)
            if path.is_symlink() or attributes & getattr(
                stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0
            ):
                raise ValueError("Output path is redirected.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true")
    mode.add_argument("--refresh", action="store_true")
    parser.add_argument("--example", action="store_true")
    parser.add_argument("--candidate")
    args = parser.parse_args()
    check_output_paths()
    bills = read_bills()
    if args.candidate and not any(
        row["candidate_id"] == args.candidate for row in bills
    ):
        raise ValueError("Candidate ID not found in NCSL input.")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ_") + str(os.getpid())
    api = LegiScan(run_id, args.offline, args.refresh)
    report = dict(source=BILLS.as_posix(), run_utc=run_id, bills=[])
    seen = set()
    completed = 0
    for row in bills:
        if args.candidate and row["candidate_id"] != args.candidate:
            continue
        if args.example and row["candidate_id"] != "AL_2025_HB365":
            continue
        item = dict(ncsl=row, result="needs_review", notes=[])
        try:
            identity = (
                row["state_code"],
                row["ncsl_year"],
                normalize_bill(row["bill_number"]),
            )
            if identity in seen:
                raise ValueError("Duplicate CSV bill.")
            seen.add(identity)
            process_bill(row, api, item)
            completed += 1
        except (KeyError, TypeError, json.JSONDecodeError):
            item["notes"].append(
                "Unexpected API/cache schema; inspect saved responses."
            )
        except (ValueError, OSError) as error:
            item["notes"].append(str(error))
        report["bills"].append(item)
        print(f"{row['candidate_id']}: {item['result']}")
    report["completed"] = completed
    destination = STAGING / "reports" / f"{run_id}.json"
    save_new(destination, json.dumps(report, indent=2))
    print(
        f"{completed}/{len(report['bills'])} staged or preserved. Report: {destination}"
    )
    return 0 if report["bills"] and completed == len(report["bills"]) else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, TypeError, csv.Error) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
