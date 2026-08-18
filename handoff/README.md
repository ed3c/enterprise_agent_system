# Local Handoff

Local Handoff is continuation authority for work that cannot be truthfully executed in the current cloud/connector runtime. It is not a dumping ground for unfinished in-session work and is not execution evidence.

## Queue State Machine

```text
QUEUE_SUBJECT_BOUND
→ EXACT_ACTIVE_ITEM_SELECTED
→ LOCAL_CAPABILITIES_REBOUND
→ COMMAND_CONTRACTS_MATERIALIZED
→ ACTIVE_ITEM_EXECUTED
→ RECEIPT_AND_CLEANUP_VERIFIED
→ CANONICAL_REDUCER_RECONCILED
→ NEXT_EPOCH_EMITTED | HUMAN_ADMIT_REQUIRED | COMPLETE | BLOCKED
```

## Item contract

```text
stable item ID
predecessor and exactly one ACTIVE state
exact repo/commit/tree/policy/method subjects
required runtime/capabilities
concrete argv arrays, cwd and timeout
environment-name allowlist, never secret values
writer/worktree/path/resource leases
expected outputs and receipt schema/path
positive and negative controls
cleanup/residue/retention checks
rollback/compensation subject
claims not proven and next authority
```

Queue shape validation does not prove command execution. Advancement requires exact receipt readback, subject match and cleanup. Merge, issue closure, provider enrollment, egress approval, irreversible effects, release and destructive rollback remain Human/trusted-policy operations.

Issue #14 currently contains a concrete candidate local-verification item for draft PR #20/#21. The canonical `local-handoff-queue.json` remains absent until the queue owner validates current subjects and exactly one ACTIVE item.
