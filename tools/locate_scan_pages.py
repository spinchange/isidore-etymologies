"""Locate pilot phrases in scan OCR and render the relevant source pages."""
from pathlib import Path
import json
import subprocess
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tmp/pdfs"
OUT.mkdir(parents=True, exist_ok=True)
jobs = [
    ("I", "lindsay-1911-volume-I.pdf", ["De litteris commvnibvs", "De etymologia", "Cuius cognitio"]),
    ("II", "lindsay-1911-volume-II.pdf", ["Musio", "Apes dictae", "Formica dicta"]),
]
results = []
for volume, filename, phrases in jobs:
    pdf = ROOT / "latin/raw" / filename
    textfile = OUT / f"vol{volume}-locate.txt"
    subprocess.run(["pdftotext", "-layout", str(pdf), str(textfile)], check=True)
    pages = textfile.read_text(encoding="utf-8").split("\f")
    document = pdfium.PdfDocument(str(pdf))
    for page_number in ([72] if volume == "I" else [11]):
        document[page_number-1].render(scale=1.8).to_pil().save(OUT / f"source-{volume}-{page_number:03}.png")
    for phrase in phrases:
        matches = [i for i, page in enumerate(pages) if phrase.casefold() in page.casefold()]
        for index in matches:
            output = OUT / f"source-{volume}-{index+1:03}.png"
            document[index].render(scale=1.8).to_pil().save(output)
            results.append({"volume": volume, "phrase": phrase, "pdf_page": index+1, "image": str(output)})
    # Title/contact evidence, the first 12 pages at low resolution.
    from PIL import Image, ImageDraw
    sheet = Image.new("RGB", (900, 1200), "#dddddd")
    draw = ImageDraw.Draw(sheet)
    for i in range(min(12, len(document))):
        page = document[i].render(scale=.4).to_pil().convert("RGB")
        page.thumbnail((280, 265))
        x, y = (i % 3)*300, (i//3)*300
        sheet.paste(page, (x, y+25))
        draw.text((x+5, y+5), f"PDF page {i+1}", fill="black")
    sheet.save(OUT / f"source-{volume}-front.png")
(OUT / "scan-locations.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
