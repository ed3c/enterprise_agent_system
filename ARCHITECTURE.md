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

## Current P5/P6 Git topology

```text
Generic EAS-X #31 @ 8b1bfa38c103e1c064b8ef0aafecfc8f2a2642dc
                     \
                      +-- Profile-X v3 #40 @ fe2748e09a5222f439f09c5d0d71e486e1ade3e8
                     /                   |
Profile-E #32 @ 9f25b94ca891faf0d926b0fc22b67be88925aa81
                                         |
                                         v
                                Profile-D v4 #44
                                a7a034ef1db778fcee586fff8d8ff7848bc9a1ab
                                         |
                                         v
                                  Root-D v2 candidate
```

Profile-X v3 is the true multi-parent child of Generic-X + Profile-E. Profile-D v4 is its true child. Root-D v2 is therefore a direct child of Profile-D v4; it does **not** create a redundant second Generic-X/Profile-D merge base. Verification siblings are evidence only and never Git parents.

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
→ OWNER_AND_CONTRACT_BOUND
→ MECHANISM_IMPLEMENTED
→ DETERMINISTIC_EVIDENCE_VERIFIED
→ LIVE_OR_PHYSICAL_EVIDENCE_VERIFIED
→ USER_OUTCOME_VERIFIED
→ HUMAN_ADMITTED
→ RELEASED
→ OPERATED_WITH_ROLLBACK
```

No transition can be inferred from a later-looking label elsewhere. A PR state does not prove user outcome; provider/API success does not prove effect commitment; model agreement does not prove Human admission.

## Profile owner split

```text
A1  bettor-arena              durable state/compaction/recovery
A2R runtime-env               runtime contract owner
A2  agent-shield-monorepo     sandbox/steering execution owner
A3  truth-verify-loop         exact evidence owner
A4  enterprise_agent_system   provenance/policy candidate + synthetic evidence only
A5  bettor-arena              discovery/admission candidate
A6  bettor-arena              ingress/effect semantics
E   enterprise_agent_system   read-only Profile Shadow
X   enterprise_agent_system   exact-subject profile convergence
D   enterprise_agent_system   documentation projection
```

`TELEMETRY-001` keeps Agent Shield as canonical runtime owner. A4 evidence does not re-own telemetry runtime. Local Handoff #14 owns P7 queue compilation; Human execution remains separate.

## Current exact evidence ceiling

```text
Profile-D #44 target        a7a034ef1db778fcee586fff8d8ff7848bc9a1ab
Profile-D hosted verify     32282726313 PASS
Profile-D Shadow            4975046170 ADMIT_FOR_ROOT_EAS_D
requirements                15
contradictions              14
stronger no-credit lanes    13
required lanes satisfied    1
requirement closure credit  0
Profile-X hosted Gate       ABSENT
vertical canary             PLAN_ONLY / execution_receipt=null
full architecture           BLOCKED_FOR_CLOSURE
profile release             NOT_ADMITTED
```

A1 current hosted receipt is `32259216877`; stale `32259476821` is historical only and excluded from current machine authority.

## Projection boundary

GitHub exact commits/trees and typed Actions/review receipts are canonical publication metadata. Google Docs/Sheets are `ADVISORY_ONLY`. Root/profile docs are projections and cannot write canonical task/workflow/effect/Human/release state.

See `docs/architecture/STATE_MACHINES.md`, `docs/architecture/DATA_FLOW.md`, and `docs/traceability/MOLECULAR_STACK_INDEX.md` for operational routing.