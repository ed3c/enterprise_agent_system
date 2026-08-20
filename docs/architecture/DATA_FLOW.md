# Guarded data flow

## Control / evidence flow

```text
source digest + locators
→ 15 requirements / 14 contradictions
→ strict contracts
→ Tech Lead DAG + zero-context packets
→ canonical A1/A2R/A2/A3/A4/A5/A6 owners
→ exact public/deterministic receipts
→ read-only Shadow + Truth Verify
→ Generic-X + EAS-A advisory reconciliation
→ Profile-X v4
→ Profile-D v5
→ Root-D v3
→ external Root-D verify + Shadow
→ P7 recompile for stronger unresolved lanes
→ Human-owned irreversible transitions
```

## Authority guards

| Flow | Guard |
|---|---|
| source → requirements | source remains `SOURCE_PROPOSAL`; private/local bytes do not egress |
| requirements → contracts | 15/14 denominator cannot shrink |
| K → Worker | one owner + path/resource lease + zero-context packet |
| owner → E/X | exact repo/commit/tree + typed receipt; no self-report |
| EAS-A → X/D | `ADVISORY_ONLY`; Google connectivity/write `NOT_PERFORMED`; source correctness `NOT_PROVEN` |
| Shadow → X | read-only; blocker remains visible |
| X → D | `PLAN_ONLY` stays `PLAN_ONLY` |
| D → Root-D | exact hosted verification + Shadow required |
| Root-D → P7 | current exact receipt required; historical queue/runner/reducer cannot execute |
| P7 → Human | irreversible transitions require Human authority |

## Forbidden flows

```text
Google Doc/Sheet → canonical task/workflow/effect/Human/release state
EAS-A advisory view → closure credit
Google revision/read → source correctness
branch name or mutable URL → immutable receipt
public fixture → provider/private/physical/user/Human PASS
CI green → business/user outcome
HTTP/API acknowledgement → effect completion
PLAN_ONLY canary → executed claim
stale P7 #59/#67/#71 → current Local Handoff authority
model/Judge agreement → Human admission
```

## Current closure projection

```text
requirements_total                   15
requirements_required_lane_satisfied  1
requirements_closure_credit           0
contradictions_total                 14
stronger_no_credit_lanes             13
vertical_canary                      PLAN_ONLY
full_architecture                    BLOCKED_FOR_CLOSURE
profile_release                      NOT_ADMITTED
P7_execution                         NOT_PERFORMED
```