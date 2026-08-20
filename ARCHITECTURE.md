# Architecture

`enterprise_agent_system` is the cross-repository control/closure plane. It coordinates exact subjects and evidence while canonical implementation stays with the owning repository.

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

## Current P5/P6 topology

```text
Generic EAS-X #31 @ b295eabec7b4c9d4e1f65f7fb0238034f454ae7f
                     \
                      +-- Profile-X v4 #80 @ df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0
                     /
Profile-E #32 @ 9f25b94ca891faf0d926b0fc22b67be88925aa81
                                         |
                                         v
                                Profile-D v5 #84
                                f04f9fc78270c8f97ce978e2ccc161ab4d724ca4
                                         |
                                         v
                                  Root-D v3 candidate
                                         |
                           external exact verification + Shadow
                                         |
                                         v
                                  P7 queue recompilation
```

EAS-A #68 @ `250717db1cad584d50890c0d851153fa2cd755e8` is `ADVISORY_ONLY` and `PROCESS_DEPENDENCY_NOT_GIT_PARENT`. It is not a third Profile-X or Root-D parent.

Profile-X #80 is the current multi-parent convergence subject. Profile-D #84 is its true child. Root-D v3 is therefore a direct child of Profile-D #84. Verification siblings #83/#90 and future Root-D verifier are evidence only and never Git parents.

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
Profile-X #80                df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0
Profile-X external verify    32321499909 PASS
Profile-X Shadow             4978282030
Profile-D #84                f04f9fc78270c8f97ce978e2ccc161ab4d724ca4
Profile-D external verify    32326260896 PASS
Profile-D Shadow             4978669357
requirements                 15
contradictions               14
stronger no-credit lanes     13
required lanes satisfied     1
requirement closure credit   0
vertical canary              PLAN_ONLY / execution_receipt=null
full architecture            BLOCKED_FOR_CLOSURE
profile release              NOT_ADMITTED
P7 execution                 NOT_PERFORMED
```

Profile-D RED runs `32325143724`, `32325653265`, and `32325967828` remain part of the fault denominator; only `32326260896` has final exact-target credit.

## Projection boundary

GitHub exact commits/trees and typed Actions/review receipts are canonical publication metadata. Google Docs/Sheets are `ADVISORY_ONLY`. EAS-A does not prove Google connectivity/write/source correctness. Root/profile docs are projections and cannot write canonical task/workflow/effect/Human/release state.

See `docs/architecture/STATE_MACHINES.md`, `docs/architecture/DATA_FLOW.md`, and `docs/traceability/MOLECULAR_STACK_INDEX.md` for operational routing.