# AGENTS.md — enterprise_agent_system operating contract

## Mandatory read order

1. `README.md` — current literal verdict and repository role.
2. `CONTEXT.md` — mutable exact-subject handoff snapshot.
3. `ARCHITECTURE.md` — stable authority/plane invariants.
4. `docs/INDEX.md` — documentation routes.
5. `docs/traceability/MOLECULAR_STACK_INDEX.md` — exact Stack/PR relationships.
6. `docs/architecture/STATE_MACHINES.md` and `DATA_FLOW.md` — state/data routes.
7. owning issue + exact fresh-session prompt under `docs/prompts/`.
8. nearest profile/repository `AGENTS.md` before mutating any child path.

## Runtime classification

Every task declares one lane before execution:

```text
CLOUD_DETERMINISTIC
PUBLIC_REVERSIBLE
LOCAL_PHYSICAL
PROVIDER_LIVE
PRIVATE_EVIDENCE
EXTERNAL_EFFECT
HUMAN_ADMIT
RELEASE_ROLLBACK
```

A cheaper lane never proxies a stronger one. `NOT_EXERCISED`, `BLOCKED`, `UNKNOWN_EFFECT`, `HUMAN_ADMIT_REQUIRED`, and `NOT_PERFORMED` earn zero closure credit.

## Source proposal / current fact law

Source PDFs, issue bodies, Docs, Sheets, prompts, diagrams, model output, and architecture prose are proposals or projections until exact evidence binds them. Current fact requires an immutable subject and the evidence lane appropriate to the claim. Branch names and mutable URLs are navigation only.

## One-interface / one-owner law

A canonical interface/state has one owner repository. EAS routes and reconciles; it must not copy runtime, durable workflow/effect, provider, independent-verifier, or Human/release implementation into the control plane.

Current important splits:

- A2R runtime contract owner = `runtime-env`; A2 sandbox/steering owner = `agent-shield-monorepo`.
- A2R current owner head and A2-consumed contract pin remain distinct identities.
- `TELEMETRY-001`: Agent Shield remains runtime owner; EAS A4 is policy/synthetic evidence only.
- `HITL-001`: EAS-H #27 owns queue contract; Human execution is separate.

## Writer / branch / path / resource leases

Before mutation, bind:

```text
owner issue
branch and exact base commit/tree
writable paths
read-only paths
forbidden paths
temporary worktree/resource leases
rollback subject
```

One active Writer owns a path/resource. A process dependency is not a Git parent. A branch created without authored bytes or PR has no Stack/evidence credit.

## Role boundaries

**Tech Lead** freezes objective/denominator, compiles DAG/leases/packets, routes candidates, and coordinates exact receipts. It cannot invent evidence.

**Worker** writes only the declared lease and returns candidate receipts. It cannot self-promote canonical state.

**Gate** is deterministic or independently attributable and fails closed for its declared semantic reason.

**Shadow Architect** receives the same immutable subject through a separate read-only path. It can block or admit for downstream review. It cannot edit Builder bytes, resolve semantic conflicts, write task/effect/Human/release state, merge, release, or roll back.

**Canonical reducer/owner** alone advances owned state after exact receipt readback.

**Human authority** alone admits legal/security conflicts, irreversible effects, merge, release, and rollback where declared.

## Start versus completion edges

`START_READY` means prerequisites are sufficient to begin bounded work. `COMPLETE_READY` requires all declared outputs/Gates/receipts. Never close a completion edge from start readiness, transport acknowledgement, issue state, or task scheduling.

## Fresh-session prompt packet contract

A Worker session must not depend on prior chat memory. The packet binds:

```text
exact repo/commit/tree + source/profile digest
objective / non-goals / invariants / unknowns
one role + one owner issue
writable / read-only / forbidden paths/resources
start dependencies + completion dependencies
input/output contracts
positive + planted mutation controls
runtime/capability requirements
evidence lane + evidence ceiling
retry / timeout / cleanup / retention / rollback
required receipt + claims_not_proven + next authority
```

## GitHub / Google projection boundary

GitHub exact commits/trees and Actions/review receipts are canonical publication metadata. Google Docs/Sheets may mirror narratives or dashboards only and are `ADVISORY_ONLY`. A Doc/Sheet edit cannot update canonical state or silently rewrite an admitted prompt packet.

## Pre-side-effect stop conditions

Stop and mark `BLOCKED` rather than improvise if work would require:

- undeclared credential/provider enrollment;
- private-data egress not explicitly admitted;
- widening network/mount/privilege/capability policy;
- external write without typed `WriteIntent`, idempotency identity, expected remote version and readback/unknown-effect plan;
- Human-owned legal/security/conflict decision;
- merge/release/rollback authority;
- writing outside the active lease;
- treating missing evidence as PASS.

## Verification and cleanup denominator

Every execution receipt retains attempts, failures, retries, skips, timeouts/OOM, unknown effects, dirty-state before/after, process/worktree/port/container/mount/index/artifact residue, cleanup result, compensation/rollback subject, claims-not-proven, and next authority. Failed attempts are not deleted from the denominator.

## Local Handoff law

The single queue under `handoff/` is canonical. Exactly one item may be `ACTIVE`. A cloud Agent may compile a candidate queue item but does not advance ACTIVE state without exact local/provider receipt readback and cleanup. Secret values never enter Git/task packets/portable receipts.

## Completion packet

Return:

```text
subject_before / subject_after commit+tree
changed paths and writer lease
commands/Gates and all attempt outcomes
exact external receipts
Shadow findings/verdict
cleanup/residue/rollback state
claims_not_proven
remaining blockers
next authority
```

A phase can be complete at its declared evidence ceiling while the architecture remains `BLOCKED_FOR_CLOSURE`.