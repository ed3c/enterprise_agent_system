# Local Handoff

Local Handoff is the boundary between cloud/deterministic coordination and execution requiring local filesystem, provider credentials, private evidence, physical isolation, external effects, or Human authority.

## Current status after EAS-A rebind

```text
Root-D v3          CANDIDATE / external verify + Shadow pending
P7 current         REBIND_REQUIRED
P7 #59             historical / authority NONE
H3R #67            historical / authority NONE
H3RR #71           historical / authority NONE
queue execution    NOT_PERFORMED
Human admission    NOT_PERFORMED
```

Do not execute historical ACTIVE items. A new P7 queue may be compiled only after Root-D v3 immutable-target verification and fresh Shadow admit the exact subject.

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

Queue-shape PASS does not mean execution occurred.

## Required unresolved lanes

Physical/multi-host durability; network/gVisor isolation; provider capability/enrollment; private/independent semantic evidence; exact external Model/Data/Trace terms; live telemetry; external benchmark; real effect/readback/compensation; business/user outcome; Human legal/security/admission.

## Safety law

Use structured argv arrays, explicit cwd/timeout and environment-name allowlists. Never persist secret values/private source bytes. External mutation requires typed WriteIntent, idempotency/effect identity, expected remote version/capability, timeout/UNKNOWN_EFFECT plan, readback oracle and compensation/rollback. Human-owned irreversible transitions remain separate.

## Authority boundary

Only the canonical reducer/owner may advance an ACTIVE item after exact receipt and clean residue readback. Root docs, CI, Shadow, Google views or queue preparation cannot advance it.