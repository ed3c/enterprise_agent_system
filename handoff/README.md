# Local Handoff

Local Handoff is the explicit boundary between public/cloud coordination and execution requiring a trusted local filesystem, private/provider credentials, physical isolation, external effects, or Human authority.

## Current exact P7 chain

```text
Queue-v4 #99
  commit 75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4
  tree   eef641a94dec755267ebe8086b68ecbe98c5b68a
  verify #101 / 32348407481 PASS
  Shadow 4980564966 primary; 4980566877 corroborating
        ↓ true child
H4R #103
  commit 7be0a69b0046b66799baee2ddb5e305c90d60ec6
  tree   e8a5643b7379acca281387727c203aa9c9559acb
  verify #105 / 32349394151 PASS
  Shadow 4980654571
        ↓ real local execution only
external secret-free receipt
        ↓
H4RR #107
  commit 4a44e9cf9ece133e8117ecc100e419f359d8e1a1
  tree   d088e4fa7a21958efc73f7246a707c2a77b5640a
  verify #109 / 32350502938 PASS
  Shadow 4980770691
```

Main integration does not replace these execution identities. Until a new local-runtime admission explicitly says otherwise, execute the exact admitted H4R subject rather than an arbitrary future `main` HEAD.

## Queue truth

```text
queue_id               LH-EAS-INCEPTION-P7-V4-2026-08-20
items                  11
ACTIVE                  1
ACTIVE item             LH-P7-01-ROOT-D-V3-LOCAL-READBACK
blocked successors      9
Human terminal          1
main commands           9
cleanup commands        3
queue execution         NOT_PERFORMED
ACTIVE execution        NOT_PERFORMED
real local receipt      NOT_OBSERVED
canonical advancement   NOT_PERFORMED
vertical canary         PLAN_ONLY / receipt=null
```

Historical queues #27/#50/#59, runners #55/#67 and reducer #71 have `authority NONE` for current execution.

## Execution State Machine

```text
QUEUE_V4_BOUND
→ EXACTLY_ONE_ACTIVE
→ EXACT_H4R_SUBJECT_ADMITTED
→ LOCAL_RUNTIME_ADMITTED
→ EXECUTION_ROOTS_VALIDATED
→ CLEAN_PREFLIGHT / NO_PREEXISTING_RESIDUE
→ 9 MAIN COMMANDS
→ 3 FINALLY CLEANUP COMMANDS
→ EXACT ROOT-D OBSERVATION
→ CLEAN RESIDUE READBACK
→ RECEIPT SCHEMA VALIDATION
→ ATOMIC EXTERNAL RECEIPT WRITE
→ H4RR SEMANTIC READBACK
→ NEXT_EPOCH_CANDIDATE
→ CANONICAL OWNER ADVANCEMENT | BLOCKED | HUMAN_ADMIT_REQUIRED
```

A command exit code alone cannot advance the queue.

## Required local environment names

Only names, never values, are portable:

```text
EAS_CHECKOUT
EAS_WORKTREES
EAS_RECEIPT_DIR
```

Their actual local values must not be written to GitHub issues, Git, portable plans, or receipt content. H4R requires the roots to be absolute, existing, pairwise disjoint and non-nested.

## ACTIVE item execution contract

The current ACTIVE performs a deterministic local readback of exact Root-D #94 and replays the current Generic-X/Profile-X/Profile-D controls.

Preflight fails closed on:

- dirty checkout;
- pre-existing `root-d-v3` worktree directory;
- pre-existing worktree registration;
- pre-existing `refs/remotes/origin/p7-root-d-v3` temporary ref;
- existing receipt target;
- path traversal/root escape;
- unknown environment names;
- missing exact external runner admission.

Subprocess law:

```text
structured argv
shell = false
bounded timeout
bounded environment
GIT_TERMINAL_PROMPT = 0
stdout/stderr => SHA-256 digest only in portable receipt
```

Main failure still executes the entire cleanup denominator in `finally`:

```text
REMOVE_ROOT_D_WORKTREE
→ PRUNE_WORKTREES
→ DELETE_TEMP_ROOT_D_REF
```

## Receipt law

Expected receipt filename:

```text
${EAS_RECEIPT_DIR}/LH-P7-01-ROOT-D-V3-LOCAL-READBACK.json
```

The receipt is external/local, secret-free, schema-validated before atomic write, never overwritten, and must retain failures/retries plus `claims_not_proven`.

H4RR independently revalidates:

- exact queue/item;
- exact H4R subject before/after;
- `LOCAL_DETERMINISTIC` evidence lane;
- exact 9-main + 3-cleanup records and zero exits for PASS;
- exact Root-D #94 observation;
- clean dirty/residue state;
- portable/secret-free surface;
- exact success transition.

A synthetic fixture or caller label `REAL_LOCAL_RECEIPT` always receives:

```text
real_local_evidence_credit = 0
queue_mutation_performed = false
canonical_advancement_performed = false
```

Missing receipt is always:

```text
BLOCKED_BY_MISSING_REAL_LOCAL_RECEIPT
```

## Stronger lanes remain blocked

A successful first local receipt would only satisfy its declared `LOCAL_DETERMINISTIC` lane. It does not satisfy provider/private/physical/effect/user/Human/release requirements. Those successors stay blocked until their own typed capability, authority, execution, readback, cleanup/compensation and Human receipts exist.

## Issue handoff

Canonical owner: issue #14. Program owner: #6.

Every local attempt must append or reference an immutable execution receipt, preserve failed/retried/UNKNOWN attempts, state cleanup/residue, and identify the next exact owner. Do not close #14 while any current queue successor or Human terminal remains unresolved.