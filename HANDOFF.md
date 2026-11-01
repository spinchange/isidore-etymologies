# Handoff

## State at scaffold — 2026-11-01

- Twenty books inventoried; no Latin downloaded, collated, or segmented.
- No translated or accepted passages; no reviews completed.
- CC0 applies to all original project contributions, including notes.
- Python tools validate the inventory and aligned JSONL, report progress,
  and assemble accepted books into Markdown. They do not generate PDFs.
- Website, EPUB, print interior, cover, art, and domain are not built or chosen.
- Companion project conventions were read from the agent journal's Iliad,
  Odyssey, and Lucretius READMEs and Lucretius handoff/manifest.
- Validation: the inventory checker and seven coverage/export unit tests pass.
  A GitHub Actions workflow repeats these checks on pushes and pull requests.

## Next work

1. Acquire and identify both volumes of Lindsay's 1911 edition. Volume I is
   verified online; a direct volume-II scan still needs confirmation.
2. Record actual download URLs, dates, hashes, rights, and edition details.
3. Import working Latin with explicit references; collate a pilot against the
   scan, then establish the expected section inventory. Include a deliberate
   decision on prefatory letters and other material outside the twenty books.
4. Translate a short Book I pilot to settle register, wordplay presentation,
   notes, and the on-page Latin/English relationship with the editor.
5. Review and record the pilot; choose print format from real typeset pages.
6. Build the website, EPUB, and separate print pipeline from accepted content.

The manifest's expected_sections is null until coverage has actually been
established. Do not fill it from the English text or claim completeness merely
because the currently imported files align.
