"""Download exact source responses (optional) and record their hashes.

Raw files are ignored by Git. --fetch retrieves missing files only; this command
never refreshes an existing response silently. PDF scans are collation evidence.
"""
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "latin/raw"
SOURCES = [
    (f"latinlibrary-book-{n:02}.html", f"https://www.thelatinlibrary.com/isidore/{n}.shtml", "working Latin transcription; not collated")
    for n in range(1, 21)
] + [
    ("lindsay-1911-volume-I.pdf", "https://archive.org/download/isidori01isiduoft/isidori01isiduoft.pdf", "Lindsay 1911 volume I, books I-X; title and pilot pages inspected"),
    ("lindsay-1911-volume-II.pdf", "https://archive.org/download/isidorihispalensisetymololindsay2/isidorihispalensisetymololindsay2.pdf", "Lindsay 1911 volume II, books XI-XX; title and pilot pages inspected"),
    ("isidori01isiduoft-metadata.json", "https://archive.org/metadata/isidori01isiduoft", "archive metadata; public-domain label"),
    ("volume-II-metadata.json", "https://archive.org/metadata/isidorihispalensisetymololindsay2", "archive metadata; public-domain mark"),
    ("latinlibrary-about.html", "https://www.thelatinlibrary.com/about.html", "transcription provenance and public-domain statement"),
    ("lindsay-1911-google-volume.pdf", "https://archive.org/download/isidorihispalen00lindgoog/isidorihispalen00lindgoog.pdf", "Alternate volume-I scan; PDF page 102 collated for I.41"),
    ("isidorihispalen00lindgoog-metadata.json", "https://archive.org/metadata/isidorihispalen00lindgoog", "Alternate scan metadata, 1911, NOT_IN_COPYRIGHT"),
    ("google-ocr.xml", "https://archive.org/download/isidorihispalen00lindgoog/isidorihispalen00lindgoog_djvu.xml", "Page-indexed OCR used only to locate alternate scan page"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Download missing responses")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    items = []
    missing = []
    for filename, url, role in SOURCES:
        target = RAW / filename
        if args.fetch and not target.exists():
            request = urllib.request.Request(url, headers={"User-Agent": "IsidoreTranslationProject/0.1 (source acquisition)"})
            with urllib.request.urlopen(request, timeout=90) as response:
                data = response.read()
            target.write_bytes(data)
        if not target.is_file():
            missing.append(filename)
            continue
        data = target.read_bytes()
        if filename.endswith(".pdf") and not data.startswith(b"%PDF"):
            raise ValueError(f"Not a PDF response: {filename}")
        items.append({"path": str(target.relative_to(ROOT)).replace("\\", "/"),
                      "url": url, "role": role, "bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest(),
                      "local_file_mtime_utc": datetime.fromtimestamp(target.stat().st_mtime, timezone.utc).isoformat()})
    record = {"schema_version": 1, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
              "acquisition_date": "2026-11-01", "method": "Original responses downloaded with PowerShell Invoke-WebRequest; this script can reproduce missing downloads via urllib.",
              "missing": missing, "files": items}
    output = ROOT / "latin/provenance/acquisition.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {len(items)} files; {len(missing)} missing")
    return int(bool(missing))


if __name__ == "__main__":
    raise SystemExit(main())
