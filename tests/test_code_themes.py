import csv
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from code_themes import create_counts, statutory_text

CODEBOOK = Path(__file__).resolve().parents[1] / "data/coding/themes.json"


class CodingReviewTests(unittest.TestCase):
    def test_search_body_excludes_history_and_deleted_text(self):
        text = (
            "Title: students\nLEGISLATIVE HISTORY\nmedical\n"
            "FULL STATUTORY TEXT - ENACTED VERSION\n"
            "[DELETED: clinical] [ADDED: school] job train-\ning\n"
        )
        self.assertEqual(statutory_text(text), "school job training")

    def test_output_pairs_indicators_with_counts_including_zero_matches(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "2025" / "Alabama"
            state.mkdir(parents=True)
            (state / "AL_HB1_Act-1.txt").write_text(
                "FULL STATUTORY TEXT\nstudents students clinical", encoding="utf-8"
            )
            (state / "AL_HB2_Signed-2025-01-01.txt").write_text(
                "FULL STATUTORY TEXT\nA neutral passage.", encoding="utf-8"
            )
            output = root / "review.csv"
            self.assertEqual(create_counts(root / "2025", CODEBOOK, output), 2)
            with output.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(rows[0]["Statute"], "AL_2025_HB1")
            self.assertEqual(rows[0]["Education and workforce development - No. mentions"], "2")
            self.assertEqual(rows[0]["Health and clinical decisions - No. mentions"], "1")
            self.assertEqual(rows[1]["Statute"], "AL_2025_HB2")
            for row in rows:
                self.assertEqual(row["State"], "AL")
                self.assertEqual(len(row), 22)
            self.assertEqual(rows[0]["Education and workforce development"], "1")
            self.assertEqual(rows[1]["Education and workforce development"], "0")
            self.assertEqual(rows[1]["Education and workforce development - No. mentions"], "0")

    def test_existing_review_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "review.csv"
            output.write_text("Human decisions", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                create_counts(root / "2025", CODEBOOK, output)
            self.assertEqual(output.read_text(encoding="utf-8"), "Human decisions")

    def test_invalid_source_does_not_leave_partial_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "2025" / "Alabama"
            state.mkdir(parents=True)
            (state / "AL_HB1_Act-1.txt").write_text("Metadata only", encoding="utf-8")
            output = root / "review.csv"
            with self.assertRaisesRegex(ValueError, "Missing statutory-text heading"):
                create_counts(root / "2025", CODEBOOK, output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
