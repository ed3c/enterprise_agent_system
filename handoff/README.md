# Local Handoff

Local Handoff is the boundary between cloud/deterministic coordination and execution requiring local filesystem, provider credentials, private evidence, physical isolation, external effects, or Human authority.

## Current P7 queue v2

The canonical P7 preparation candidate is `handoff/local-handoff-queue.json` under issue #46. It is compiled from final Root-D:

```text
Root-D commit 89e12f5863c9bfd02bddb28de121d9c19cc25d16
Root-D tree   16e51462b2a0a693c1af92ad344fa3db6bbd4879
DV run        32272986158 PASS
Shadow        4974136248
P6 state      COMPLETE_AT_DOCS_CEILING
P7 execution  NOT_PERFORMED
```

Queue v2 has exactly one `ACTIVE` item: `LH-P7-01-FINAL-P6-LOCAL-READBACK`. It only performs a local exact-subject readback/replay of final public P6 bytes. It does not need the local-only PDF, a provider credential or an external write.

The successor chain remains blocked:

```text
01 final P6 local readback
-> 02 A2R tokenizer/context observation
-> 03 A1 physical durability
-> 04 A2 network/gVisor + provider capability
-> 05 A3 independent semantic/private evidence
-> 06 A4 exact terms + live telemetry
-> 07 A5 external matched benchmark + Human admission
-> 08 A6 provider effect/readback/compensation
-> 09 content-addressed vertical canary
-> 10 final independent Truth Verify
-> 11 Human legal/security/admission + separate merge/release/rollback
```

The vertical canary remains `PLAN_ONLY`, its execution receipt remains `null`, profile Shadow remains `BLOCKED_FOR_CLOSURE`, and queue execution remains `NOT_PERFORMED`.

## Superseded queue history

PR #27 / commit `9223107163b27984ed490246b4c0899caeb1bdae` / tree `d462e2a1a69d225bf8161ce01918e5e8bb8d102f` is `SUPERSEDED_STALE_SUBJECT`.

Its ACTIVE item `LH-INCEPTION-SOURCE-01` bound profile PR #21 at `60f994f...`. Final P5/P6 subjects have advanced, so issue #14's stale-subject stop condition applies. The old queue must not execute and receives no evidence credit. The immutable disposition is recorded in `history/LH-EAS-INCEPTION-2026-08-18-superseded.json`; old bytes remain recoverable at their exact Git subject.

## Queue State Machine

```text
QUEUE_SUBJECT_BOUND
-> EXACTLY_ONE_ACTIVE
-> RUNTIME_AND_CAPABILITIES_CHECKED
-> COMMANDS_EXECUTED
-> EXACT_RECEIPT_WRITTEN
-> CLEANUP_AND_RESIDUE_READ_BACK
-> CANDIDATE_RECEIPT_READY
-> CANONICAL_REDUCER_READBACK
-> NEXT_EPOCH | BLOCKED | HUMAN_ADMIT_REQUIRED | COMPLETE
```

A queue-shape PASS does not mean execution occurred. A command exit code does not advance the queue.

## Receipt contract

Every executed item must validate against `local-handoff-receipt.schema.json` and record exact queue/item ID, start/end, subject before/after, argv/cwd, exit codes, stdout/stderr digests, observed commit/tree, literal evidence lane/result, dirty state, residue inventory, cleanup, failures/retries, effect/readback/compensation state where applicable, claims-not-proven and next transition.

Only the canonical reducer/owner may advance the ACTIVE item after exact receipt readback, evidence-lane match and clean residue verification.

## Command safety

Use structured argv arrays with explicit cwd and timeout. Never interpolate source/issue/user text into an untrusted shell string. Secret values are forbidden in Git, task packets, logs, and portable receipts; only approved environment/credential-handle names may be declared.

Current environment-name allowlist:

```text
EAS_CHECKOUT
EAS_WORKTREES
EAS_RECEIPT_DIR
RUNTIME_ENV_CHECKOUT
BETTOR_ARENA_CHECKOUT
AGENT_SHIELD_CHECKOUT
TRUTH_VERIFY_CHECKOUT
```

## Pre-effect law

An external mutation needs typed `WriteIntent`, idempotency/effect identity, expected remote version/capability, least privilege, timeout/`UNKNOWN_EFFECT` behavior, remote readback oracle, compensation/rollback and Human approval where irreversible. `2xx`, browser click completion, transport acknowledgement, queue-shape PASS or model self-report is not effect commitment.

## Evidence ceiling

P7 queue v2 proves **executable queue preparation only**. It does not prove the ACTIVE item executed, physical durability, provider/network isolation, private evidence, external independent semantics, legal/security approval, live telemetry, external benchmark, real external effects/readback, compensation, business/user outcome, Human admission, merge, release or rollback.
