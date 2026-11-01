"""Assemble fixed pilot source excerpts; apply explicitly collated corrections."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SELECTIONS = [
    {"id": "etymology", "title": "What words reveal", "refs": [f"1.29.{n}" for n in range(1, 6)], "volume": "I", "pdf_pages": [71, 72], "scope": "Complete chapter I.29"},
    {"id": "writing", "title": "Writing against forgetting", "refs": [f"1.3.{n}" for n in range(1, 4)], "volume": "I", "pdf_pages": [42], "scope": "Three complete numbered sections, I.3.1-3; the remainder of chapter I.3 is not included"},
    {"id": "ants", "title": "Ants: crumbs and gold", "refs": ["12.3.9"], "volume": "II", "pdf_pages": [64], "scope": "One complete numbered section, XII.3.9"},
    {"id": "bees", "title": "Bees: a city in wax", "refs": ["12.8.1", "12.8.2"], "volume": "II", "pdf_pages": [95], "scope": "Two complete numbered sections, XII.8.1-2; the remainder of chapter XII.8 is not included"},
]

corrections = [
    {"ref": "1.29.1", "old": "SUMBOLON", "new": "σύμβολον", "reason": "Restore Greek from Lindsay volume I, PDF page 71; Latin Library substitutes capital Latin letters."},
    {"ref": "1.29.3", "old": '"reges’', "new": "'reges'", "reason": "Normalize mismatched quotation marks to the printed quotation boundaries; I, PDF page 72."},
    {"ref": "1.29.4", "old": '"prudens’', "new": "'prudens'", "reason": "Normalize mismatched quotation marks; I, PDF page 72."},
    {"ref": "1.29.4", "old": '"garrulus’', "new": "'garrulus'", "reason": "Normalize mismatched quotation marks; I, PDF page 72."},
]


def main():
    records = {}
    hashes = {}
    for book in (1, 12):
        path = ROOT / f"latin/book-{book:02}.jsonl"
        hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        for line in path.read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            records[item["ref"]] = item
    result = []
    for selection in SELECTIONS:
        row = dict(selection)
        row["sections"] = []
        for ref in row["refs"]:
            text = records[ref]["text"]
            for correction in corrections:
                if correction["ref"] == ref:
                    if correction["old"] not in text:
                        raise ValueError(f"Expected correction input missing at {ref}")
                    text = text.replace(correction["old"], correction["new"])
            row["sections"].append({"ref": ref, "latin": text})
        result.append(row)
    output = {"schema_version": 1, "base_edition": "Lindsay (Oxford, 1911)",
              "status": "pilot Latin collated against printed pages; full corpus not collated",
              "source_hashes": hashes, "selections": result}
    (ROOT / "pilot/source.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "pilot/source-corrections.json").write_text(json.dumps(corrections, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {sum(len(s['refs']) for s in result)} pilot sections")


if __name__ == "__main__":
    main()
