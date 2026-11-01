"""Check the selected pilot's coverage, exact term forms, and preserved tasks."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def whole_form(text, term):
    return bool(re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text))


def validate(source, translation):
    expected = [item["ref"] for selection in source["selections"] for item in selection["sections"]]
    actual = [item["ref"] for item in translation["sections"]]
    if not expected or len(set(expected)) != len(expected) or actual != expected:
        raise ValueError("Pilot selection references must match exactly once, in the assigned order")
    latin = {item["ref"]: item["latin"] for selection in source["selections"] for item in selection["sections"]}
    for item in translation["sections"]:
        ref = item["ref"]
        if not isinstance(item.get("text"), str) or not item["text"].strip():
            raise ValueError(f"{ref}: empty translation")
        if not isinstance(item.get("notes"), list) or any(not isinstance(n, str) or not n.strip() for n in item["notes"]):
            raise ValueError(f"{ref}: invalid notes")
        for term in item["terms"]:
            if not term["source_form"] or not whole_form(latin[ref], term["source_form"]):
                raise ValueError(f"{ref}: source term missing as a whole form: {term['source_form']}")
            if not term["display_form"] or not whole_form(item["text"], term["display_form"]):
                raise ValueError(f"{ref}: displayed Latin term missing: {term['display_form']}")
    return expected


def check_tasks(root=ROOT):
    draft = json.loads((root / "pilot/draft-task.json").read_text(encoding="utf-8"))
    for file_key, hash_key in (("source_file", "source_sha256"), ("draft_file", "draft_sha256")):
        data = (root / draft[file_key]).read_bytes()
        if hashlib.sha256(data).hexdigest() != draft[hash_key]:
            raise ValueError(f"Preserved task input/output hash mismatch: {draft[file_key]}")
    if hashlib.sha256(draft["prompt"].encode()).hexdigest() != draft["prompt_sha256"]:
        raise ValueError("Draft task prompt hash mismatch")
    audit = json.loads((root / "pilot/audit-task.json").read_text(encoding="utf-8"))
    for item in audit["inputs"] + [audit["output"]]:
        digest = hashlib.sha256((root / item["path"]).read_bytes()).hexdigest()
        if digest != item["sha256"].lower():
            raise ValueError(f"Audit task file hash mismatch: {item['path']}")
    if hashlib.sha256(audit["prompt"].encode()).hexdigest() != audit["prompt_sha256"].lower():
        raise ValueError("Audit task prompt hash mismatch")
    for record in (draft, audit):
        if (root / record["prompt_file"]).read_text(encoding="utf-8").strip() != record["prompt"]:
            raise ValueError("Archived dispatch prompt differs from task record")
    source = json.loads((root / "pilot/source.json").read_text(encoding="utf-8"))
    refs = [s["ref"] for selection in source["selections"] for s in selection["sections"]]
    checked = json.loads((root / "pilot/draft-audit.json").read_text(encoding="utf-8"))["checked_refs"]
    if draft["assigned_refs"] != refs or audit["section_refs"] != refs or checked != refs:
        raise ValueError("Task section assignments differ from the fixed selection")


def main():
    source = json.loads((ROOT / "pilot/source.json").read_text(encoding="utf-8"))
    translation = json.loads((ROOT / "pilot/translation.json").read_text(encoding="utf-8"))
    refs = validate(source, translation)
    check_tasks()
    if translation["status"] != "editorially-reviewed-pilot":
        raise ValueError("Expected lead-reviewed pilot status")
    if not (ROOT / translation["review_record"]).read_text(encoding="utf-8").strip():
        raise ValueError("Pilot review record missing")
    print(f"OK: {len(refs)} selected sections, exact paired forms, preserved draft/input/prompt hashes")


if __name__ == "__main__":
    main()
