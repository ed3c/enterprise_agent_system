# Local Handoff

Local Handoff is the boundary between public/cloud coordination and execution requiring local filesystem, provider credentials, private evidence, physical isolation, external effects, or Human authority.

## Current P7 candidate

```text
Root-D #94
  6981c700f9f2f9128ebeebdf80e627178b2be336
  tree d044ae652b65af6a0aba49f0f79c7c04c630bebf
  verify 32342272177 PASS
  Shadow 4979950874 = ADMIT_FOR_P7_REBIND_AFTER_EAS_A

P7 queue v4
  queue LH-EAS-INCEPTION-P7-V4-2026-08-20
  items 11
  ACTIVE 1  LH-P7-01-ROOT-D-V3-LOCAL-READBACK
  blocked successors 9
  Human terminal 1
  main commands 9
  cleanup commands 3
  queue execution NOT_PERFORMED
  vertical canary PLAN_ONLY
```

EAS-A remains `ADVISORY_ONLY`; Google connectivity/write is `NOT_PERFORMED`; source correctness is `NOT_PROVEN`.

Historical/no-current-authority subjects:

```text
PR #27  authority NONE
PR #50  authority NONE
PR #59  authority NONE
H3R #67 authority NONE
H3RR #71 authority NONE
```

Do not execute historical ACTIVE items.

## Queue State Machine

```text
QUEUE_SUBJECT_BOUND
→ EXACTLY_ONE_ACTIVE
→ RUNTIME_AND_CAPABILITIES_CHECKED
→ COMMANDS_EXECUTED
→ EXACT_RECEIPT_WRITTEN
→ CLEANUP_AND_RESIDUE_READ_BACK
→ CANDIDATE_RECEIPT_READY
→ CANONICAL_REDUCER_READBACK
→ NEXT_EPOCH | BLOCKED | HUMAN_ADMIT_REQUIRED | COMPLETE
```

Canonical projection invariant: `exactly-one-ACTIVE`.

Queue-shape PASS is not execution PASS. A local command exit alone cannot advance the queue.

## First ACTIVE item

The only ACTIVE item may read back public Root-D v3 bytes in a detached worktree, replay current Generic-X/Profile-X/Profile-D controls, assert the exact Root-D subject, write a secret-free external receipt, then remove/prune the worktree and temporary ref. Actual execution is outside this public GitHub phase and remains `NOT_PERFORMED`.

## Safety and authority

Use structured argv arrays, explicit cwd/timeout, an environment-name allowlist, and no secret/credential values in Git. External mutation requires typed WriteIntent, idempotency/effect identity, expected remote version, UNKNOWN_EFFECT/readback/compensation handling, and Human authority where irreversible.

Only the canonical reducer/owner may advance ACTIVE after exact receipt and clean residue readback. Root docs, GitHub Actions, Shadow, EAS-A/Google projections, queue preparation, or model agreement cannot perform Human admission, merge, release or rollback.