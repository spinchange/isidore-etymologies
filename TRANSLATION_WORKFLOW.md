# Translation workflow

## Text and units

Use Lindsay (1911) as the declared base edition. Preserve book, chapter, and
section numbering as positive dotted Arabic references, for example `1.1.1`.
Keep printed headings and prefatory matter in a separately documented inventory
when imported; do not squeeze unnumbered matter into invented numbered sections.

Accepted files are UTF-8 JSONL: one JSON object per numbered source section.
Source records in `latin/book-NN.jsonl` contain `ref` and `text`. Accepted
English records in `translation/book-NN.jsonl` contain `ref`, `text`, and a
`notes` array of strings. Newlines within a section are JSON escapes. Plain
text fields are literal text, not HTML. An example of the record structure is:

```json
{"ref":"1.1.1","text":"The transcribed Latin section goes here."}
```

The example is documentation, not source text. Nothing imports it automatically.

## Stages

1. Acquire: retain raw downloads outside version control and record provenance.
2. Collate: compare the working Latin with the scan; log changes and establish
   each book's expected section list from the source, not from the translation.
3. Draft: work in `segments/bNN/`; retain the source references and model/run
   details. Segment on complete sections and preferably chapter boundaries.
4. Fidelity: compare every clause with the Latin; record omissions, additions,
   ambiguity, technical terms, Greek/Hebrew, quotations, and etymological claims.
5. Annotate: draft notes clearly marked as draft. Distinguish Isidore's claims
   from modern explanations and do not silently repair his historical science.
6. Review: adjudicate each finding, record a reason for changes and declined
   findings, and read the revised English against the complete Latin section.
7. Accept: assemble the reviewed English JSONL, finalize notes, and attach the
   evidence path in the manifest. Set status `accepted` only when the book has
   verified source coverage and the whole translation has passed review.
8. Publish: derive all editions from that same accepted text; inspect rendered
   pages, hyperlinks, section alignment, and print proofs separately.

The workflow describes required evidence, not work already performed. No
particular model, automation runner, or independent reviewer is assigned yet.
Record actual identities, dates, findings, and decisions in the review record.
Any later change to the Latin inventory or accepted English reopens review.

## Manifest

`segments/manifest.json` contains twenty ordered book records. Status is
`not-started`, `in-progress`, or `accepted`. Each record gives source and
translation paths, `expected_sections` (null until established),
`coverage_verified`, and an optional `review_record` path. An accepted book
requires all coverage flags, matching source/English references, and a
nonempty review record. The checker checks structure and recorded evidence;
it cannot certify the philological quality of a review.
