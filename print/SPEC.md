# Lulu print edition — production plan, not a finished specification

Official requirements checked 2026-11-01:
https://help.lulu.com/en/support/solutions/articles/64000255519-pdf-creation-settings
https://help.lulu.com/en/support/solutions/articles/64000255583-tips-for-formatting-documents

Lulu describes a single interior PDF containing all front matter and blank
pages, in single-page layout. Its guidance calls for embedded fonts, 300 ppi
images, appropriate safety/gutter margins, and no trim or bleed marks. The
cover is a separate one-piece PDF containing back, spine, and front; the spine
depends on the actual interior page count and the selected product.

The generic settings page includes 0.125-inch bleed and margin figures. Use
the current template for the actual selected trim, binding, paper, and bleed
option before fixing page geometry. Do not reuse a companion book's spine
formula or claim generic settings certify this edition.

## Planned build

- A separate typesetting build from accepted text, not an EPUB-to-PDF shortcut.
- Stable section numbers, running heads, folios, real contents page numbers,
  and clearly linked notes in the source.
- Unicode font coverage for Latin, Greek, and any other scripts; include
  font licenses and inspect for substituted/missing glyphs.
- English-only versus parallel Latin/English and volume division remain open.
- Keep generated PDF files in ignored `print-build/`; attach vetted artifacts
  to versioned GitHub releases with checksums and build provenance.

## Release checks

1. Freeze accepted text and record the exact Git commit.
2. Verify selected product's dimensions, page limits, margins, color settings,
   bleed, and template against current Lulu guidance.
3. Generate interior; check dimensions, page count, font embedding, glyphs,
   contents, notes, cross-references, and text completeness.
4. Render and visually inspect pages, including each opener and difficult
   scripts, tables, footnotes, indexes, and intentionally blank pages.
5. Generate the cover from the finalized page count and Lulu template;
   inspect spine, bleed, safe areas, and any barcode requirements.
6. Use Lulu's validation/preview and order a physical proof when authorized.
7. Inspect the proof, correct defects, and only then approve a sale edition.

The scaffold provides no PDF generator or automatic Lulu upload. No payment,
proof order, ISBN purchase, or publication has been initiated.
