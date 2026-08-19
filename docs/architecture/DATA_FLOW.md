# Guarded data flow

## Control / evidence flow

```text
source digest + page locators
  -> source/requirement graph (15 requirements / 14 contradictions)
  -> strict C/C1 contracts
  -> Tech Lead K/profile-K DAG + fresh-session packets
  -> canonical A1/A2R/A2/A3/A4/A5/A6 owners
  -> exact deterministic/public receipts
  -> read-only Shadow + independent Truth Verify
  -> profile X + generic X convergence
  -> profile D + root D documentation projection
  +-> Local Handoff for stronger unresolved lanes
  -> Human-owned irreversible transitions
```

Every arrow has an evidence/authority guard. A downstream consumer may only claim the evidence class actually returned by the upstream owner.

## Runtime/effect flow owned outside EAS

```text
provider event
-> provider-specific auth/replay
-> durable inbox + dedupe
-> versioned Domain State
-> deterministic macro DAG
-> bounded sandbox/sub-agent
-> content-addressed artifacts/candidate receipts
-> deterministic physical gates
-> independent semantic/Shadow verification
-> typed WriteIntent
-> idempotent effect ledger
-> external API/browser adapter
-> remote readback / UNKNOWN_EFFECT reconciliation
-> Domain State update
-> sanitize-before-export telemetry
-> lane-literal closure receipt
```

EAS documents/routes this flow; canonical runtime/effect owners implement it.

## Authority guards

| Flow | Guard |
|---|---|
| source → requirements | source remains `SOURCE_PROPOSAL`; private/local bytes do not egress |
| requirements → contracts | 15/14 denominator cannot shrink |
| contracts → K | exact schema/version/digest |
| K → Worker | one owner, path/resource lease, zero-context packet |
| A2R → A2 | current runtime owner head and consumed contract pin stay distinct |
| owner → Shadow/X | exact repository/commit/tree + typed receipt; no self-report |
| A4 evidence → X | synthetic telemetry/provenance cannot become legal/live-runtime clearance |
| A6 → effect completion | transport/attempt is not `COMMITTED`; UNKNOWN_EFFECT blocks blind retry |
| Shadow → X | Shadow is read-only; `BLOCKED_FOR_CLOSURE` remains visible |
| X → D | docs may project facts only; PLAN_ONLY stays PLAN_ONLY |
| X/D → Local Handoff | blocked successor only; ACTIVE queue unchanged until exact receipt |
| Local Handoff → Human | irreversible transitions require Human authority |

## Forbidden flows

```text
Google Doc/Sheet -> canonical task/workflow/effect/Human/release state
branch name or mutable URL -> immutable receipt
public fixture -> provider/private/physical/user/Human/release PASS
model/Judge agreement -> Human admission
CI green -> business/user outcome
HTTP/API acknowledgement -> durable task/effect completion
Profile-D/root-D docs -> runtime/effect state mutation
process dependency -> invented Git ancestry
PLAN_ONLY vertical canary -> executed end-to-end claim
license whitelist/AST rewrite -> legal/commercial clearance
local telemetry -> zero-leakage claim
```

## Current closure projection

```text
requirements_total                 15
requirements_required_lane_satisfied 1
requirements_closure_credit         0
contradictions_total               14
contradictions_preserved           14
profile_shadow                     BLOCKED_FOR_CLOSURE
vertical_canary                    PLAN_ONLY
profile_release                    NOT_ADMITTED
```

## Evidence lanes still blocked

Physical/multi-host recovery, network/gVisor isolation, provider capability/enrollment, external independent semantic/private evidence, exact external Model/Data/Trace terms, live telemetry, external benchmark, real external effect/readback, compensation, business/user outcome, Human legal/security/admission, merge/release/rollback all remain separate next-epoch receipts.