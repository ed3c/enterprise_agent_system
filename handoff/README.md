# Local Handoff

Local Handoff is the boundary between cloud/deterministic coordination and execution requiring local filesystem, provider credentials, private evidence, physical isolation, external effects, or Human authority.

The canonical queue is `local-handoff-queue.json` when present on the admitted EAS-H subject. P6 documentation does **not** modify or advance that queue.

## Current contract subject

EAS-H PR #27 provides a deterministic queue contract at:

```text
commit 9223107163b27984ed490246b4c0899caeb1bdae
tree   d462e2a1a69d225bf8161ce01918e5e8bb8d102f
state  DETERMINISTIC_QUEUE_CONTRACT_ONLY
queue execution NOT_PERFORMED
Human admission NOT_PERFORMED
```

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

A queue-shape PASS does not mean execution occurred.

## P6 handoff denominator

After root EAS-D is exact-target verified and Shadow-reviewed, blocked successors may be compiled for:

- physical power-loss / multi-host durability;
- network/gVisor isolation;
- provider capability observation/enrollment;
- external independent semantic/private evidence;
- exact external Model/Data/Trace terms;
- live telemetry export/store/delete;
- external candidate benchmark;
- real API/browser effect + remote readback;
- compensation;
- business/user outcome;
- Human legal/security/admission.

## Command safety

Use structured argv arrays with explicit cwd and timeout. Never interpolate source/issue/user text into an untrusted shell string. Secret values are forbidden in Git, task packets, logs, and portable receipts; only approved environment/credential-handle names may be declared.

## Pre-effect law

An external mutation needs typed `WriteIntent`, idempotency/effect identity, expected remote version/capability, least privilege, timeout/UNKNOWN_EFFECT behavior, remote readback oracle, compensation/rollback and Human approval where irreversible. `2xx`, browser click completion, or transport acknowledgement is not effect commitment.

## Receipt and cleanup

Every attempt records exact subject, argv/cwd, exit/result, output digests, evidence lane, failures/retries, dirty state before/after, process/worktree/port/container/mount/index/artifact residue, cleanup result, effect/readback/compensation state, rollback subject, claims-not-proven and next transition.

## Authority boundary

Only the canonical reducer/owner may advance the ACTIVE item after exact receipt and cleanup readback. Cloud P6 cannot advance it. Human-owned merge, release and rollback remain separate even after local/provider success.