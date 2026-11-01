"""Check that incomplete or unreviewed books cannot become release manuscripts."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import project


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ("latin", "translation", "segments", "audit"):
            (self.root / folder).mkdir()
        self.manifest = {"schema_version": 1, "books": [
            {"book": number, "status": "not-started",
             "latin": f"latin/book-{number:02}.jsonl",
             "translation": f"translation/book-{number:02}.jsonl",
             "expected_sections": None, "coverage_verified": False,
             "review_record": None}
            for number in range(1, 21)]}

    def save(self):
        (self.root / "segments/manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def section(self, folder, ref="1.1.1", text="Fixture text"):
        record = {"ref": ref, "text": text}
        if folder == "translation":
            record["notes"] = ["A fixture note."]
        with (self.root / folder / "book-01.jsonl").open("a", encoding="utf-8") as output:
            output.write(json.dumps(record) + "\n")

    def accept(self):
        self.section("latin")
        self.section("translation")
        self.manifest["books"][0].update(status="accepted", expected_sections=["1.1.1"],
            coverage_verified=True, review_record="audit/book-01.md")
        (self.root / "audit/book-01.md").write_text("Fixture acceptance evidence", encoding="utf-8")
        self.save()

    def test_empty_scaffold_cannot_export(self):
        self.save()
        with self.assertRaisesRegex(ValueError, "no accepted translation"):
            project.manuscript(project.inspect(self.root), [1])

    def test_verified_coverage_detects_missing_source_section(self):
        self.accept()
        self.manifest["books"][0]["expected_sections"].append("1.1.2")
        self.save()
        with self.assertRaisesRegex(ValueError, "expected coverage"):
            project.inspect(self.root)

    def test_incomplete_english_cannot_be_accepted(self):
        self.accept()
        self.section("latin", "1.1.2")
        self.manifest["books"][0]["expected_sections"].append("1.1.2")
        self.save()
        with self.assertRaisesRegex(ValueError, "complete alignment"):
            project.inspect(self.root)

    def test_duplicate_source_reference_rejected(self):
        self.accept()
        self.section("latin")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            project.inspect(self.root)

    def test_acceptance_requires_review_record(self):
        self.accept()
        (self.root / "audit/book-01.md").write_text("", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "nonempty review record"):
            project.inspect(self.root)

    def test_export_has_stable_note_keys(self):
        self.accept()
        text = project.manuscript(project.inspect(self.root), [1])
        self.assertIn("**1.1.1** Fixture text[^s1-1-1-n1]", text)
        self.assertIn("[^s1-1-1-n1]: (1.1.1) A fixture note.", text)

    def test_path_cannot_escape_repository(self):
        self.manifest["books"][0]["latin"] = "../outside.jsonl"
        self.save()
        with self.assertRaisesRegex(ValueError, "escapes project"):
            project.inspect(self.root)


if __name__ == "__main__":
    unittest.main()
