# Architecture

`enterprise_agent_system` is a cross-repository control/closure plane. It coordinates exact subjects and evidence; canonical implementation stays with the owning repository.

## Stable planes

```text
Source / Contract Plane
  source registry, requirement/contradiction graph, strict contracts

Control Plane
  Tech Lead DAG, fresh-session packets, writer/resource leases, candidate reducer

Execution Plane (external owners)
  runtime, sandbox, durable workflow/state, compaction, ingress/effects, provider adapters

Verification Plane
  deterministic Gates + independent Truth Verify + read-only Shadow

Convergence Plane
  exact owner/evidence graph, literal evidence ceilings, Molecular Stack

Documentation Plane
  Agent-readable projections and prompt catalogue; no canonical runtime state

Local/Human Plane
  Local Handoff queue, provider/private/physical receipts, Human admission, release/rollback
```

## Core invariants

1. One interface/canonical state has one owner.
2. Source proposal, implementation candidate, deterministic receipt, live/physical receipt, user outcome, Human admission and release are distinct states.
3. Start edges and completion edges are distinct.
4. Process dependencies are not automatically Git parents.
5. Immutable identity is repository + commit + tree plus typed receipt where needed.
6. A Writer has exclusive declared path/resource leases.
7. Shadow is read-only and separately attributable.
8. Failed/blocked/retried/skipped/unknown-effect attempts stay in the denominator.
9. Cleanup/residue/retention/compensation/rollback is part of correctness.
10. Documentation/projection systems cannot advance canonical execution or Human state.
11. A public/deterministic fixture cannot proxy provider/private/physical/user/Human/release evidence.
12. Human-owned irreversible transitions cannot be self-promoted by an Agent, model, CI, PR state or issue state.

## Exact P6 convergence topology

```text
Generic EAS-X #31
3f8af3d75b28ca1904fe07b8ea9ee0d291f5989c
             \
              +-- root EAS-D convergence base -- root docs
             /
Profile-D #37
690154a5f7154d551bef6942fe5d1f34091c2197
```

The root convergence base is a real multi-parent Git commit whose tree contains Generic-X control/convergence bytes and the complete Profile-D profile subtree plus inherited profile workflows. Historical PR #26 is a documentation blueprint/process dependency, not a final parent.

## Canonical ownership map

```text
enterprise_agent_system  control/closure/docs projection/Local-Handoff contract
runtime-env               runtime capability/workload policy contracts
agent-shield-monorepo     sandbox/steering/provider/runtime/telemetry adapters
bettor-arena              durable Domain State/compaction/ingress/effect semantics
truth-verify-loop         independent exact evidence and disagreement receipts
openwiki-source-anchoring lexical/source anchors
Human authority           legal/security, irreversible effects, merge/release/rollback
```

## Closure ladder

```text
SOURCE_PROPOSAL
-> OWNER_AND_CONTRACT_BOUND
-> MECHANISM_IMPLEMENTED
-> DETERMINISTIC_EVIDENCE_VERIFIED
-> LIVE_OR_PHYSICAL_EVIDENCE_VERIFIED
-> USER_OUTCOME_VERIFIED
-> HUMAN_ADMITTED
-> RELEASED
-> OPERATED_WITH_ROLLBACK
```

No transition can be inferred from a later-looking label elsewhere. For example, a PR merged state does not prove user outcome; a provider 2xx does not prove effect commitment; a model agreement does not prove Human admission.

## Profile-specific owner split

```text
A1  bettor-arena              durable state/compaction/recovery
A2R runtime-env               runtime contract owner
A2  agent-shield-monorepo     sandbox/steering execution owner
A3  truth-verify-loop         exact evidence owner
A4  enterprise_agent_system   provenance/policy candidate + synthetic evidence only
A5  bettor-arena              discovery/admission candidate
A6  bettor-arena              ingress/effect semantics
E   enterprise_agent_system   read-only profile Shadow
X   enterprise_agent_system   exact-subject profile convergence
D   enterprise_agent_system   documentation projection
```

`TELEMETRY-001` still has Agent Shield as canonical runtime owner. A4 evidence does not re-own telemetry runtime. `HITL-001` binds EAS-H #27 queue contract; queue execution and Human admission remain separate.

## Evidence status at P6

```text
requirements 15/15 exact owners
required lanes satisfied 1/15
requirement closure credit 0
contradictions 14/14 preserved
profile Shadow BLOCKED_FOR_CLOSURE
vertical canary PLAN_ONLY
profile release NOT_ADMITTED
```

See `docs/architecture/STATE_MACHINES.md`, `docs/architecture/DATA_FLOW.md`, and `docs/traceability/MOLECULAR_STACK_INDEX.md` for operational routing.