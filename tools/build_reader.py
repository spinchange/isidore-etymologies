"""Build a configurable abridged reader PDF from a reviewed edition directory."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

from check_pilot import validate

ROOT = Path(__file__).resolve().parents[1]
EDITION = ROOT / "edition"


def markup(text, terms=()):
    """Escape literal text and italicize only explicitly supplied Latin forms."""
    terms = sorted({term for term in terms if term}, key=len, reverse=True)
    if not terms:
        return escape(text)
    pattern = re.compile(r"(?<!\w)(" + "|".join(map(re.escape, terms)) + r")(?!\w)")
    parts, last = [], 0
    for match in pattern.finditer(text):
        parts.extend((escape(text[last:match.start()]), "<i>" + escape(match.group()) + "</i>"))
        last = match.end()
    parts.append(escape(text[last:]))
    return "".join(parts)


def preserved_text(text):
    """Normalize PDF extraction whitespace while preserving all content characters."""
    return "".join(text.split())


def build():
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate,
                                   Paragraph, Spacer)

    source_path, translation_path, manifest_path = (EDITION / "source.json", EDITION / "translation.json", EDITION / "manifest.json")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    translation = json.loads(translation_path.read_text(encoding="utf-8"))
    config = json.loads(manifest_path.read_text(encoding="utf-8"))
    refs = validate(source, translation)
    required = ("title", "subtitle", "version", "front_note", "output")
    if any(key not in config for key in required) or not isinstance(config["front_note"], list):
        raise ValueError("edition/manifest.json needs title, subtitle, version, front_note (list), and output")
    output = (ROOT / config["output"]).resolve()
    if ROOT.resolve() not in output.parents:
        raise ValueError("Configured output must stay inside the repository")
    records = {row["ref"]: row for row in translation["sections"]}
    for name, filename in (("Gentium", "Gentium-Regular.ttf"), ("Gentium-Italic", "Gentium-Italic.ttf"), ("Gentium-Bold", "Gentium-Bold.ttf")):
        pdfmetrics.registerFont(TTFont(name, str(ROOT / "assets/fonts" / filename)))
    pdfmetrics.registerFontFamily("Gentium", normal="Gentium", italic="Gentium-Italic", bold="Gentium-Bold", boldItalic="Gentium-Bold")
    ink, quiet = colors.HexColor("#20201e"), colors.HexColor("#52524b")
    styles = {
        "body": ParagraphStyle("reader_body", fontName="Gentium", fontSize=11.3, leading=15, spaceAfter=9, textColor=ink, allowWidows=0, allowOrphans=0),
        "heading": ParagraphStyle("reader_heading", fontName="Gentium", fontSize=20, leading=24, spaceBefore=17, spaceAfter=5, textColor=ink, keepWithNext=True),
        "scope": ParagraphStyle("reader_scope", fontName="Gentium-Italic", fontSize=9, leading=12, spaceAfter=13, textColor=quiet, keepWithNext=True),
        "note": ParagraphStyle("reader_note", fontName="Gentium", fontSize=9.1, leading=12, spaceAfter=6, textColor=quiet, allowWidows=0, allowOrphans=0),
        "label": ParagraphStyle("reader_label", fontName="Gentium-Bold", fontSize=8.5, leading=11, spaceBefore=7, spaceAfter=5, textColor=quiet, keepWithNext=True),
        "title": ParagraphStyle("reader_title", fontName="Gentium", fontSize=32, leading=37, spaceAfter=16, textColor=ink),
        "subtitle": ParagraphStyle("reader_subtitle", fontName="Gentium-Italic", fontSize=15, leading=20, spaceAfter=24, textColor=quiet),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(output), pagesize=(6*inch, 9*inch), leftMargin=.78*inch, rightMargin=.65*inch,
                          topMargin=.7*inch, bottomMargin=.67*inch, title=config["title"],
                          author="Isidore of Seville; edited and produced by Chris Duffy")

    def page(canv, current):
        n = current.page
        # Even and odd templates use mirrored inside/outside margins without editing private frame geometry.
        left, right = ((.78, .65) if n % 2 else (.65, .78))
        canv.setFont("Gentium", 8.2)
        canv.setFillColor(quiet)
        if n > 1:
            canv.drawString(left*inch, 8.58*inch, config["title"].upper())
            canv.drawRightString(6*inch-right*inch, 8.58*inch, "SELECTIONS")
        canv.setFont("Gentium", 8.5)
        outside = (6-.65)*inch if n % 2 else .65*inch
        if n % 2:
            canv.drawRightString(outside, .35*inch, str(n))
        else:
            canv.drawString(outside, .35*inch, str(n))
        canv.setFont("Gentium-Italic", 7.5)
        canv.drawCentredString(3*inch, .35*inch, config["version"])

    # Two page templates supply mirrored margins using public Frame geometry.
    frames = [
        Frame(.78*inch, .67*inch, 6*inch-(.78+.65)*inch, 9*inch-(.7+.67)*inch, id="odd", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
        Frame(.65*inch, .67*inch, 6*inch-(.65+.78)*inch, 9*inch-(.7+.67)*inch, id="even", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
    ]
    doc.addPageTemplates([
        PageTemplate(id="odd", frames=[frames[0]], onPage=page, autoNextPageTemplate="even"),
        PageTemplate(id="even", frames=[frames[1]], onPage=page, autoNextPageTemplate="odd"),
    ])
    story = [Spacer(1, .6*inch), Paragraph("ISIDORE OF SEVILLE", styles["label"]), Spacer(1, .23*inch),
             Paragraph(escape(config["title"]), styles["title"]), Paragraph(escape(config["subtitle"]), styles["subtitle"]),
             Paragraph("An abridged reader in progress", styles["body"]), Spacer(1, .15*inch)]
    story.extend(Paragraph(escape(note), styles["body"]) for note in config["front_note"])
    story.append(Spacer(1, .16*inch))
    story.append(Paragraph("From Lindsay’s Oxford Latin edition, 1911.<br/>Original English and notes dedicated under CC0 1.0.<br/>Edited and produced by Chris Duffy.", styles["note"]))
    story.append(PageBreak())
    for selection in source["selections"]:
        story.extend((Paragraph(escape(selection["title"]), styles["heading"]), Paragraph(escape(selection["scope"]), styles["scope"])))
        notes = []
        for section in selection["sections"]:
            row = records[section["ref"]]
            terms = [term["display_form"] for term in row["terms"]]
            story.append(Paragraph(f'<font size="8.2" color="#52524b">{escape(row["ref"])}</font>  ' + markup(row["text"], terms), styles["body"]))
            notes.extend((row["ref"], note) for note in row["notes"])
        if notes:
            story.append(Paragraph("NOTES", styles["label"]))
            story.extend(Paragraph(f'<b>{escape(ref)}</b>  ' + markup(note), styles["note"]) for ref, note in notes)
        story.append(Spacer(1, 5))
    story.append(KeepTogether([
        Paragraph("TEXT AND EDITION", styles["label"]),
        Paragraph("Based on W. M. Lindsay, <i>Isidori Hispalensis episcopi Etymologiarum sive Originum libri XX</i>, Oxford, 1911, volumes I-II. The selected Latin was checked against the printed pages. The complete Latin and English for these selections, draft history, and review notes accompany the project repository.", styles["note"]),
        Paragraph('Modern biology note: University of Florida/IFAS, <i>European Honey Bee</i>, IN1005. <link href="https://ask.ifas.ufl.edu/publication/IN1005" color="#20201e">ask.ifas.ufl.edu/publication/IN1005</link>.', styles["note"]),
        Paragraph('Project: <link href="https://github.com/spinchange/isidore-etymologies" color="#20201e">github.com/spinchange/isidore-etymologies</link>. Reading draft for review; not a Lulu upload file or final sale edition.', styles["note"]),
    ]))

    def make_canvas(*args, **kwargs):
        kwargs["initialFontName"] = "Gentium"
        return canvas.Canvas(*args, **kwargs)
    doc.build(story, canvasmaker=make_canvas)
    record = {"built_at_utc": datetime.now(timezone.utc).isoformat(), "inputs": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (source_path, translation_path, manifest_path)},
              "output": output.relative_to(ROOT).as_posix(), "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
              "builder": Path(__file__).relative_to(ROOT).as_posix(), "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "pages": len(__import__("pypdf").PdfReader(output).pages), "sections": len(refs), "trim_inches": [6, 9], "body_pt": 11.3, "leading_pt": 15,
              "status": "reading draft; PDF requires separate visual review; not a Lulu upload file"}
    (EDITION / "build.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(output)


if __name__ == "__main__":
    build()
