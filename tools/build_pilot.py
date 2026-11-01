"""Typeset the reviewed selection as a 6x9-inch design proof, not a sale PDF."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                               PageTemplate, Paragraph, Spacer)

from check_pilot import validate, check_tasks

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/pdf/isidore-selected-pilot.pdf"


def markup(text, terms=()):
    # Original fields are literal text; only our own escaped italic spans are markup.
    terms = sorted(set(terms), key=len, reverse=True)
    if not terms:
        return escape(text)
    pattern = re.compile(r"(?<!\w)(" + "|".join(map(re.escape, terms)) + r")(?!\w)")
    pieces, last = [], 0
    for match in pattern.finditer(text):
        pieces.extend([escape(text[last:match.start()]), "<i>" + escape(match.group()) + "</i>"])
        last = match.end()
    pieces.append(escape(text[last:]))
    return "".join(pieces)


def build():
    source_path = ROOT / "pilot/source.json"
    text_path = ROOT / "pilot/translation.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    translation = json.loads(text_path.read_text(encoding="utf-8"))
    validate(source, translation)
    check_tasks()
    records = {row["ref"]: row for row in translation["sections"]}
    for name, filename in [("Gentium", "Gentium-Regular.ttf"), ("Gentium-Italic", "Gentium-Italic.ttf"), ("Gentium-Bold", "Gentium-Bold.ttf")]:
        pdfmetrics.registerFont(TTFont(name, str(ROOT / "assets/fonts" / filename)))
    pdfmetrics.registerFontFamily("Gentium", normal="Gentium", italic="Gentium-Italic", bold="Gentium-Bold", boldItalic="Gentium-Bold")
    ink = colors.HexColor("#20201e")
    quiet = colors.HexColor("#52524b")
    styles = {
        "body": ParagraphStyle("body", fontName="Gentium", fontSize=11.3, leading=15, spaceAfter=9, textColor=ink, allowWidows=0, allowOrphans=0),
        "heading": ParagraphStyle("heading", fontName="Gentium", fontSize=20, leading=24, spaceBefore=17, spaceAfter=5, textColor=ink, keepWithNext=True),
        "scope": ParagraphStyle("scope", fontName="Gentium-Italic", fontSize=9, leading=12, spaceAfter=13, textColor=quiet, keepWithNext=True),
        "note": ParagraphStyle("note", fontName="Gentium", fontSize=9.1, leading=12, spaceAfter=6, textColor=quiet, allowWidows=0, allowOrphans=0),
        "label": ParagraphStyle("label", fontName="Gentium-Bold", fontSize=8.5, leading=11, spaceBefore=7, spaceAfter=5, textColor=quiet, keepWithNext=True),
        "title": ParagraphStyle("title", fontName="Gentium", fontSize=32, leading=37, spaceAfter=16, textColor=ink),
        "subtitle": ParagraphStyle("subtitle", fontName="Gentium-Italic", fontSize=15, leading=20, spaceAfter=24, textColor=quiet),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(OUT), pagesize=(6*inch, 9*inch), leftMargin=.78*inch,
                          rightMargin=.65*inch, topMargin=.7*inch, bottomMargin=.67*inch,
                          title="Isidore: Words and the World - Selected Etymologies (Pilot)",
                          author="Isidore of Seville; translation pilot produced with Codex; editor Chris Duffy")

    def page(canv, current):
        page_number = current.page
        # Mirror inside and outside margins for a spread.
        left = (.78 if page_number % 2 else .65)*inch
        current_frame = current.pageTemplate.frames[0]
        current_frame._x1 = left
        current_frame._geom()
        canv.setFont("Gentium", 8.2)
        canv.setFillColor(quiet)
        if page_number > 1:
            canv.drawString(left, 8.58*inch, "ISIDORE / WORDS AND THE WORLD")
            canv.drawRightString(6*inch-(.65 if page_number % 2 else .78)*inch, 8.58*inch, "SELECTIONS")
        canv.setFont("Gentium", 8.5)
        outside = (6-.65)*inch if page_number % 2 else .65*inch
        if page_number % 2:
            canv.drawRightString(outside, .35*inch, str(page_number))
        else:
            canv.drawString(outside, .35*inch, str(page_number))
        canv.setFont("Gentium-Italic", 7.5)
        canv.drawCentredString(3*inch, .35*inch, "Translation and design pilot / November 2026")

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="reading", frames=[frame], onPage=page))
    story = [Spacer(1, .6*inch), Paragraph("ISIDORE OF SEVILLE", styles["label"]),
             Spacer(1, .23*inch), Paragraph("Words and<br/>the World", styles["title"]),
             Paragraph("Selections from the Etymologies", styles["subtitle"]),
             Paragraph("A translation and page-design pilot", styles["body"]),
             Spacer(1, .15*inch)]
    front = [
        "Words can explain a river, preserve an absent voice, or turn a hive into an army. These selections explore how Isidore connects the names of things with the world he describes.",
        "This is an abridged edition in progress. The pilot contains eleven complete numbered sections in four selections. Only the first selection is a complete chapter. The headings are ours; the references retain Isidore’s organization.",
        "The English carries the explanation. Italic Latin stays beside it where a key term or the sound and shape of a word matter. Brief notes distinguish editorial explanation from Isidore’s account.",
    ]
    story.extend(Paragraph(escape(text), styles["body"]) for text in front)
    story.extend([Spacer(1, .16*inch), Paragraph("From Lindsay’s Oxford Latin edition, 1911.<br/>Original English and notes dedicated under CC0 1.0.<br/>Edited and produced by Chris Duffy.", styles["note"]), PageBreak()])
    for selection in source["selections"]:
        story.append(Paragraph(escape(selection["title"]), styles["heading"]))
        story.append(Paragraph(escape(selection["scope"]), styles["scope"]))
        notes = []
        for section in selection["sections"]:
            row = records[section["ref"]]
            terms = [term["display_form"] for term in row["terms"]]
            body = f'<font size="8.2" color="#52524b">{row["ref"]}</font>  ' + markup(row["text"], terms)
            story.append(Paragraph(body, styles["body"]))
            for note in row["notes"]:
                notes.append((row["ref"], note))
        if notes:
            story.append(Paragraph("NOTES", styles["label"]))
            for ref, note in notes:
                story.append(Paragraph(f'<b>{ref}</b>  ' + markup(note), styles["note"]))
        story.append(Spacer(1, 5))
    story.append(Paragraph("TEXT AND EDITION", styles["label"]))
    story.append(Paragraph("Based on W. M. Lindsay, <i>Isidori Hispalensis episcopi Etymologiarum sive Originum libri XX</i>, Oxford, 1911, volumes I-II. The selected Latin was checked against the printed pages. The complete Latin and English for these selections, draft history, and review notes accompany the project repository.", styles["note"]))
    story.append(Paragraph('Modern biology note: University of Florida/IFAS, <i>European Honey Bee</i>, IN1005. <link href="https://ask.ifas.ufl.edu/publication/IN1005" color="#20201e">ask.ifas.ufl.edu/publication/IN1005</link>.', styles["note"]))
    story.append(Paragraph('Project: <link href="https://github.com/spinchange/isidore-etymologies" color="#20201e">github.com/spinchange/isidore-etymologies</link>. Working title and layout; not a Lulu upload file or a final sale edition.', styles["note"]))
    def make_canvas(*args, **kwargs):
        kwargs["initialFontName"] = "Gentium"
        return canvas.Canvas(*args, **kwargs)
    doc.build(story, canvasmaker=make_canvas)
    record = {"built_at_utc": datetime.now(timezone.utc).isoformat(), "output": str(OUT.relative_to(ROOT)).replace("\\", "/"),
              "sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
              "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
              "translation_sha256": hashlib.sha256(text_path.read_bytes()).hexdigest(),
              "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "trim_inches": [6, 9], "body_pt": 11.3, "leading_pt": 15,
              "status": "design-proof; visual QA required; not a Lulu upload file"}
    (ROOT / "pilot/build.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    build()
