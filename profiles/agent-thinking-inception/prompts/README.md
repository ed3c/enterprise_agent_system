# Agent Thinking Inception — P0–P7 Prompt Catalogue

This catalogue is a **documentation projection**, not an execution engine. Every
entry is either a committed prompt blob or a deterministic render route from the
exact Profile-K packet specification. Chat history is never an input to a fresh
session.

## Current catalogue inputs

```text
Profile-X v3 parent
  PR     #40
  commit fe2748e09a5222f439f09c5d0d71e486e1ade3e8
  tree   0425916bea831c125702696544ae2848fdf9bd0e
  Shadow 4974017388

Profile-K packet source
  profiles/agent-thinking-inception/orchestration/profile-worker-packet-specs.json
  blob e088ead98d9f11590bd8b9621dce64f2e25fcbbe

Packet renderer
  profiles/agent-thinking-inception/orchestration/compile_profile_packets.py
  blob 7e320dbfce8119002ad53b3a20291598490d3610

Rendered packet bundle
  sha256:dc4473b3195a738e55eb49c43661b6e1f4ea7f95c66749454776f2003b18ebc3

P7 deterministic queue contract
  EAS-H PR #27
  commit 9223107163b27984ed490246b4c0899caeb1bdae
  tree   d462e2a1a69d225bf8161ce01918e5e8bb8d102f
  queue execution NOT_PERFORMED
```

## Catalogue

| Phase | Role | Prompt source | Current immutable identity / route |
|---|---|---|---|
| P0 | Source & Authority Auditor | `00-source-auditor.system.md` | Git blob `e786de9d2465d551bab625e03a8dbf3321bdb102` |
| P1 | Profile Contract Lock Worker | `01-profile-contract-worker.system.md` | Git blob `53d6752f246062f537b24f14ad6ff2fb5253e654` |
| P2 | Profile Tech Lead Controller | `02-tech-lead-profile-controller.system.md` | Git blob `e3115597a6344b0fb26bc3f3e2d6beba973614ee` |
| P2/P3 | Common fresh-session Worker envelope | `03-profile-worker-envelope.system.md` | Git blob `c8073d5ccc250e61a4bb0e78c0e60744473ac40b` |
| P3 | A1 compaction/recovery owner | render `TASK-INCEPTION-A1` | Profile-K packet bundle digest above |
| P3 | A2 runtime/sandbox/steering owner | render `TASK-INCEPTION-A2`; bind exact A2R contract owner and consumed pin separately | Profile-K packet bundle digest above |
| P3 | A3 exact-evidence owner | render `TASK-INCEPTION-A3` | Profile-K packet bundle digest above |
| P3 | A4 provenance/telemetry owner | render `TASK-INCEPTION-A4` | Profile-K packet bundle digest above |
| P3 | A5 discovery/admission owner | render `TASK-INCEPTION-A5` | Profile-K packet bundle digest above |
| P3 | A6 ingress/effect owner | render `TASK-INCEPTION-A6` | Profile-K packet bundle digest above |
| P4 | Profile Shadow Architect | `10-shadow-architect-profile.system.md` | Git blob `884d8037653b8ffc89f825b7939cb03c455ec873`; PR #32 / Shadow `4973593318` |
| P5 | Profile Convergence Owner | `11-profile-convergence.system.md` | Git blob `7f855e4d3ae637354dc474c45bfc5cd6dc15cb7c`; PR #40 / Shadow `4974017388` |
| P6 | Profile Docs / Stack Convergence | `12-profile-docs-convergence.system.md` | Current Profile-D authored file; final immutable blob is bound by the P6 verification receipt, not self-declared here |
| P7 | Local Handoff Compiler | render `TASK-INCEPTION-H` and consume EAS-H #27 queue contract | Profile-K packet bundle + exact PR #27 subject; queue execution remains `NOT_PERFORMED` |

## Phase handoff map

```text
P0 → P1
source identity + requirement/contradiction graph

P1 → P2
strict source-specific contracts + owner/required-lane bindings

P2 → P3
fresh-session owner packets + start/completion DAGs + leases

P3 → P4
exact owner subjects + typed public/deterministic receipts

P4 → P5
read-only Profile Shadow denominator + stronger no-credit lanes

P5 → P6
Profile-X v3 exact subject + 15/14/13/1/0 closure projection
+ PLAN_ONLY canary

P6 → P7
only after external Profile-D verification and root EAS-D convergence

P7 → Human / canonical reducer
only exact local/provider/physical receipts can advance their declared lane
```

## Fresh-session contract

Every direct or rendered system prompt must bind all of the following without
hidden prior-chat context:

```text
exact repository / commit / tree
source/profile identity, digest and class
objective + non-goals
invariants + unknowns
one role + one owner issue
writable / read-only / forbidden paths
resource leases
start dependencies + completion dependencies
input/output contracts
positive controls + planted disagreement controls
runtime/capability requirements
evidence lane + evidence ceiling
retry budget + timeout
cleanup/residue/retention/rollback limits
required receipt fields
stop conditions
claims_not_proven
next authority
```

A prompt or packet existing does **not** mean the task executed.

## Deterministic P3/P7 rendering

Canonical renderer:

```text
python3 profiles/agent-thinking-inception/orchestration/compile_profile_packets.py --output <isolated-dir>
```

The renderer must produce the expected task JSON packets, fresh-session system
prompts and manifest from the exact packet specification. Rendered prompts remain
candidates until their bytes/digests are read back by the receiving phase.

## Current P5/P6 truth that prompts must preserve

```text
requirements                   15
contradictions                 14
stronger no-credit lanes       13
source-required lanes satisfied 1
requirement closure credit      0
Profile-X hosted Gate           ABSENT
vertical canary                 PLAN_ONLY
vertical canary digest          sha256:7a881bbe4b2b9605d56838f5f1e9a3c76dbf45ebc1b0aa7a973fd1329f88efbb
execution receipt               null
highest profile projection      DETERMINISTIC_EVIDENCE_VERIFIED
full architecture               BLOCKED_FOR_CLOSURE
profile release                 NOT_ADMITTED
```

The current A1 hosted run is `32259216877`; `32259476821` is historical stale
metadata only and must not re-enter current prompt inputs.

## Authority boundary

- GitHub issue/PR/commit/tree/Actions/review identities are publication/evidence metadata with typed scope.
- Google Docs may project long-form reviews and prompt copies; Google Sheets may project human dashboards.
- Google Docs/Sheets are `ADVISORY_ONLY` and cannot write Task, Workflow, Effect, Human, merge, release or rollback state.
- A model/Judge output cannot replace Shadow or Human authority.
- A fresh-session prompt cannot infer missing secrets, provider capabilities, private source bytes or Human decisions.
- P6 documentation and P7 queue compilation cannot self-authorize execution.
