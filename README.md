# Isidore: Etymologies

A new English translation of Isidore of Seville's *Etymologiae*, based on
W. M. Lindsay's Oxford critical edition (1911), in twenty books.

**Status: scaffold only. No Latin has been imported and no translation has
been drafted or reviewed.**

The intended edition will be free to read and download, with a physical
edition sold through Lulu. Our original translation, notes, introduction,
editorial material, artwork, and project code are dedicated under CC0 1.0.
Third-party material retains its own rights; see [RIGHTS.md](RIGHTS.md).

Edited and produced by Chris Duffy. Translation and review contributors,
including the actual models used, will be recorded as work is performed.
The domain, final title, trim size, and division into print volumes remain open.

## Working commands

Python 3.12 or later; no third-party dependencies are needed for these commands.

```powershell
python tools/project.py status
python tools/project.py check
python -m unittest discover -s tests -v
python tools/project.py manuscript --books 1 --output build/book-01.md
```

The last command intentionally refuses until Book 1 has verified source
coverage and an accepted translation. It produces manuscript Markdown,
not a Lulu-ready PDF. PDF, EPUB, and website builders are future work.

## Layout

```text
latin/                  source record; future book-NN.jsonl and raw downloads
translation/            register; future accepted book-NN.jsonl
segments/manifest.json  twenty-book inventory and coverage/review status
prompts/                translation and review instructions
audit/                  rubric and future findings/decisions
editorial/              publication plan, domain ideas, decision log
print/                  Lulu production specification and release checklist
web/                    requirements for the future reading edition
docs/                   reserved GitHub Pages output (not built yet)
tools/project.py        inventory, alignment validation, manuscript assembly
tests/                  checks for coverage and publication guards
HANDOFF.md              current state and next work
```

Read [HANDOFF.md](HANDOFF.md), [TRANSLATION_WORKFLOW.md](TRANSLATION_WORKFLOW.md),
and [translation/CONVENTIONS.md](translation/CONVENTIONS.md) before continuing.
This project follows the organization of the companion Iliad, Odyssey, and
Lucretius projects in the agent journal, with prose section alignment in place
of verse-line alignment. Nothing from those projects has been copied here.

## Editions and releases

One accepted text should feed the free website, aligned Latin/English data,
downloadable EPUB and PDF, and the Lulu interior. The print cover is a separate
file, sized only after the interior and binding are fixed. See
[print/SPEC.md](print/SPEC.md). There are no publication-ready artifacts yet.

## Public domain

To the extent possible under law, the contributors waive copyright and related
rights in their original contributions to this project under
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
You may copy, modify, redistribute, and sell them without asking permission.
The dedication also applies to original editorial notes; attribution is welcome
but is not a condition of use. See [LICENSE](LICENSE) for the full legal text.
