# Tech Lead orchestration core

This package implements deterministic, provider-neutral control-plane primitives. It consumes the EAS-C orchestration vocabulary; it does not implement transport, provider execution, workflow/effect state or Human/release authority.

## State machine

```text
REQUEST_BOUND
→ SYSTEM_CONTRACT_EXTRACTED
→ CAPABILITY_DAG_COMPILED
→ START_AND_COMPLETION_EDGES_ASSERTED
→ TASK_DAG_COMPILED
→ PROMPT_PACKETS_EMITTED
→ WORKERS_AND_LEASES_ADMITTED
→ CANDIDATES_RECEIVED
→ INDEPENDENT_GATES_APPLIED
→ CANONICAL_REDUCTION
→ GLOBAL_OBJECTIVE_ASSERTED
→ DELIVERY_OR_LOCAL_HANDOFF
```

## Public primitives

| Primitive | Output | Refuses |
|---|---|---|
| `validate_run` | admitted deterministic orchestration record | mutable subjects, malformed/looping edges, missing/overlapping leases, second state writers, authority widening |
| `topological_waves` | stable parallel waves | unknown or cyclic dependencies |
| `compile_prompt_packet` | content-addressed zero-context Worker packet | missing objective/invariants/Gates or invalid run |
| `validate_prompt_packet` | persisted packet digest/lease/authority verdict | silent packet edits, read/write collisions, missing Local/Human handoff, authority widening |
| `reduce_candidate` | one candidate admitted for convergence or a blocked verdict | stale subject, wrong task/lane, missing Gates, multiple winners, critical Shadow finding, Human/release promotion |

A candidate admitted for convergence is not `COMPLETE`, `HUMAN_ADMITTED`, `MERGED` or `RELEASED`.

## Independent Shadow plane

`shadow.py` evaluates the same immutable public subject through a separate, read-only path. It detects source-to-fact promotion, stale subjects, evidence-lane substitution, false closure credit, missing receipt subjects, shared-projection authority, denominator loss, terminal-state promotion and open critical findings without owner issues. Its strongest automated terminal state is `ADMIT_FOR_REVIEW`; open critical findings force `BLOCKED_FOR_CLOSURE`.
