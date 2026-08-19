# Local Handoff

Local Handoff is the boundary between cloud/deterministic coordination and execution requiring local filesystem, provider credentials, private evidence, physical isolation, external effects, or Human authority.

P6 root documentation does **not** modify or advance the canonical queue.

## Current P7 disposition

```text
current Root-D external receipt   PENDING
P7 queue compilation              BLOCKED_PENDING_CURRENT_ROOT_D_RECEIPT
queue execution                   NOT_PERFORMED
Human admission                   NOT_PERFORMED
```

Historical queue subjects remain visible but have no current execution authority:

```text
EAS-H PR #27
  commit 9223107163b27984ed490246b4c0899caeb1bdae
  tree   d462e2a1a69d225bf8161ce01918e5e8bb8d102f
  state  SUPERSEDED_STALE_PROFILE_SUBJECT

EAS-H2 PR #50 / verifier #51
  parent old Root-D PR #41
  state  SUPERSEDED_FOR_CURRENT_P7_UNTIL_REBOUND
```

Do not execute either historical queue against current P6 state.

## Queue State Machine

```text
CURRENT_ROOT_D_RECEIPT_BOUND
→ QUEUE_COMPILED
→ EXACTLY_ONE_ACTIVE
→ RUNTIME_AND_CAPABILITIES_CHECKED
→ COMMANDS_EXECUTED
→ EXACT_RECEIPT_WRITTEN
→ CLEANUP_AND_RESIDUE_READ_BACK
→ CANONICAL_REDUCER_READBACK
→ NEXT_EPOCH | BLOCKED | HUMAN_ADMIT_REQUIRED | COMPLETE
```

A queue-shape PASS does not mean execution occurred.

## Current stronger-lane denominator

After current Root-D is exact-target verified and Shadow-reviewed, P7 may compile bounded successors for:

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

Use structured argv arrays with explicit cwd and timeout. Never interpolate source/issue/user text into an untrusted shell string. Secret values/private bytes are forbidden in Git, task packets, logs and portable receipts; only approved environment/credential-handle names may be declared.

## Pre-effect law

Before an external mutation require typed `WriteIntent`, idempotency/effect identity, expected remote version/capability, least privilege, timeout/`UNKNOWN_EFFECT` behavior, remote readback oracle, compensation/rollback and Human approval where irreversible. `2xx`, browser click completion or transport acknowledgement is not effect commitment.

## Receipt and cleanup

Every attempt records exact subject, argv/cwd, result/exit, output digests, evidence lane, failures/retries, dirty state, process/worktree/port/container/mount/index/artifact residue, cleanup, effect/readback/compensation state, rollback subject, claims-not-proven and next transition.

## Authority boundary

Only the canonical reducer/owner may advance an ACTIVE item after exact receipt and cleanup readback. Root P6 can only produce a handoff input. Human-owned merge, release and rollback remain separate even after local/provider success.