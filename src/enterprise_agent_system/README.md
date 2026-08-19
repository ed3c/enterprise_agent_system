# Enterprise Agent System control-plane primitives

This package implements deterministic, provider-neutral control-plane primitives. It consumes the EAS-C orchestration vocabulary; it does not implement transport, provider execution, workflow/effect state or Human/release authority.

## Tech Lead orchestration state machine

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
| `validate_convergence_snapshot` | exact-owner/evidence P5 convergence candidate | owner substitution, missing denominator lanes, false Git ancestry, stronger-lane credit, false vertical-canary execution |
| `validate_owner_record` | one immutable owner binding | repository/interface mismatch, mutable subject, absent hosted/typed-Shadow receipt |

A candidate admitted for convergence is not `COMPLETE`, `HUMAN_ADMITTED`, `MERGED` or `RELEASED`.

## Independent Shadow plane

`shadow.py` evaluates the same immutable public subject through a separate, read-only path. It detects source-to-fact promotion, stale subjects, evidence-lane substitution, false closure credit, missing receipt subjects, shared-projection authority, denominator loss, terminal-state promotion and open critical findings without owner issues. Its strongest automated terminal state is `ADMIT_FOR_REVIEW`; open critical findings force `BLOCKED_FOR_CLOSURE`.

## EAS-X cross-repository convergence

`convergence.py` is an aggregate-only P5 validator. Its current machine input is `evidence/ledgers/cross-repo-closure.json` and its human route is `docs/integration/cross-repo-convergence.md`.

```text
current exact owner subjects
→ one-interface / one-owner validation
→ exact commit/tree + hosted receipt binding
→ typed Shadow provenance
→ stronger-lane denominator preservation
→ public no-effect vertical-canary PLAN_ONLY
→ external exact-head Shadow receipt
→ profile X #22 / P6 #13 / Local Handoff #14
```

EAS-X deliberately keeps `A2R_RUNTIME_CONTRACT` (`runtime-env`) separate from `A2_SANDBOX_STEERING` (`agent-shield-monorepo`). It also keeps EAS-A issue #10 visible as `NOT_IMPLEMENTED` while no exact adapter subject exists. Neither absence nor a public fixture may be normalized into a stronger PASS.

### External Shadow receipt law

The final PR review is an external authority and is **not written back into the branch it reviews**. Binding a review id into branch bytes would mutate the reviewed subject and create a self-referential freshness loop. Machine DAGs therefore record `REQUIRES_EXTERNAL_EXACT_HEAD_RECEIPT`; downstream owners must read the GitHub PR/Issue receipt against the immutable final head before consuming X. A stale review remains historical and cannot be silently reused after subject rebinding.
