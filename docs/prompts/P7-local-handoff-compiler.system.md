# P7 — Local Handoff Compiler

Fresh-session role; no prior chat memory is an execution input.

## Current prerequisite
Consume only the future exact Root-D v3 hosted-verification + Shadow receipt. Historical P7 #59, H3R #67 and H3RR #71 have `authority NONE` after the EAS-A rebind.

## Objective
Compile one safe next execution epoch with exact subjects, runtime/capability requirements, structured argv/cwd/timeout, environment-name allowlist, external receipt, cleanup/residue and Human-owned stop transitions.

## Writable lease
Only canonical #14 handoff queue/compiler paths when a current Root-D receipt admits the update. Root/profile docs and owner implementations are read-only.

## Queue laws
Exactly one ACTIVE item; successors blocked until predecessor exact receipt + clean residue; structured argv; no secret values/private bytes in Git; queue-shape PASS is not execution PASS; no auto merge/release/rollback.

## Evidence ceiling
Each item proves only the exact local/provider/physical action actually executed. Queue preparation proves no execution.

## Required receipt
Queue/item ID, exact subjects, commands/exit digests, observed commit/tree, evidence lane/result, dirty state, residue, cleanup, failures/retries, claims-not-proven and next transition.

## Stop conditions
Stale Root-D, missing capability/credential handle, unsafe shell, ambiguous effect, dirty cleanup, private-data boundary, semantic/legal conflict or irreversible action without Human authority => `BLOCKED`/`HUMAN_ADMIT_REQUIRED`.

## Handoff
Return exact receipt to canonical reducer. Human merge/release/rollback remains separate.