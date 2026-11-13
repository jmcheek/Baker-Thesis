"""Create bordered Excel tables and a summary chart from theme_counts.csv.

Requires openpyxl: python -m pip install openpyxl
"""

import argparse
import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


SHEET_NAMES = [
    "Education", "Synthetic media", "Public safety", "Health",
    "Infrastructure", "Consumer protection", "Public governance",
    "Privacy", "Employment", "National security",
]


def style_table(sheet, widths, freeze):
    edge = Side(style="thin", color="A6B3C0")
    border = Border(left=edge, right=edge, top=edge, bottom=edge)
    for row in sheet:
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            if cell.row == 1:
                cell.fill = PatternFill("solid", fgColor="24476A")
                cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            else:
                cell.font = Font(name="Calibri", size=11)
                if cell.row % 2 == 0:
                    cell.fill = PatternFill("solid", fgColor="EDF3F8")
                if isinstance(cell.value, int):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
    for index, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    sheet.row_dimensions[1].height = 48
    sheet.freeze_panes = freeze
    sheet.auto_filter.ref = sheet.dimensions
    sheet.sheet_view.showGridLines = False
    sheet.sheet_properties.pageSetUpPr.fitToPage = True
    sheet.page_setup.orientation = "landscape"
    sheet.page_setup.paperSize = sheet.PAPERSIZE_A4
    sheet.page_setup.fitToWidth = 1
    sheet.page_setup.fitToHeight = 0
    sheet.print_title_rows = "1:1"


def export_workbook(source, output):
    if output.exists():
        raise FileExistsError(f"Output already exists: {output}. Choose another --output.")
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    if not rows or not fields or fields[:2] != ["State", "Statute"]:
        raise ValueError("Expected a nonempty theme_counts.csv with State and Statute columns.")
    themes = fields[2::2]
    if len(themes) != len(SHEET_NAMES):
        raise ValueError("Expected ten paired themes and mention-count columns.")
    for theme, count_header in zip(themes, fields[3::2]):
        if count_header != f"{theme} - No. mentions":
            raise ValueError(f"Unexpected mention-count column for {theme}")
        for row in rows:
            count = int(row[count_header])
            if count < 0 or int(row[theme]) != int(count > 0):
                raise ValueError(f"Inconsistent search indicator/count: {row['Statute']}")

    book = Workbook()
    overview = book.active
    overview.title = "Overview"
    overview.append(["Theme", "Bills with keyword matches", "Total mentions"])
    for theme in themes:
        overview.append([
            theme,
            sum(int(row[theme]) for row in rows),
            sum(int(row[f"{theme} - No. mentions"]) for row in rows),
        ])
    style_table(overview, [48, 26, 22], "B2")
    overview["A14"] = "1 = keyword match found; 0 = no match. These are not reviewed coding decisions."
    overview.merge_cells("A14:C16")
    overview["A14"].alignment = Alignment(wrap_text=True, vertical="center")
    overview["A14"].font = Font(italic=True, color="52616F")
    chart = BarChart()
    chart.type = "bar"
    chart.title = "Bills with candidate theme keywords"
    chart.x_axis.title = f"Number of bills (out of {len(rows)})"
    chart.add_data(Reference(overview, min_col=2, min_row=1, max_row=11), titles_from_data=True)
    chart.set_categories(Reference(overview, min_col=1, min_row=2, max_row=11))
    chart.legend = None
    chart.width = 25
    chart.height = 15
    overview.add_chart(chart, "E2")

    all_themes = book.create_sheet("All themes")
    all_themes.append(fields)
    for row in rows:
        all_themes.append([row[field] if index < 2 else int(row[field]) for index, field in enumerate(fields)])
    style_table(all_themes, [12, 27] + [24, 18] * len(themes), "C2")

    for theme, sheet_name in zip(themes, SHEET_NAMES):
        sheet = book.create_sheet(sheet_name)
        sheet.append(["State", "Statute", theme, "No. mentions"])
        for row in rows:
            sheet.append([row["State"], row["Statute"], int(row[theme]), int(row[f"{theme} - No. mentions"])])
        style_table(sheet, [12, 29, 38, 18], "C2")

    output.parent.mkdir(parents=True, exist_ok=True)
    # Save through an exclusively created stream to preserve existing workbooks.
    with output.open("xb") as stream:
        book.save(stream)
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("output/coding/theme_counts.csv"))
    parser.add_argument("--output", type=Path, default=Path("output/coding/theme_counts.xlsx"))
    args = parser.parse_args()
    count = export_workbook(args.source, args.output)
    print(f"Saved {count} statutes with bordered tables and a summary chart to {args.output}")


if __name__ == "__main__":
    main()
