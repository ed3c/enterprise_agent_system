# Root guarded data flow

## Canonical flow

```text
SOURCE_PROPOSAL
  ↓ exact digest + locators
15 requirements / 14 contradictions
  ↓ strict contracts
Tech Lead DAG + fresh-session packets
  ↓ disjoint owner leases
A1 / A2R / A2 / A3 / A4 / A5 / A6
  ↓ public receipts
Profile-E read-only Shadow
  ↓ evidence
Generic-X + Profile-E
  ↓ true multi-parent Git input
Profile-X #80
  ↓ true Git child
Profile-D #84
  ↓ true Git child
Root-D v3 candidate
  ↓ external exact-target verification
Root-D Shadow
  ↓ if admitted
P7 queue recompilation
  ↓ only after future real local/provider receipts
next epoch or HUMAN_ADMIT_REQUIRED
```

EAS-A #68 participates only as an advisory/process dependency:

```text
EAS-A #68
250717db1cad584d50890c0d851153fa2cd755e8
ADVISORY_ONLY
PROCESS_DEPENDENCY_NOT_GIT_PARENT
       ├─ GitHub projection semantics
       └─ Google Docs/Sheets advisory projection semantics
```

It cannot mutate canonical workflow/effect/Human/release state and does not prove Google connectivity/write/source correctness.

## Current exact guards

| Edge | Guard |
|---|---|
| Generic-X → Profile-X | `b295eabe...`, verify `32296886625`, Shadow `4976304922` |
| Profile-E → Profile-X | `9f25b94c...`, Shadow `4973593318` |
| EAS-A → Profile-X | process dependency only; `ADVISORY_ONLY`, verify `32295871632`, Shadow `4976213414` |
| Profile-X → Profile-D | PR #80 `df4cd19d...`, verify `32321499909`, Shadow `4978282030` |
| Profile-D → Root-D | PR #84 `f04f9fc...`, verify `32326260896`, Shadow `4978669357` |
| Root-D → P7 | blocked until exact Root-D external verifier + fresh Shadow |
| P7 → Local execution | blocked until a newly compiled current queue/runner exists |
| Local/provider → Human | receipt cannot self-promote Human state |

## Closure projection carried through every edge

```text
requirements_total                  15
requirements_required_lane_satisfied 1
requirements_closure_credit          0
contradictions_total                14
contradictions_preserved            14
stronger_no_credit_lanes            13
vertical_canary                     PLAN_ONLY
vertical_execution_receipt          null
full_architecture                   BLOCKED_FOR_CLOSURE
profile_release                     NOT_ADMITTED
P7_execution                        NOT_PERFORMED
```

## Forbidden flows

```text
Google Doc/Sheet edit        -X-> canonical task/workflow/effect/Human state
EAS-A advisory PASS          -X-> Google live/write/source correctness
CI green                     -X-> user outcome
owner receipt                -X-> integrated vertical execution
PLAN_ONLY canary             -X-> EXECUTED
model/Shadow agreement       -X-> HUMAN_ADMITTED
old P7 #59                   -X-> current Local execution
old H3R/H3RR #67/#71        -X-> current queue advancement
historical #77/#79           -X-> current Profile-X ancestry
```

## Failure denominator

Profile-D verification retains:

```text
32325143724 RED
32325653265 RED
32325967828 RED
32326260896 PASS
```

A downstream projection must retain these as history and use only the final exact green subject for current deterministic credit.

## Cleanup / rollback routing

Execution-side cleanup, residue, compensation, and rollback remain owner/local/Human responsibilities. Root-D documents those routes but does not execute them. P7 recompilation must bind exact cleanup commands and receipts before any future ACTIVE item can advance.