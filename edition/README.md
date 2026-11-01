# Cumulative reading draft 02

Twenty-seven complete numbered sections, eleven selections. The initial
eleven-section pilot is preserved; its voice and 6x9 design were approved by
the editor. Sixteen new sections develop rhetoric, dialectic, and history.
The new text has lead fidelity review; approval of the initial pilot does not
claim editor approval of the new translations.

## Reproduce and check

From the repository root, Python 3.12:

```powershell
python tools/assemble_reader.py
python tools/check_reader.py
python tools/project.py check
python tools/check_pilot.py
python -m unittest discover -s tests -v
```

PDF dependencies are pinned in requirements-print.txt. With the project venv:

```powershell
.venv\Scripts\python.exe tools/build_reader.py
.venv\Scripts\python.exe tools/check_reader_pdf.py
pdftoppm -r 110 -png output/pdf/isidore-selected-reader.pdf tmp/pdfs/reader
```

Inspect every rendered page. Automated text and embedded-font checks do not
certify layout. build.json pins PDF, inputs, and builder; pdf-qa.json records
automated checks; visual-review.md records the separately inspected build.

The manifest pins the four parent source/translation inputs, review evidence,
and task file. Source and English objects are preserved, ordered thematically.
Chapter scope and omissions are explicit. This reading PDF is not a final Lulu
interior; release needs a completed selection, production checks, a matching
cover, and a physical proof.
