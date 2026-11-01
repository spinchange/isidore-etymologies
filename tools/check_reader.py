"""Validate assembled reading-draft inputs against their reviewed parents."""
import hashlib
import json
from pathlib import Path

from check_pilot import validate
from assemble_reader import PARENTS, REVIEWS, SELECTION_IDS, ROOT, EDITION


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def verify_file_hash(item, root, label="Batch task hash mismatch"):
    actual = hashlib.sha256((root / item["path"]).read_bytes()).hexdigest()
    if actual != item["sha256"].lower():
        raise ValueError(f"{label}: {item['path']}")


def validate_task_records(tasks, root, batch_refs):
    expected = {
        "draft-oratory": batch_refs[:10],
        "draft-logic-history": batch_refs[10:],
        "bounded-draft-audit": batch_refs,
    }
    by_name = {task["task"]: task for task in tasks["tasks"]}
    if set(by_name) != set(expected):
        raise ValueError("Batch task names differ from the expected three task contracts")
    for name, refs in expected.items():
        task = by_name[name]
        if task["assigned_refs"] != refs:
            raise ValueError(f"Task assignments differ from expected contract: {name}")
        output_path = root / task["output"]["path"]
        output = json.loads(output_path.read_text(encoding="utf-8"))
        if name == "bounded-draft-audit":
            actual = output.get("checked_refs")
        else:
            actual = [section["ref"] for section in output.get("sections", [])]
        if actual != refs:
            raise ValueError(f"Task output refs differ from assignment: {name}")


def check_tasks(source_refs, manifest):
    expected_task_paths = ["batches/002-trivium/tasks.json"] if (ROOT / "batches/002-trivium/tasks.json").exists() else []
    recorded = [item["path"] for item in manifest["parent_task_files"]]
    if recorded != expected_task_paths:
        raise ValueError("Manifest parent task file list is out of date; rerun assemble_reader.py")
    if expected_task_paths:
        tasks_path = expected_task_paths[0]
        task_file_entry = manifest["parent_task_files"][0]
        verify_file_hash(task_file_entry, ROOT, "Manifest parent task file hash mismatch")
        tasks = read(tasks_path)
        if tasks.get("schema_version") != 1:
            raise ValueError("Unsupported tasks.json schema")
        if tasks["source"]["path"] != "batches/002-trivium/source.json":
            raise ValueError("Batch task source path differs from the reviewed source")
        for item in [tasks["source"]] + [f for task in tasks["tasks"] for f in task["instruction_files"] + [task["output"]]]:
            verify_file_hash(item, ROOT)
        batch_refs = [section["ref"] for selection in read("batches/002-trivium/source.json")["selections"] for section in selection["sections"]]
        audit = read("batches/002-trivium/draft-audit.json")
        if audit["checked_refs"] != batch_refs:
            raise ValueError("Batch audit checked_refs differ from source selection")
        validate_task_records(tasks, ROOT, batch_refs)


def main():
    source = read("edition/source.json")
    translation = read("edition/translation.json")
    manifest = read("edition/manifest.json")
    if manifest["selection_ids"] != SELECTION_IDS:
        raise ValueError("Manifest selection ID order differs from approved assembly order")
    for item in manifest["parent_inputs"]:
        if sha(item["path"]) != item["sha256"].lower():
            raise ValueError(f"Parent input hash mismatch: {item['path']}")
    if [item["path"] for item in manifest["parent_inputs"]] != PARENTS:
        raise ValueError("Manifest parent input list differs from the four expected files")
    parent_sources = {p: read(p) for p in (PARENTS[0], PARENTS[2])}
    selection_by_id = {selection["id"]: selection for p in (PARENTS[0], PARENTS[2]) for selection in parent_sources[p]["selections"]}
    expected_selections = [selection_by_id[sid] for sid in SELECTION_IDS]
    if source["selections"] != expected_selections:
        raise ValueError("Assembled source selections differ from reviewed parent objects")
    parent_translations = {p: read(p)["sections"] for p in (PARENTS[1], PARENTS[3])}
    translation_by_ref = {row["ref"]: row for rows in parent_translations.values() for row in rows}
    expected_refs = [section["ref"] for selection in expected_selections for section in selection["sections"]]
    if len(expected_refs) != 27 or translation["sections"] != [translation_by_ref[ref] for ref in expected_refs]:
        raise ValueError("Assembled translations differ from parent objects or selection order")
    refs = validate(source, translation)
    for item in manifest["review_evidence"]:
        if not (ROOT / item["path"]).is_file() or not (ROOT / item["path"]).read_text(encoding="utf-8").strip():
            raise ValueError(f"Review evidence missing or empty: {item['path']}")
        if sha(item["path"]) != item["sha256"].lower():
            raise ValueError(f"Review evidence hash mismatch: {item['path']}")
    if [item["path"] for item in manifest["review_evidence"]] != REVIEWS:
        raise ValueError("Manifest review evidence list differs from expected review records")
    for parent_translation in (read(PARENTS[1]), read(PARENTS[3])):
        review_path = parent_translation.get("review_record")
        if not review_path or not (ROOT / review_path).is_file() or not (ROOT / review_path).read_text(encoding="utf-8").strip():
            raise ValueError(f"Recorded review evidence missing: {review_path}")
    check_tasks(refs, manifest)
    print(f"OK: {len(refs)} refs in {len(source['selections'])} selections; parents, translations, reviews and task records match")


if __name__ == "__main__":
    main()
