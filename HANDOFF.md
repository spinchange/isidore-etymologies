# Handoff - 2026-11-01

## Current direction and approval

The editor now prefers an abridged, reader-interest edition. Favor complete,
self-contained sections; an interesting fragment can be included with the gap
clearly labeled and nothing supplied speculatively. Retain Latin key terms and
sound/shape-dependent etymologies. See editorial/SELECTION.md.

The editor approved the initial pilot's effortless prose, Latin usage, notes,
and 6x9 design. The first release remains abridged; a complete edition is a
possible later project. Rhetoric and the trivium have explicit priority.
See editorial/DECISIONS.md for approval and provisional extent planning.

## Source acquired

- All twenty Latin Library HTML books, both Lindsay 1911 print volumes, and
  an alternate volume-I PDF with metadata and DjVu XML (28 responses total)
  are downloaded in ignored latin/raw/. `python tools/acquire_sources.py
  --fetch` reproduces missing downloads; acquisition.json records hashes.
- The second volume is isidorihispalensisetymololindsay2, title inspected.
  The earlier Google scan is an additional copy of volume I, not volume II.
- Extraction currently yields 4,511 sections from 17 books. The three other
  raw books are available, with explicit issues in latin/provenance/import.json:
  V (misnumbered heading), X (unchaptered references), XI (letter l in a marker).
- No full-book coverage is certified. Unnumbered material and damaged/ASCII
  Greek are logged. Do not treat parser counts as the complete source inventory.
- Twenty-seven selected sections were checked against printed pages. The first eleven are preserved
  separately in pilot/source.json; restoration of Greek and punctuation is
  recorded in pilot/source-corrections.json. Corpus files stay uncollated.
- The next sixteen are in batches/002-trivium/source.json with separate
  corrections. The primary volume-I PDF omits I.40-41; alternate volume-I PDF
  page 102 supplies I.41. The missing scan pages are not silently filled from OCR.

## Pilot and continuation

The pilot tests I.29.1-5 (complete chapter on etymology), I.3.1-3 (writing),
XII.3.9 (ants), and XII.8.1-2 (bees). Scope is explicit at each selection.
Selections are ordered thematically; section order is kept inside each one.

Low-reasoning subagents supplied the extractor, first draft, bounded audit,
and workflow proposals. Drafts and task hashes remain in pilot/. Lead review
produces pilot/translation.json and audit/pilot-review.md. AI output is not
literally deterministic; section and hash checks are.

See pilot/README.md for the specimen build. The PDF is a design proof, not a
Lulu upload file or a physical proof. Domain, final title, extent, and binding
remain open. The editor's approval of voice, Latin/notes, and 6x9 page design
is now recorded in editorial/DECISIONS.md.

## Cumulative reading draft 02

Twenty-seven complete numbered sections in eleven thematic selections: the
pilot plus rhetoric II.1-3, II.4.1-4, dialectic II.22, the hand comparison
II.23.1-2, and history I.41. Scope labels distinguish complete chapters from
selected openings. See edition/README.md for assembly and PDF checks.

Two low-reasoning subagents supplied fixed-reference drafts. A bounded audit
also checks its own drafter's work and is not independent. Its dispatch-time
draft hashes were not captured; it quotes the intermediate wording observed.
The final proposals, task contracts, actual configuration, and hashes are in
batches/002-trivium/tasks.json. Lead review in audit/batch-002-review.md produces
the separate reviewed translation. AI prose is not deterministic; the reference,
whole-form, and hash checks are. The initial pilot remains unchanged.

edition/ assembles both batches without changing parent objects. Its manifest
pins inputs, review evidence, and task file; build.json and pdf-qa.json record
the PDF checks, with a separate visual review. Editor approval of the pilot
does not claim approval of new translations. No Lulu upload, physical proof,
domain registration, paid order, or website deployment has occurred.

Next: compact, intact selections on definition, argument, figures of speech,
and ambiguity. Collate each unit before dispatch. Keep room for living things
and ordinary objects in the wider thematic plan. The 25,000-35,000 translated
word range is a planning proposal, not an approved quota. Final title, extent,
binding, ancient attribution checks, historical apparatus, and proof remain open.

Run project.py check, check_pilot.py, check_reader.py, and the unit suite after
changes. Reassemble and rebuild when inputs change; inspect the latest PDF
after layout changes. Do not translate all twenty books merely because the
source is available.
