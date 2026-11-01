# Latin source record

## Base and acquisition

Isidore of Seville. *Isidori Hispalensis episcopi Etymologiarum sive Originum
libri XX*. Edited by W. M. Lindsay. Oxford: Clarendon Press, 1911. Two volumes.

## Located online — 2026-11-01

- LacusCurtius: https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Isidore/home.html
  Its introduction identifies Lindsay (Oxford, 1911) and reports that all
  twenty books have been proofread. A useful working transcription; still
  collate readings relevant to the translation against the printed edition.
- Latin Library: https://www.thelatinlibrary.com/isidore.html
  Index of twenty HTML books. A second working transcription, not evidence
  of an independent manuscript witness.
- Verified volume I: https://archive.org/details/isidori01isiduoft
  Publication 1911; language Latin; publisher Clarendon; marked Public Domain.
  PDF: https://archive.org/download/isidori01isiduoft/isidori01isiduoft.pdf
  OCR: https://archive.org/stream/isidori01isiduoft/isidori01isiduoft_djvu.txt
- Verified volume II: https://archive.org/details/isidorihispalensisetymololindsay2
  Metadata identifies 1911 and volume 2 with a Public Domain Mark. The title
  page (PDF page 11) reads TOMVS II / LIBROS XI-XX CONTINENS. Inspected visually.
  PDF: https://archive.org/download/isidorihispalensisetymololindsay2/isidorihispalensisetymololindsay2.pdf
- Additional volume-I copy: https://archive.org/details/isidorihispalen00lindgoog
  OCR includes the editor's volume-I preface. Not used as the volume-II source.

The guessed identifier `isidori02isiduoft` returned Item cannot be found and
must not be used as a verified source. The volume-II record above resolves
the earlier gap. LacusCurtius could not be retrieved for local acquisition;
the working HTML corpus is from Latin Library, not a LacusCurtius download.

## Acquired files and reproducibility

`latin/provenance/acquisition.json` records 25 original responses: twenty HTML
books, both PDFs, both archive metadata responses, and the transcription's
about page. It gives URLs, byte sizes, SHA-256 hashes, recording date/time, and
local file timestamps. Raw responses are kept in ignored `latin/raw/` rather
than pushed to GitHub. `python tools/acquire_sources.py --fetch` downloads
missing responses without silently replacing an existing file.

`tools/import_latin.py` uses the Python standard library to decode source BOMs
or declared fallback encodings, split chapter/section markers, and retain verse
and paragraph continuations. `latin/provenance/import.json` records parser
version, source hashes, decoding choice, counts, unassigned text, and errors.
Source bytes are unmodified. Some snapshots are UTF-16; others need cp1252
decoding and use Latin-letter placeholders for Greek. These are defects or
conventions of the working transcription, not restored Greek from the scan.

Current extraction: 4,511 numbered sections in 17 books. Books V, X, and XI
remain in raw HTML only: a regressing chapter heading, unchaptered reference
structure, and a letter-l section marker respectively. No speculative numbering
repair was made. Unnumbered introductions remain in the report, not invented
numbered sections. Counts are not full-work completeness certification.

## Pilot collation

Eleven selected sections in `pilot/source.json` were checked against the print
scans: I.3.1-3 (volume I PDF page 42), I.29.1-5 (pages 71-72), XII.3.9
(volume II PDF page 64), XII.8.1-2 (page 95). These are PDF page ordinals,
not printed folios. See `pilot/source-corrections.json` and `audit/pilot-review.md`.
Greek σύμβολον replaces the HTML's SUMBOLON in the pilot only. This is a working
text, not a diplomatic transcription of typography or the entire apparatus.
Full-source file hashes in the pilot snapshot identify its preparation state;
the saved pilot input remains unchanged if the larger corpus is later reimported.

The Latin Library describes its Latin as public-domain text, acknowledges
remaining scanner errors, and says it is not a substitute for a critical
edition: https://www.thelatinlibrary.com/about.html. Our textual authority is
the 1911 print, not website design or a modern English translation. The scans
are retained for consultation; their Google front matter and watermarks are
not reproduced as book content. OCR locates passages but does not settle Greek,
punctuation, or section numbering.
