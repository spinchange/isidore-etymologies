"""Verify specimen geometry, embedded fonts, and preservation of all paragraphs."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def compact(text):
    return "".join(text.split())


def main():
    pdf = ROOT / "output/pdf/isidore-selected-pilot.pdf"
    reader = PdfReader(pdf)
    translation = json.loads((ROOT / "pilot/translation.json").read_text(encoding="utf-8"))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    normalized = compact(text)
    fonts = set()
    for number, page in enumerate(reader.pages, 1):
        size = (float(page.mediabox.width), float(page.mediabox.height))
        if size != (432.0, 648.0):
            raise ValueError(f"Page {number}: wrong geometry {size}")
        for font in page["/Resources"]["/Font"].values():
            font = font.get_object()
            descriptor = font.get("/FontDescriptor")
            if not descriptor:
                raise ValueError(f"Unembedded font: {font.get('/BaseFont')}")
            descriptor = descriptor.get_object()
            if not any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                raise ValueError(f"Font has no embedded data: {font.get('/BaseFont')}")
            fonts.add(str(font["/BaseFont"]))
    for section in translation["sections"]:
        if section["ref"] not in text or compact(section["text"]) not in normalized:
            raise ValueError(f"Missing or changed paragraph in PDF: {section['ref']}")
        for note in section["notes"]:
            if compact(note) not in normalized:
                raise ValueError(f"Missing note in PDF: {section['ref']}")
    if "\ufffd" in text or "\x00" in text:
        raise ValueError("Replacement or null glyph in PDF text")
    build = json.loads((ROOT / "pilot/build.json").read_text(encoding="utf-8"))
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest != build["sha256"]:
        raise ValueError("PDF hash differs from recorded build")
    if hashlib.sha256((ROOT / "pilot/translation.json").read_bytes()).hexdigest() != build["translation_sha256"]:
        raise ValueError("Translation has changed since PDF build")
    if hashlib.sha256((ROOT / "tools/build_pilot.py").read_bytes()).hexdigest() != build["builder_sha256"]:
        raise ValueError("Typesetting script has changed since PDF build")
    record = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "pdf_sha256": digest,
              "pages": len(reader.pages), "page_size_points": [432, 648],
              "embedded_fonts": sorted(fonts), "paragraphs_preserved": len(translation["sections"]),
              "all_notes_preserved": True, "replacement_characters": False,
              "visual_review": "Separate lead inspection required after this build; automated text checks do not certify layout."}
    (ROOT / "pilot/qa.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
