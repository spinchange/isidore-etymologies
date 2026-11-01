"""Check reader PDF geometry, embedded fonts, source preservation, and build hashes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
EDITION = ROOT / "edition"


def compact(text):
    return "".join(text.split())


def main():
    config = json.loads((EDITION / "manifest.json").read_text(encoding="utf-8"))
    translation_path = EDITION / "translation.json"
    translation = json.loads(translation_path.read_text(encoding="utf-8"))
    build = json.loads((EDITION / "build.json").read_text(encoding="utf-8"))
    pdf = ROOT / config["output"]
    reader = PdfReader(pdf)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    normalized = compact(text)
    fonts = set()
    for number, page in enumerate(reader.pages, 1):
        size = (float(page.mediabox.width), float(page.mediabox.height))
        if size != (432.0, 648.0):
            raise ValueError(f"Page {number}: wrong geometry {size}")
        for font_ref in page["/Resources"]["/Font"].values():
            font = font_ref.get_object()
            descriptor = font.get("/FontDescriptor")
            if not descriptor or not any(key in descriptor.get_object() for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                raise ValueError(f"Unembedded font: {font.get('/BaseFont')}")
            fonts.add(str(font["/BaseFont"]))
    for section in translation["sections"]:
        if section["ref"] not in text or compact(section["text"]) not in normalized:
            raise ValueError(f"Missing or changed paragraph in PDF: {section['ref']}")
        for note in section["notes"]:
            if compact(note) not in normalized:
                raise ValueError(f"Missing note in PDF: {section['ref']}")
    if "\ufffd" in text or "\x00" in text:
        raise ValueError("Replacement or null glyph in PDF text")
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest != build["output_sha256"]:
        raise ValueError("PDF hash differs from recorded build")
    for path_key, hash_value in build["inputs"].items():
        if hashlib.sha256((ROOT / path_key).read_bytes()).hexdigest() != hash_value:
            raise ValueError(f"Input has changed since build: {path_key}")
    builder_path = ROOT / build["builder"]
    if hashlib.sha256(builder_path.read_bytes()).hexdigest() != build["builder_sha256"]:
        raise ValueError("Builder has changed since PDF build")
    record = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "pdf_sha256": digest,
              "pages": len(reader.pages), "page_size_points": [432, 648], "embedded_fonts": sorted(fonts),
              "paragraphs_preserved": len(translation["sections"]), "all_notes_preserved": True,
              "replacement_characters": False,
              "visual_review": "Separate lead inspection required after this build; automated text checks do not certify layout."}
    (EDITION / "pdf-qa.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
