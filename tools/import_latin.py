"""Deterministic extraction of numbered sections from saved Latin Library HTML."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import re
from datetime import datetime, timezone
from pathlib import Path

VERSION = "1.2.0"
ROOT = Path(__file__).resolve().parents[1]
SECTION = re.compile(r"\[(\d+)\]")
NAVIGATION_HREFS = {"isidore.html", "christian.html", "index.html", "classics.html"}
# Chapter headers in these files are uppercase Roman labels followed by an
# uppercase title and section [1]. Matching upper case is important: prose and
# cited Roman numerals also occur at the start of HTML paragraphs.
CHAPTER = re.compile(r"(?<![A-Z0-9])([IVXLCDM]+)\.\s+([A-ZÀ-Þ][^a-z\[\]]*?)(?=\s*\[1\])")


class ExtractionError(ValueError):
    pass


def decode_source(data: bytes) -> tuple[str, str]:
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16"), "utf-16"
    try:
        return data.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        # The supplied Latin Library snapshots contain cp1252 bytes. Keep the
        # original file untouched and make the decoding choice visible in provenance.
        return data.decode("cp1252"), "cp1252-fallback"


def extract_html(html: str, book: int) -> tuple[list[dict], list[dict], list[dict]]:
    class Paragraphs(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.blocks: list[str] = []
            self.parts: list[str] = []
            self.previous_was_br = False
            self.skip_navigation_link = False
        def flush(self):
            value = "".join(self.parts).strip()
            if value:
                self.blocks.append(value)
            self.parts = []
        def handle_starttag(self, tag, attrs):
            tag = tag.lower()
            if tag == "a":
                href = dict(attrs).get("href", "").rsplit("/", 1)[-1].lower()
                self.skip_navigation_link = href in NAVIGATION_HREFS
            elif tag == "p": self.flush()
            elif tag == "br" and not self.skip_navigation_link:
                if self.previous_was_br:
                    self.flush()
                else:
                    self.parts.append("\n")
                self.previous_was_br = True
        def handle_endtag(self, tag):
            tag = tag.lower()
            if tag == "p": self.flush()
            elif tag == "a": self.skip_navigation_link = False
        def handle_data(self, data):
            if self.skip_navigation_link:
                return
            if data.strip(): self.previous_was_br = False
            self.parts.append(data)
    tokenizer = Paragraphs()
    tokenizer.feed(html)
    tokenizer.flush()
    records: list[dict] = []
    chapters: list[dict] = []
    warnings: list[dict] = []
    active_chapter: int | None = None
    active_section: int | None = None
    active_text: list[str] = []
    previous: tuple[int, int] | None = None
    substantive_unassigned: list[str] = []

    def finish() -> None:
        nonlocal active_section, active_text, previous
        if active_section is None:
            return
        text = "\n".join(part for part in active_text if part).strip()
        if not text:
            raise ExtractionError(f"empty numbered content at {book}.{active_chapter}.{active_section}")
        key = (active_chapter or 0, active_section)
        if previous is not None and key <= previous:
            raise ExtractionError(f"duplicate or out-of-order reference {book}.{key[0]}.{key[1]}")
        records.append({"ref": f"{book}.{key[0]}.{key[1]}", "book": book,
                        "chapter": key[0], "section": key[1], "text": text})
        previous = key
        active_section = None
        active_text = []

    def process_section_text(text: str) -> None:
        nonlocal active_section, active_text
        matches = list(SECTION.finditer(text))
        if matches:
            if active_chapter is None:
                raise ExtractionError(f"numbered section before Roman chapter heading: {text[:100]}")
            prefix = text[:matches[0].start()].strip()
            if prefix:
                if active_section is not None:
                    active_text.append(prefix)
                else:
                    substantive_unassigned.append(prefix)
            for i, match in enumerate(matches):
                finish()
                active_section = int(match.group(1))
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                active_text = [text[match.end():end].strip()]
        elif active_section is not None:
            active_text.append(text)
        elif len(text) > 2 and not text.lower().startswith(("isidori hispalensis", "de ")):
            substantive_unassigned.append(text)

    for raw in tokenizer.blocks:
        text = re.sub(r"[ \t\xa0]+", " ", raw).strip()
        if not text:
            continue
        # <br> is meaningful in quoted verse: preserve each rendered line.
        pieces = [re.sub(r"\s+", " ", p).strip() for p in text.split("\n")]
        text = "\n".join(p for p in pieces if p)
        headings = list(CHAPTER.finditer(text))
        if headings:
            prefix = text[:headings[0].start()].strip()
            if prefix and active_section is not None:
                active_text.append(prefix)
            elif prefix and not prefix.upper().startswith(("DE ", "ISIDORI ", "ISIDORE ")):
                substantive_unassigned.append(prefix)
            for index, heading in enumerate(headings):
                finish()
                roman, title = heading.groups()
                chapter = roman_to_int(roman)
                if chapter <= 0 or (chapters and chapter <= chapters[-1]["chapter"]):
                    raise ExtractionError(f"duplicate or out-of-order chapter heading {roman}")
                active_chapter = chapter
                chapters.append({"book": book, "chapter": chapter, "roman": roman.upper(), "title": title.strip(" .]")})
                end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
                process_section_text(text[heading.end():end].strip())
        else:
            process_section_text(text)

    finish()
    if substantive_unassigned:
        warnings.append({"type": "unassigned-substantive-text", "count": len(substantive_unassigned),
                         "samples": substantive_unassigned[:20]})
    if not records:
        raise ExtractionError(f"no numbered sections found for book {book}")
    return records, chapters, warnings


def roman_to_int(value: str) -> int:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, char in enumerate(value.upper()):
        amount = values[char]
        total += -amount if i + 1 < len(value) and amount < values[value[i + 1].upper()] else amount
    return total


def import_book(book: int) -> dict:
    source = ROOT / "latin" / "raw" / f"latinlibrary-book-{book:02}.html"
    if not source.exists():
        raise ExtractionError(f"missing source file {source}")
    raw = source.read_bytes()
    html, encoding = decode_source(raw)
    records, chapters, warnings = extract_html(html, book)
    destination = ROOT / "latin" / f"book-{book:02}.jsonl"
    destination.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    return {"book": book, "source": source.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(), "encoding": encoding,
            "output": destination.relative_to(ROOT).as_posix(), "record_count": len(records),
            "chapter_count": len(chapters), "warnings": warnings, "chapters": chapters}


def _is_reviewed(entry: dict) -> bool:
    return (entry.get("status") not in {"not-started", "in-progress"}
            or entry.get("coverage_verified") is True
            or entry.get("review_record") is not None)


def _set_in_progress(entry: dict) -> None:
    entry["status"] = "in-progress"
    entry["expected_sections"] = None
    entry["coverage_verified"] = False


def merge_import_report(old_report: dict, results: list[dict], errors: list[dict], *,
                        all_books: bool, target_book: int | None,
                        blocked_books: set[int], reset_events: list[dict]) -> dict:
    old_imports = {item["book"]: item for item in old_report.get("imports", [])}
    if all_books:
        merged_imports = {book: record for book, record in old_imports.items() if book in blocked_books}
        merged_imports.update({record["book"]: {k: v for k, v in record.items() if k != "chapters"}
                               for record in results})
        merged_errors = {item["book"]: item for item in errors}
    else:
        merged_imports = dict(old_imports)
        merged_errors = {item["book"]: item for item in old_report.get("errors", [])}
        if target_book not in blocked_books:
            merged_imports.pop(target_book, None)
            merged_errors.pop(target_book, None)
            for result in results:
                merged_imports[target_book] = {k: v for k, v in result.items() if k != "chapters"}
        merged_errors.update({item["book"]: item for item in errors})
    return {"parser_version": VERSION, "imported_at_utc": datetime.now(timezone.utc).isoformat(),
            "imports": sorted(merged_imports.values(), key=lambda item: item["book"]),
            "errors": sorted(merged_errors.values(), key=lambda item: item["book"]),
            "status_resets": old_report.get("status_resets", []) + reset_events,
            "note": "Extraction counts are not collation or coverage verification."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--book", type=int, choices=range(1, 21))
    group.add_argument("--all", action="store_true")
    parser.add_argument("--reset-status", action="store_true",
                        help="explicitly clear review status for the selected --book only")
    args = parser.parse_args()
    if args.reset_status and args.book is None:
        parser.error("--reset-status requires --book and cannot be used with --all")
    books = range(1, 21) if args.all else [args.book]
    results = []
    errors = []
    blocked_books: set[int] = set()
    reset_events = []
    manifest_path = ROOT / "segments" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_entries = {item["book"]: item for item in manifest["books"]}
    old_report_path = ROOT / "latin" / "provenance" / "import.json"
    old_report = json.loads(old_report_path.read_text(encoding="utf-8")) if old_report_path.exists() else {}
    old_imports = {item["book"]: item for item in old_report.get("imports", [])}
    for book in books:
        entry = manifest_entries[book]
        if _is_reviewed(entry) and not (args.book == book and args.reset_status):
            blocked_books.add(book)
            source = ROOT / "latin" / "raw" / f"latinlibrary-book-{book:02}.html"
            raw = source.read_bytes() if source.exists() else b""
            errors.append({"book": book, "source": source.relative_to(ROOT).as_posix(),
                           "sha256": hashlib.sha256(raw).hexdigest(),
                           "error": "reviewed manifest entry left untouched; use --book N --reset-status to reimport"})
            continue
        if args.book == book and args.reset_status:
            reset_events.append({"book": book, "previous_manifest_entry": dict(entry),
                                 "previous_source_sha256": old_imports.get(book, {}).get("sha256")})
            entry["review_record"] = None
        try:
            results.append(import_book(book))
        except ExtractionError as exc:
            source = ROOT / "latin" / "raw" / f"latinlibrary-book-{book:02}.html"
            raw = source.read_bytes() if source.exists() else b""
            details = {
                5: "Source heading sequence has XXXVIII followed by XXIX; no Roman numeral correction inferred.",
                10: "Source begins numbered material without a Roman chapter heading; chapter numbering is unsupported here.",
                11: "Raw source uses [l] (lowercase L) for a numbered section after chapter II; kept ambiguous, not normalized to [1].",
            }
            errors.append({"book": book, "source": source.relative_to(ROOT).as_posix(),
                           "sha256": hashlib.sha256(raw).hexdigest(), "error": str(exc),
                           "source_issue": details.get(book, ""),
                           "stale_output": f"latin/book-{book:02}.jsonl" if (ROOT / "latin" / f"book-{book:02}.jsonl").exists() else None})
        _set_in_progress(entry)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    chapters_path = ROOT / "latin" / "chapters.json"
    existing = json.loads(chapters_path.read_text(encoding="utf-8")) if chapters_path.exists() else {}
    if args.all:
        existing = {str(book): value for book, value in existing.items() if int(book) in blocked_books}
    elif args.book not in blocked_books and not results:
        existing.pop(str(args.book), None)
    for result in results:
        existing[str(result["book"])] = result["chapters"]
    chapters_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    provenance_dir = ROOT / "latin" / "provenance"
    provenance_dir.mkdir(parents=True, exist_ok=True)
    report = merge_import_report(old_report, results, errors, all_books=args.all,
                                 target_book=args.book, blocked_books=blocked_books,
                                 reset_events=reset_events)
    (provenance_dir / "import.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"books": len(results), "sections": sum(r["record_count"] for r in results),
                      "warnings": sum(len(r["warnings"]) for r in results), "errors": len(errors)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
