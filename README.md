# Isidore: Etymologies

A selected English translation of Isidore of Seville's *Etymologiae*, based on
W. M. Lindsay's Oxford critical edition (1911). The source has twenty books;
this project is an explicitly abridged edition for general readers.

**Status: sources acquired and an eleven-section translation/design pilot.**
Both print volumes and all twenty HTML books are acquired. Seventeen books
are extracted into working JSONL; three source/reference issues are logged.
Only the pilot Latin is collated; no whole-book completeness is claimed.
See [pilot/README.md](pilot/README.md) and [HANDOFF.md](HANDOFF.md).

The intended edition will be free to read and download, with a physical
edition sold through Lulu. Our original translation, notes, introduction,
editorial material, artwork, and project code are dedicated under CC0 1.0.
Third-party material retains its own rights; see [RIGHTS.md](RIGHTS.md).

Edited and produced by Chris Duffy. Translation and review contributors,
including the actual models used, will be recorded as work is performed.
The domain, final title, extent, and binding remain open. The pilot tests a
6x9-inch page. Latin is retained in the English when key terms or etymologies
would otherwise become invisible.

## Working commands

Python 3.12 or later; no third-party dependencies are needed for these commands.

```powershell
python tools/project.py status
python tools/project.py check
python -m unittest discover -s tests -v
python tools/project.py manuscript --books 1 --output build/book-01.md
```

The last command is the complete-book exporter: it refuses until Book 1 has verified source
coverage and an accepted translation. It produces manuscript Markdown,
not a Lulu-ready PDF. The abridgment pilot has a separate build described in
[pilot/README.md](pilot/README.md). Production EPUB and website builders remain future work.

## Layout

```text
latin/                  source record, 17 extracted books, provenance, ignored raw files
translation/            register; future accepted book-NN.jsonl
segments/manifest.json  twenty-book inventory and coverage/review status
prompts/                translation and review instructions
audit/                  rubric and pilot review decisions
editorial/              publication plan, domain ideas, decision log
print/                  Lulu production specification and release checklist
web/                    requirements for the future reading edition
docs/                   reserved GitHub Pages output (not built yet)
tools/project.py        inventory, alignment validation, manuscript assembly
tools/build_pilot.py    6x9 PDF specimen from the reviewed selection
pilot/                  collated excerpts, draft, audit, reviewed English, task hashes
output/pdf/             the rendered pilot artifact
tests/                  checks for coverage and publication guards
HANDOFF.md              current state and next work
```

Read [HANDOFF.md](HANDOFF.md), [TRANSLATION_WORKFLOW.md](TRANSLATION_WORKFLOW.md),
and [translation/CONVENTIONS.md](translation/CONVENTIONS.md) before continuing.
This project follows the organization of the companion Iliad, Odyssey, and
Lucretius projects in the agent journal, with prose section alignment in place
of verse-line alignment. Nothing from those projects has been copied here.

## Editions and releases

One accepted selection should feed the free website, aligned Latin/English data,
downloadable EPUB and PDF, and the Lulu interior. The print cover is a separate
file, sized only after the interior and binding are fixed. See
[print/SPEC.md](print/SPEC.md). The pilot is a design specimen, not a sale edition.

## Public domain

To the extent possible under law, the contributors waive copyright and related
rights in their original contributions to this project under
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
You may copy, modify, redistribute, and sell them without asking permission.
The dedication also applies to original editorial notes; attribution is welcome
but is not a condition of use. See [LICENSE](LICENSE) for the full legal text.
