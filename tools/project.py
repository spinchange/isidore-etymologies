"""Inventory and publication guards for the Isidore project (standard library)."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def local_path(root, value):
    if not isinstance(value, str) or not value:
        raise ValueError("File paths must be nonempty strings")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes project: {value}")
    return path


def reference(value, book):
    if not isinstance(value, str) or not re.fullmatch(r"[1-9]\d*\.[1-9]\d*\.[1-9]\d*", value):
        raise ValueError(f"Invalid numbered section: {value!r}")
    key = tuple(map(int, value.split(".")))
    if key[0] != book:
        raise ValueError(f"Wrong book in reference {value}")
    return key


def read_records(path, book, english=False):
    records = []
    if not path.exists():
        return records
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError("Expected a section object")
            reference(record.get("ref"), book)
            if not isinstance(record.get("text"), str) or not record["text"].strip():
                raise ValueError("Section text must be nonempty")
            if english:
                notes = record.get("notes")
                if not isinstance(notes, list) or any(not isinstance(n, str) or not n.strip() for n in notes):
                    raise ValueError("English sections require notes: a list of nonempty strings")
            records.append(record)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"{path.name}:{line_number}: {exc}") from exc
    refs = [r["ref"] for r in records]
    if len(set(refs)) != len(refs):
        raise ValueError(f"Duplicate references in {path.name}")
    if refs != sorted(refs, key=lambda ref: reference(ref, book)):
        raise ValueError(f"Out-of-order references in {path.name}")
    return records


def inspect(root=ROOT):
    manifest = json.loads((root / "segments/manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported manifest schema")
    books = manifest.get("books", [])
    if (not isinstance(books, list) or any(not isinstance(b, dict) for b in books)
            or [b.get("book") for b in books] != list(range(1, 21))
            or any(type(b.get("book")) is not int for b in books)):
        raise ValueError("Manifest must inventory Books 1-20 exactly once, in order")
    result = []
    for book in books:
        number = book["book"]
        status = book.get("status")
        if status not in {"not-started", "in-progress", "accepted"}:
            raise ValueError(f"Book {number}: unknown status")
        if type(book.get("coverage_verified")) is not bool:
            raise ValueError(f"Book {number}: coverage_verified must be boolean")
        latin = read_records(local_path(root, book.get("latin")), number)
        english = read_records(local_path(root, book.get("translation")), number, english=True)
        source_refs = [r["ref"] for r in latin]
        english_refs = [r["ref"] for r in english]
        if not set(english_refs).issubset(source_refs):
            raise ValueError(f"Book {number}: English has references absent from Latin")
        if status == "not-started" and (latin or english):
            raise ValueError(f"Book {number}: imported content cannot be not-started")
        expected = book.get("expected_sections")
        if expected is not None:
            if not isinstance(expected, list) or not expected:
                raise ValueError(f"Book {number}: expected_sections must be null or a nonempty list")
            keys = [reference(ref, number) for ref in expected]
            if keys != sorted(set(keys)):
                raise ValueError(f"Book {number}: expected references must be unique and ordered")
        if book["coverage_verified"] and (not expected or source_refs != expected):
            raise ValueError(f"Book {number}: verified Latin does not match expected coverage")
        if status == "accepted":
            if not book["coverage_verified"] or not latin or source_refs != english_refs:
                raise ValueError(f"Book {number}: acceptance requires verified, complete alignment")
            review = local_path(root, book.get("review_record"))
            if not review.is_file() or not review.read_text(encoding="utf-8").strip():
                raise ValueError(f"Book {number}: acceptance requires a nonempty review record")
        result.append((book, latin, english))
    return result


def literal(value):
    """Escape literal text fields for manuscript Markdown."""
    return re.sub(r"([\\`*_{}\[\]<>#])", r"\\\1", value)


def manuscript(inventory, selected):
    if not selected or len(set(selected)) != len(selected):
        raise ValueError("Select each requested book once")
    lookup = {b["book"]: (b, en) for b, _, en in inventory}
    parts = ["# Isidore: Etymologies", "Manuscript export — not a print-ready PDF.",
             "Original translation and notes: CC0 1.0. Base Latin edition: Lindsay (1911)."]
    for number in sorted(selected):
        if number not in lookup or lookup[number][0]["status"] != "accepted":
            raise ValueError(f"Book {number}: no accepted translation ready for export")
        _, english = lookup[number]
        parts.append(f"## Book {number}")
        notes = []
        for record in english:
            markers = []
            for index, note in enumerate(record["notes"], 1):
                key = f"s{record['ref'].replace('.', '-')}-n{index}"
                markers.append(f"[^{key}]")
                notes.append(f"[^{key}]: ({record['ref']}) {literal(note)}")
            parts.append(f"**{record['ref']}** {literal(record['text'])}" + "".join(markers))
        if notes:
            parts.append("\n\n".join(notes))
    return "\n\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    commands.add_parser("status")
    export = commands.add_parser("manuscript")
    export.add_argument("--books", nargs="+", type=int, default=list(range(1, 21)))
    export.add_argument("--output", type=Path, default=Path("build/etymologies.md"))
    args = parser.parse_args()
    try:
        inventory = inspect()
        if args.command == "check":
            print("OK: 20-book inventory and current alignment valid; this does not certify editorial completeness.")
        elif args.command == "status":
            for book, latin, english in inventory:
                expected = book["expected_sections"]
                count = str(len(expected)) if expected is not None else "unknown"
                print(f"Book {book['book']:02}: {book['status']:11} Latin={len(latin)} English={len(english)} expected={count}")
        else:
            text = manuscript(inventory, args.books)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
            print(f"Wrote {args.output} (manuscript only)")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
