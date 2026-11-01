import json
import hashlib
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_reader import validate_task_records, verify_file_hash


class ReaderTaskContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.refs = [f"ref-{i}" for i in range(16)]
        self.tasks = {"tasks": []}
        for name, refs in (("draft-oratory", self.refs[:10]),
                           ("draft-logic-history", self.refs[10:]),
                           ("bounded-draft-audit", self.refs)):
            output = {"checked_refs": refs} if name == "bounded-draft-audit" else {
                "sections": [{"ref": ref} for ref in refs]}
            output_path = self.root / f"{name}.json"
            output_path.write_text(json.dumps(output), encoding="utf-8")
            self.tasks["tasks"].append({"task": name, "assigned_refs": list(refs),
                                         "output": {"path": output_path.name}})

    def tearDown(self):
        self.temp.cleanup()

    def test_expected_partition_and_audit_refs_pass(self):
        validate_task_records(self.tasks, self.root, self.refs)

    def test_wrong_task_assignment_fails(self):
        self.tasks["tasks"][0]["assigned_refs"] = self.refs
        with self.assertRaisesRegex(ValueError, "assignments"):
            validate_task_records(self.tasks, self.root, self.refs)

    def test_output_must_match_assigned_refs(self):
        path = self.root / self.tasks["tasks"][1]["output"]["path"]
        path.write_text(json.dumps({"sections": [{"ref": "wrong"}]}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "output refs"):
            validate_task_records(self.tasks, self.root, self.refs)

    def test_tampered_recorded_hash_fails(self):
        path = self.root / "input.txt"
        path.write_text("source", encoding="utf-8")
        entry = {"path": path.name, "sha256": hashlib.sha256(b"different").hexdigest()}
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            verify_file_hash(entry, self.root)


if __name__ == "__main__":
    unittest.main()
