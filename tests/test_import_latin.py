import unittest

from pathlib import Path
from tools.import_latin import (ExtractionError, _is_reviewed,
                                extract_html, merge_import_report)


class ImportLatinTests(unittest.TestCase):
    def test_continuation_and_poetry_are_attached_until_next_number(self):
        html = """<html><body><p>I. DE TEST. [1] First <b>Latin</b>.</p>
        <p>Poetry line one<br>Poetry line two.</p>
        <p>[2] Second with Greek ἄλφα.</p></body></html>"""
        records, chapters, warnings = extract_html(html, 3)
        self.assertEqual([r["ref"] for r in records], ["3.1.1", "3.1.2"])
        self.assertIn("Poetry line one\nPoetry line two.", records[0]["text"])
        self.assertIn("ἄλφα", records[1]["text"])
        self.assertEqual(chapters[0]["title"], "DE TEST")
        self.assertEqual(warnings, [])

    def test_duplicate_section_ids_fail(self):
        html = "<p>I. DE TEST. [1] A.</p><p>[1] B.</p>"
        with self.assertRaisesRegex(ExtractionError, "duplicate or out-of-order"):
            extract_html(html, 1)

    def test_uppercase_html_and_inline_chapter_boundary(self):
        html = "<P>I. DE PRIMA. [1] Prima.</P><P>II. DE SECVNDA.[1] Secunda.</P>"
        records, chapters, _ = extract_html(html, 4)
        self.assertEqual([r["ref"] for r in records], ["4.1.1", "4.2.1"])
        self.assertEqual([c["title"] for c in chapters], ["DE PRIMA", "DE SECVNDA"])

    def test_lowercase_prose_with_roman_citation_does_not_reset_chapter(self):
        html = "<p>I. DE TEST. [1] Initium.</p><p>verbum I. dictum. [2] Continuatio.</p>"
        records, chapters, _ = extract_html(html, 2)
        self.assertEqual([r["ref"] for r in records], ["2.1.1", "2.1.2"])
        self.assertEqual(len(chapters), 1)

    def test_substantive_unassigned_text_is_reported(self):
        html = "<p>I. DE TEST. [1] A.</p><p>Loose text.</p>"
        records, _, warnings = extract_html(html, 1)
        self.assertEqual(records[0]["text"], "A.\nLoose text.")
        self.assertEqual(warnings, [])

    def test_raw_book_12_footer_does_not_contaminate_last_section(self):
        source = Path(__file__).parent / "fixtures" / "book12-footer.html"
        html = source.read_text(encoding="utf-8")
        records, _, _ = extract_html(html, 12)
        self.assertEqual(records[-1]["ref"], "12.8.17")
        self.assertTrue(records[-1]["text"].startswith("Gurgulio dicitur"))
        self.assertNotRegex(records[-1]["text"], r"Isidore of Seville|Christian Latin|The Latin Library|The Classics Page")

    def test_single_book_report_merge_preserves_other_imports_and_errors(self):
        old = {"imports": [{"book": 1, "sha256": "old1"}, {"book": 2, "sha256": "old2"}],
               "errors": [{"book": 3, "error": "source issue"}]}
        result = {"book": 1, "sha256": "new1", "record_count": 4, "chapters": []}
        merged = merge_import_report(old, [result], [], all_books=False, target_book=1,
                                    blocked_books=set(), reset_events=[])
        self.assertEqual([(row["book"], row["sha256"]) for row in merged["imports"]],
                         [(1, "new1"), (2, "old2")])
        self.assertEqual(merged["errors"], old["errors"])

    def test_full_report_replaces_run_and_retains_blocked_reviewed_import(self):
        old = {"imports": [{"book": 1, "sha256": "old1"}, {"book": 2, "sha256": "reviewed2"}],
               "errors": [{"book": 3, "error": "old error"}]}
        merged = merge_import_report(old, [{"book": 1, "sha256": "new1", "chapters": []}],
                                    [{"book": 3, "error": "current error"}], all_books=True,
                                    target_book=None, blocked_books={2}, reset_events=[])
        self.assertEqual([(row["book"], row["sha256"]) for row in merged["imports"]],
                         [(1, "new1"), (2, "reviewed2")])
        self.assertEqual(merged["errors"], [{"book": 3, "error": "current error"}])

    def test_reviewed_entries_require_explicit_reset(self):
        self.assertTrue(_is_reviewed({"status": "reviewed", "coverage_verified": False,
                                      "review_record": None}))
        self.assertTrue(_is_reviewed({"status": "in-progress", "coverage_verified": True,
                                      "review_record": None}))
        self.assertFalse(_is_reviewed({"status": "in-progress", "coverage_verified": False,
                                       "review_record": None}))


if __name__ == "__main__":
    unittest.main()
