import unittest
from tools.check_pilot import validate, whole_form


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.source = {"selections": [{"sections": [{"ref": "1.3.3", "latin": "Litterae legiterae iter legentibus."}]}]}
        self.translation = {"sections": [{"ref": "1.3.3", "text": "Letters give a path (iter).", "notes": [], "terms": [{"source_form": "iter", "display_form": "iter"}]}]}

    def test_wordplay_form_is_not_a_substring(self):
        self.assertFalse(whole_form("legiterae", "iter"))
        self.assertTrue(whole_form("a path (iter)", "iter"))

    def test_missing_selection_rejected(self):
        self.translation["sections"] = []
        with self.assertRaisesRegex(ValueError, "references"):
            validate(self.source, self.translation)

    def test_hidden_term_does_not_pass(self):
        self.translation["sections"][0]["text"] = "Letters are legiterae."
        with self.assertRaisesRegex(ValueError, "displayed Latin"):
            validate(self.source, self.translation)

    def test_exact_selection_and_term_pass(self):
        self.assertEqual(validate(self.source, self.translation), ["1.3.3"])


if __name__ == "__main__":
    unittest.main()
