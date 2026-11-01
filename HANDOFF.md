# Handoff - 2026-11-01

## Current direction

The editor now prefers an abridged, reader-interest edition. Favor complete,
self-contained sections; an interesting fragment can be included with the gap
clearly labeled and nothing supplied speculatively. Retain Latin key terms and
sound/shape-dependent etymologies. See editorial/SELECTION.md.

## Source acquired

- All twenty Latin Library HTML books and both Lindsay 1911 print volumes
  are downloaded in ignored latin/raw/. `python tools/acquire_sources.py
  --fetch` reproduces missing downloads; acquisition.json records hashes.
- The second volume is isidorihispalensisetymololindsay2, title inspected.
  The earlier Google scan is an additional copy of volume I, not volume II.
- Extraction currently yields 4,511 sections from 17 books. The three other
  raw books are available, with explicit issues in latin/provenance/import.json:
  V (misnumbered heading), X (unchaptered references), XI (letter l in a marker).
- No full-book coverage is certified. Unnumbered material and damaged/ASCII
  Greek are logged. Do not treat parser counts as the complete source inventory.
- Eleven pilot sections were checked against printed pages. They are preserved
  separately in pilot/source.json; restoration of Greek and punctuation is
  recorded in pilot/source-corrections.json. Corpus files stay uncollated.

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
remain open. Next: editor responds to the voice, density of Latin/notes, and
6x9 page design, then choose a small next batch using the selection rubric.
Do not translate all twenty books merely because the source is available.
