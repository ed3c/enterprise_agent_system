# Documentation index

Read in this order for root architecture work:

1. [`../README.md`](../README.md) — current verdict, exact convergence inputs, phase/owner overview.
2. [`../AGENTS.md`](../AGENTS.md) — operating contract, role/lease/evidence/side-effect laws.
3. [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — stable plane and ownership invariants.
4. [`../CONTEXT.md`](../CONTEXT.md) — mutable current exact-subject handoff snapshot.
5. [`architecture/STATE_MACHINES.md`](architecture/STATE_MACHINES.md) — directory → owner → State Machine → Gate → next owner.
6. [`architecture/DATA_FLOW.md`](architecture/DATA_FLOW.md) — guarded process/evidence/runtime flows and forbidden routes.
7. [`traceability/MOLECULAR_STACK_INDEX.md`](traceability/MOLECULAR_STACK_INDEX.md) — Generic/Profile Stack, Git ancestry versus process dependencies, receipt history.
8. [`prompts/`](prompts/) — P0-P7 complete fresh-session system prompts.
9. [`../prompts/README.md`](../prompts/README.md) — prompt catalogue/selection and content-addressing rules.
10. [`../handoff/README.md`](../handoff/README.md) — P7 Local Handoff and Human boundary.

## Machine authorities consumed by docs

Generic:

- `../plans/task-dag.json`
- `../plans/molecular-stack-index.json`
- `../evidence/ledgers/cross-repo-closure.json`

Agent Thinking Inception profile:

- `../profiles/agent-thinking-inception/plans/closure-record.json`
- `../profiles/agent-thinking-inception/plans/vertical-canary.json`
- `../profiles/agent-thinking-inception/plans/molecular-stack-index.json`
- `../profiles/agent-thinking-inception/plans/directory-state-machine-index.json`
- `../profiles/agent-thinking-inception/plans/data-flow.json`
- `../profiles/agent-thinking-inception/evidence/convergence/receipt-index.json`
- `../profiles/agent-thinking-inception/prompts/README.md`

Human docs are projections over these machine records and exact GitHub receipts. If prose and machine records disagree, stop and reconcile the exact subject; do not silently choose the more optimistic interpretation.

## Current evidence ceiling

```text
P6 documentation routing/index consistency can be verified.
Operational closure cannot be inferred.
```

Current profile denominator remains 15 requirements, 14 contradictions, 1/15 required lanes satisfied, zero requirement closure credit, Profile Shadow `BLOCKED_FOR_CLOSURE`, vertical canary `PLAN_ONLY`, and release `NOT_ADMITTED`.