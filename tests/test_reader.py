import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_reader import markup, preserved_text


class ReaderMarkupTests(unittest.TestCase):
    def test_markup_escapes_literal_paragraph_and_italicizes_term(self):
        self.assertEqual(markup("A & B; apis, apicula.", ["apis"]), "A &amp; B; <i>apis</i>, apicula.")

    def test_term_matching_respects_word_boundaries(self):
        self.assertEqual(markup("Apis apis-api apiary", ["apis"]), "Apis <i>apis</i>-api apiary")

    def test_preservation_normalizes_only_whitespace(self):
        self.assertEqual(preserved_text("a b\n c—d"), "abc—d")


if __name__ == "__main__":
    unittest.main()
