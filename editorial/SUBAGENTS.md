# Bounded subagent protocol

Subagents may perform narrow, reviewable assistance after source files and
section inventories are fixed. They may draft bounded translation proposals
and identify possible fidelity issues, but do not resolve Latin readings,
select final content, or make editorial decisions. The lead/editorial team
owns fidelity review and acceptance; obtain user approval for voice and design
choices. No external automatic batch runner or paid API job is configured;
the recorded pilot tasks used the session's subagent tools.

## Fixed task inputs

Each task record names the task and schema version, exact input paths and
SHA-256 hashes, edition and source status, included section IDs, prompt path
and SHA-256, requested operation, actual model and reasoning effort (as
reported), start/completion dates, retry count and reasons, and output path
and hash. Record unknown metadata as `unknown`; never guess it. Each retry is
a separate dated attempt. Keep source excerpts within the assigned IDs.

## Permitted tasks and JSON outputs

- **Extraction proposal:** transcribe only assigned scan spans; return JSON
  `{schema, task_id, items:[{ref, text, page, uncertainty}]}`. This is
  unverified OCR/transcription, not working Latin.
- **Coverage audit:** compare fixed expected IDs and supplied IDs; return
  `{schema, task_id, missing:[...], unexpected:[...], duplicates:[...]}`.
- **Latin term inventory:** list forms only in supplied text; return
  `{schema, task_id, terms:[{form, ref, context}]}`. Do not assert etymologies.
- **Mechanical checks:** report specified rule results only; return
  `{schema, task_id, checks:[{rule, ref, result, detail}]}`.
- **Draft proposal:** translate only assigned complete sections; return
  `{schema, task_id, sections:[{ref, text, notes, latin_terms}]}`. Keep
  uncertainty visible; this is unreviewed proposal text.
- **Fidelity proposal:** flag only requested issue types with source and draft
  evidence; return `{schema, task_id, findings:[{ref, kind, latin_evidence,
  draft_evidence, proposed_action}]}`. Do not rewrite the full draft.

For every task, include all schema keys, use JSON null for unavailable values,
and return no unrequested prose. Preserve exact section IDs. Pin input hashes;
if any input changes, issue a new task record. The lead/editorial team verifies
source fidelity and decides whether any proposal is useful.

## Review and limits

Model outputs are not literally deterministic, even with fixed prompts and
inputs. Reproducibility means preserving the actual run record and artifacts,
not promising identical output. Deterministic scripts gate IDs, alignment,
coverage, and declared mechanical rules; they cannot establish translation
fidelity. The lead/editorial fidelity review compares proposed text with the
collated Latin, records corrections and decisions, and marks work
accepted. User approval is for voice and design, not routine line-by-line
checking. No subagent result counts as review evidence until editorial review
is recorded.
