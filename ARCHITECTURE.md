# Architecture

## Stable principle

`enterprise_agent_system` is a control plane over immutable subjects and owner receipts. It is not the execution plane.

```text
CONTROL PLANE
  source registry
  requirements / contradictions
  contracts and owner bindings
  Tech Lead DAG and prompt packets
  independent Shadow controls
  closure reducer / Stack / handoff

EXECUTION PLANES
  runtime-env                 capability/workload contract
  bettor-arena                durable workflow/state/VFS/effects
  agent-shield-monorepo       sandbox/provider/API/browser/telemetry
  truth-verify-loop           independent evidence
  Human/trusted policy        admission/release/rollback
```

## Core invariants

1. One interface and canonical state have one owner.
2. Domain State, task state, effect state, Human decisions and release state are distinct.
3. Conversation context is working memory, not the system of record.
4. Complete tool transactions are atomic across checkpoint/compaction.
5. Provider capabilities are observed; unsupported behavior stays `ABSENT`.
6. Start and completion edges are separate.
7. Worker output is candidate evidence.
8. Evidence lanes are literal and exact-subject.
9. At-least-once delivery requires idempotency, effect ledger, readback and unknown-effect handling.
10. Google Docs/Sheets are advisory projections.
11. No static result can self-promote live/Human/release state.
12. Cleanup, failure denominator and rollback are part of completion.

## Control-plane State Machine

```text
SOURCE_REGISTERED
→ REQUIREMENT_DENOMINATOR_FROZEN
→ CONTRACTS_BOUND
→ CAPABILITY_AND_TASK_DAGS_COMPILED
→ PROMPT_PACKETS_AND_LEASES_EMITTED
→ CANDIDATE_RECEIPTS_COLLECTED
→ INDEPENDENT_GATES_AND_SHADOW_APPLIED
→ CANONICAL_REDUCTION
→ GLOBAL_OBJECTIVE_ASSERTED
→ DOCS_CONVERGENCE | LOCAL_HANDOFF
→ HUMAN_ADMIT_REQUIRED | COMPLETE | BLOCKED
```

## Closure planes

```text
mechanism        implementation exists on exact subject
deterministic    declared controls pass on exact subject
live/physical    real runtime/provider/host behavior observed
effect           external write read back or explicit unknown/compensation
user             named user-visible outcome verified
Human            authorized person/policy admits transition
release          exact release subject promoted
operations       rollback/recovery exercised
```

The planes are monotonic only with their own receipts. A later repository commit may invalidate prior evidence and require re-evaluation.
