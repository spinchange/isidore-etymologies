# Eleven-section pilot

The working title is *Words and the World: Selections from the Etymologies*.
It is a proposal for the editor, not a settled title or a domain decision.

The reviewed specimen is [the PDF](../output/pdf/isidore-selected-pilot.pdf).
It is five 6x9-inch pages, set in Gentium 7.000, 11.3-point body with 15-point
leading, mirrored inside/outside margins, small section references, italic
Latin in the English, and short notes after each selection. It is a design
proof, not a Lulu upload file, finished book, or physical print proof.

## Selection

| Editorial heading | Original references | Scope |
|---|---|---|
| What words reveal | I.29.1-5 | Complete chapter |
| Writing against forgetting | I.3.1-3 | Three complete sections of a longer chapter |
| Ants: crumbs and gold | XII.3.9 | One complete section |
| Bees: a city in wax | XII.8.1-2 | Two complete sections of a longer chapter |

There are no intra-section cuts and no fragments in this pilot. Future
interesting fragments remain eligible with a visible gap and explanation.
Ease guides the size of a production batch; reader interest guides inclusion.

## Files and review

- source.json: fixed collated Latin excerpts and scope/page references.
- source-corrections.json: Greek restoration and punctuation corrections.
- draft.json: original low-reasoning draft, preserved unchanged.
- draft-audit.json: bounded low-reasoning audit proposal, preserved unchanged.
- draft-task.json and audit-task.json: configured model/effort, prompts,
  exact section lists, and input/output hashes. These are task records, not
  guarantees of identical model outputs on a rerun.
- translation.json: lead-reviewed English and notes, plus exact Latin source
  forms and their displayed forms. Lemmas are explicit, not mistaken for the
  source's inflected wording.
- ../audit/pilot-review.md: decisions, scope of collation, and open questions.
- build.json and qa.json: output/input hashes, geometry, and checks.

The task source is a frozen input. Its recorded full-corpus file hashes describe
the moment it was prepared; later corpus reimports do not rewrite the preserved
task input. Only a new reviewed task should replace the pilot selection.

## Build

Core checks and source extraction need only Python's standard library. For PDF:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-print.txt
python tools/check_pilot.py
.venv\Scripts\python.exe tools/build_pilot.py
.venv\Scripts\python.exe tools/check_pilot_pdf.py
pdftoppm -scale-to 1300 -png output/pdf/isidore-selected-pilot.pdf tmp/pdfs/pilot
```

Inspect every rendered page after changes; text extraction cannot establish
layout quality. The latest five rendered pages were inspected by the lead.
PDF production follows the PDF skill's artifact-operation marker when used
inside Codex. The checker does not claim a physical Lulu proof was ordered.

For a quick text read, translation.json is the authority; section identifiers
and full prose are also searchable in the PDF. The paired-form check uses word
boundaries: iter hidden inside legiterae cannot satisfy an explicit iter term.

## Editorial choices to respond to

Voice and pace; how much Latin belongs in the paragraph; useful versus
repetitive notes; type size and measure; and whether these thematic groupings
make a useful entrance to Isidore. The next batch should be selected after this
response, not expanded automatically to all twenty books.
