# EAS-A Google Docs / Sheets advisory adapter

This directory implements only the read-side projection contract from issue #10.

Google Docs and Sheets are `ADVISORY_ONLY` projections. A revision, URL, successful read, shared-drive edit, row value, or rendered prompt mirror cannot mutate canonical task/workflow/effect/Human/release state.

Supported target classes:

```text
NARRATIVE
DASHBOARD
PROMPT_CATALOGUE_MIRROR
```

`CANONICAL_PROMPT_PACKET` and other canonical-state targets are refused. Read access may be `EXERCISED`, `REFUSED`, or `ABSENT`; missing/forbidden access is never represented as empty successful content. Writes are unavailable in this adapter and require a separate explicitly authorized action.

Rendered advisory views may carry exact GitHub linkbacks containing repository, commit, tree, and a navigation reference. They do not proxy GitHub receipts or closure authority.

No Google document, spreadsheet, credential, token, or private source byte is created or persisted by this public implementation candidate.
