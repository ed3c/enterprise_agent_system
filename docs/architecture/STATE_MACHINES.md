# Directory → State Machine → DAG ownership

| Surface | State Machine | Canonical owner | Gate / blocker | Evidence ceiling | Next owner |
|---|---|---|---|---|---|
| `contracts/control-plane/**` | `UNBOUND → STRICT_CONTRACT → CONSUMER_READY` | EAS-C #8 | schema/mutation controls | contract | K/E/X |
| `src/enterprise_agent_system/**` | `REQUEST → DAG → PACKETS → REDUCE` | EAS-K #9 | DAG/lease/parent binding | deterministic | owners/X |
| `integrations/github/**`, `integrations/google-drive/**` | `REFERENCE → REVISION/DIGEST → CURRENT|STALE|REFUSED|ABSENT` | EAS-A #10 | `32295871632`, Shadow `4976213414`; Google write/connectivity not exercised | `ADVISORY_ONLY` | X/D |
| profile `source/**` | `SOURCE_REGISTERED → SOURCE_PROPOSAL` | C0 #2 | source digest/coverage | source graph | requirements |
| profile `contracts/**` | `PROFILE_CONTRACT_READY → OWNER_LANES_BOUND` | C1 #3 | 20 mutations | contract | K |
| profile `orchestration/**` | `PROFILE_REQUEST → TASK_DAG → PACKETS` | K #4 | tasks/packets/leases | deterministic plan | A1-A6/E |
| owner A1-A6 | owner-specific public State Machines | canonical owner repos | public deterministic receipts; stronger lanes open | partial public | E/X |
| profile `shadow/**` | `SUBJECT → DENOMINATOR → ADMIT|BLOCK` | Profile-E #19 | read-only Shadow | evaluator | X |
| profile convergence | `EXACT_RECEIPTS → RECONCILE → PLAN_ONLY_CANARY` | Profile-X #22 | #80 / `32321499909` / Shadow `4978282030` | routing only | D |
| profile docs | `PROFILE_X_PINNED → ROUTES/STACK → DOCS_GATE` | Profile-D #23 | #84 / `32326260896` / Shadow `4978669357` | docs only | Root-D |
| root docs | `PROFILE_D_PINNED → ROOT_ROUTES_RENDERED → EXTERNAL_VERIFY → SHADOW` | EAS-D #13 | current Root-D v3 exact target not yet externally verified | docs only | P7 |
| handoff queue | `QUEUE_BOUND → ONE_ACTIVE → EXECUTE → RECEIPT/CLEANUP → REDUCE` | #14 | post-EAS-A P7 rebind required; old #59/#67/#71 authority NONE | preparation/exact local item only | canonical reducer/Human |

## Start/completion law

Start readiness never equals completion readiness. Completion requires exact outputs, declared Gates, cleanup/receipt denominator and canonical-owner readback.

## Current P6 → P7 guard

```text
Profile-D #84 verified + Shadow
→ Root-D v3 candidate
→ external immutable-target Root-D verification
→ fresh Shadow COMMENT
→ only then P7 recompile
```

Google Docs/Sheets and EAS-A projections remain `ADVISORY_ONLY`; they cannot advance any State Machine.