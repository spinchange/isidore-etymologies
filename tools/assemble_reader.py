"""Assemble the reviewed pilot and trivium batch into the reading-draft inputs."""
import hashlib
import json
from pathlib import Path

from check_pilot import validate

ROOT = Path(__file__).resolve().parents[1]
EDITION = ROOT / "edition"
SELECTION_IDS = ["etymology", "writing", "history", "rhetoric", "rhetoric-learning",
                 "orator", "persuasion", "dialectic", "fist-palm", "ants", "bees"]
PARENTS = ["pilot/source.json", "pilot/translation.json",
           "batches/002-trivium/source.json", "batches/002-trivium/translation.json"]
REVIEWS = ["audit/pilot-review.md", "audit/batch-002-review.md"]


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def assemble():
    parent_data = {p: json.loads((ROOT / p).read_text(encoding="utf-8")) for p in PARENTS}
    source_by_id = {}
    for path in (PARENTS[0], PARENTS[2]):
        for selection in parent_data[path]["selections"]:
            if selection["id"] in source_by_id:
                raise ValueError(f"Duplicate parent selection ID: {selection['id']}")
            source_by_id[selection["id"]] = selection
    if set(source_by_id) != set(SELECTION_IDS):
        raise ValueError(f"Selection IDs differ from requested set: {sorted(source_by_id)}")
    selections = [source_by_id[sid] for sid in SELECTION_IDS]
    translations = {}
    for path in (PARENTS[1], PARENTS[3]):
        for section in parent_data[path]["sections"]:
            if section["ref"] in translations:
                raise ValueError(f"Duplicate parent translation reference: {section['ref']}")
            translations[section["ref"]] = section
    expected_refs = [s["ref"] for sel in selections for s in sel["sections"]]
    actual_refs = [row["ref"] for row in translations.values()]
    if set(expected_refs) != set(actual_refs) or len(expected_refs) != 27:
        raise ValueError(f"Expected 27 matching unique references, found {len(expected_refs)} selected")
    source = {"schema_version": 1, "base_edition": "Lindsay (Oxford, 1911)",
              "status": "reviewed selections assembled for abridged reading draft",
              "source_hashes": {**parent_data[PARENTS[0]]["source_hashes"], **parent_data[PARENTS[2]]["source_hashes"]},
              "selections": selections}
    translation = {"schema_version": 1, "status": "lead-reviewed-reading-draft-input",
                   "license": "CC0-1.0 for original English and notes; source Latin public domain",
                   "source_file": "edition/source.json", "review_record": REVIEWS[0],
                   "editorial_note": "A thematic abridgment assembled from reviewed selections. It is incomplete by design; Latin remains beside English where a term, sound, or word shape matters.",
                   "sections": [translations[ref] for ref in expected_refs]}
    validate(source, translation)
    manifest = {"title": "Words and the World", "subtitle": "Selections from the Etymologies",
                "version": "Reading draft 02", "output": "output/pdf/isidore-selected-reader.pdf",
                "front_note": [
                    "This abridged reader brings together selections on words, writing, memory, history, rhetoric, and reasoning. It is thematic and incomplete: the headings are editorial, and gaps between selections are intentional.",
                    "The English carries the explanation. Latin forms remain visible where an argument depends on their sound, spelling, or word shape. The selected passages preserve complete numbered sections; notes clarify editorial brackets and ancient claims. This is a reading draft under review.",
                ],
                "selection_ids": SELECTION_IDS,
                "parent_inputs": [{"path": p, "sha256": digest(p)} for p in PARENTS],
                "review_evidence": [{"path": p, "sha256": digest(p)} for p in REVIEWS],
                "parent_task_files": []}
    tasks_path = ROOT / "batches/002-trivium/tasks.json"
    if tasks_path.exists():
        manifest["parent_task_files"].append({"path": "batches/002-trivium/tasks.json", "sha256": digest("batches/002-trivium/tasks.json")})
    write_json(EDITION / "source.json", source)
    write_json(EDITION / "translation.json", translation)
    write_json(EDITION / "manifest.json", manifest)
    print(f"Assembled {len(expected_refs)} sections in {len(selections)} selections")


if __name__ == "__main__":
    assemble()
