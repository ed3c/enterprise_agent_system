# enterprise_agent_system

Cross-repository **management, routing, traceability, and closure control plane** for enterprise Agent programs. It binds source proposals to immutable Git subjects, compiles Tech Lead DAGs and fresh-session prompt packets, reconciles independent Shadow findings, projects Molecular Stack status, and routes blocked work to Local Handoff without becoming a second runtime, workflow engine, VFS, effect ledger, verifier, provider adapter, Human authority, or release authority.

## Current verdict

```text
P0-P5 generic/profile control-plane candidates   COMPLETE_AT_DECLARED_PUBLIC_EVIDENCE_CEILING
P6 profile documentation candidate               COMPLETE / PR #37
P6 root documentation candidate                  COMPLETE_AT_DOCS_CEILING / PR #41
P7 Local Handoff                                 READY_FOR_PREPARATION / execution NOT_PERFORMED
requirements                                     15/15 exact owner subjects
required evidence lanes satisfied                 1/15
requirement closure credit                        0
contradictions                                   14/14 preserved
contradictions resolved                           0
profile Shadow                                   BLOCKED_FOR_CLOSURE
vertical canary                                  PLAN_ONLY / execution_receipt=null
EAS-A projection adapters                        NOT_IMPLEMENTED / subject=null / credit=0
physical/provider/private/user/Human/release     OPEN
profile release                                  NOT_ADMITTED
```

Documentation completeness is not operational closure.

## Exact convergence inputs

```text
Generic EAS-X
  PR       #31
  commit   3f8af3d75b28ca1904fe07b8ea9ee0d291f5989c
  tree     e1be41234ff336297ce591b564291c9a0cd819ed
  Shadow   4973461122 = ADMIT_FOR_DOWNSTREAM_REVIEW

Profile-X
  PR       #33
  commit   a27aa552f1c258e09f515b4a5d117ba37f4d6615
  tree     71eaa3f4acafd0b004ccdff16e4aa14bc2599649
  XV run   32268112684 PASS
  Shadow   4973663047 = ADMIT_FOR_P6_REVIEW

Profile-D
  PR       #37
  commit   690154a5f7154d551bef6942fe5d1f34091c2197
  tree     1a2e02d4c92b882f51f8c8d28f70771648a6a528
  DV run   32270454491 PASS
  Shadow   4973885537 = ADMIT_FOR_ROOT_EAS_D_REVIEW
```

Root EAS-D starts from a real multi-parent convergence commit that contains both Generic-X and Profile-D bytes. Historical docs PR #26 is a documentation blueprint only and is not final P6 evidence. The final root-D commit/tree and external exact-target verification/Shadow receipt live outside the reviewed branch to avoid a self-referential receipt loop.

## Why this repository exists

The Agent Thinking Inception source proposes compaction, VFS persistence, dynamic steering, parallel sub-agents, deterministic gates, citation repair, Code/Model/Data/Trace screening, continuous repository convergence, issue-triggered execution, sandboxing, telemetry, and writeback. The production architecture is stricter:

```text
SOURCE_PROPOSAL
-> OWNER_AND_CONTRACT_BOUND
-> MECHANISM_IMPLEMENTED
-> DETERMINISTIC_EVIDENCE_VERIFIED
-> LIVE_OR_PHYSICAL_EVIDENCE_VERIFIED
-> USER_OUTCOME_VERIFIED
-> HUMAN_ADMITTED
-> RELEASED
-> OPERATED_WITH_ROLLBACK
```

Every transition needs its own exact-subject receipt. Markdown, issue state, green CI, model agreement, local fixtures, API acknowledgements, or provider self-report cannot proxy a later lane.

## Canonical repository roles

| Plane | Canonical repository | Owns | Does not own |
|---|---|---|---|
| Control / closure | `enterprise_agent_system` | source/requirement graph, contracts, Tech Lead routing, convergence, docs projection, Local Handoff contract | runtime execution, durable business workflow/effects, independent truth, Human release |
| Portable method | `skills-shared` | Tech Lead/Shadow/Stack/Local-Handoff methodology | repo-specific state |
| Runtime contract | `runtime-env` | workload/capability/policy/environment contracts | provider secrets, workflow/effect state |
| Workflow/effect | `bettor-arena` | durable Domain State, compaction/recovery, ingress/effect identity, retries/reconciliation | provider-specific runtime adapters |
| Provider/runtime adapter | `agent-shield-monorepo` | sandbox, steering, provider/runtime/telemetry adapter behavior | EAS canonical closure or Human release |
| Independent verification | `truth-verify-loop` | exact source/code/effect/user-result verification and disagreement receipts | implementation mutation or canonical reduction |
| Source anchoring | `openwiki-source-anchoring` | exact lexical path/span anchors | semantic or release authority |

One interface or canonical state has one owner.

## Eight phases

| Phase | Role | Output | Current profile state |
|---|---|---|---|
| P0 | Source & Authority Auditor | source digest, 15 requirements, 14 contradictions | deterministic candidate |
| P1 | Contract Lock Worker | strict generic/profile contracts | deterministic candidate |
| P2 | Tech Lead Controller | task DAG, leases, 10 worker packets | deterministic candidate |
| P3 | Parallel Owner Wave | A1-A6 owner implementations/receipts | public/deterministic partial evidence |
| P4 | Shadow Architect | independent mutation/evidence-ceiling review | public denominator admitted; full closure blocked |
| P5 | Convergence Owner | exact cross-repo/profile closure candidate | complete at routing ceiling |
| P6 | Docs / Stack Convergence | Agent-readable routes, State Machines, data flow, prompts, Stack | profile + root candidates complete at docs ceiling |
| P7 | Local Handoff Compiler | concrete local/provider/physical execution queue | ready for preparation; execution not performed |

## Molecular Stack

Generic control plane:

```text
C -> K -> E -> X -> D
     A = sibling projection adapter atom; currently NOT_IMPLEMENTED
```

Profile program:

```text
C0 -> C1 -> K
             +-> A1 durable state/compaction/recovery
             +-> A2R runtime contract -> A2 sandbox/steering
             +-> A3 exact evidence
             +-> A4 provenance/telemetry policy evidence
             +-> A5 discovery/admission
             +-> A6 ingress/effects
             -> E read-only Shadow
             -> X exact-subject convergence
             -> D profile docs
             -> root EAS-D
```

Process ordering is not automatically Git ancestry. Exact parent relations and immutable subjects are documented in `docs/traceability/MOLECULAR_STACK_INDEX.md` and the profile machine index under `profiles/agent-thinking-inception/plans/`.

## Repository map

```text
enterprise_agent_system/
├── README.md
├── AGENTS.md
├── ARCHITECTURE.md
├── CONTEXT.md
├── contracts/control-plane/             # generic C
├── src/enterprise_agent_system/          # generic K/E/X primitives
├── plans/                                # generic X DAG/Stack candidates
├── evidence/                             # exact public/Shadow/convergence receipts
├── profiles/agent-thinking-inception/
│   ├── source/                           # P0
│   ├── requirements/                     # 15 + 14 denominator
│   ├── contracts/                        # P1
│   ├── orchestration/                    # P2 K
│   ├── shadow/                           # profile E
│   ├── evidence/convergence/             # profile X receipts
│   ├── plans/                            # X/D machine indexes
│   ├── prompts/                          # content-addressed prompt catalogue
│   ├── docs/                             # profile D route
│   └── tests/                            # deterministic semantic controls
├── docs/
│   ├── INDEX.md
│   ├── architecture/
│   ├── prompts/
│   └── traceability/
├── prompts/README.md
└── handoff/                              # canonical P7 queue contract
```

Directory presence never proves execution. See `docs/architecture/STATE_MACHINES.md` for directory → owner → State Machine → Gate → evidence-ceiling routing.

## Process/evidence flow

```text
local-only source digest
-> requirement/contradiction graph
-> strict contracts
-> Tech Lead DAG + zero-context packets
-> canonical owner implementations
-> exact public/deterministic receipts
-> independent Shadow + Truth Verify
-> profile and generic convergence
-> documentation projection
+-> Local Handoff for stronger lanes
-> Human-owned irreversible transitions
```

Detailed guards and forbidden flows are in `docs/architecture/DATA_FLOW.md` and `profiles/agent-thinking-inception/plans/data-flow.json`.

## Prompt contract

P0-P7 prompts are indexed under `docs/prompts/` and `prompts/README.md`. Every fresh session must receive exact repository/commit/tree inputs, objective/non-goals/invariants/unknowns, one role/owner, writable/read-only/forbidden paths, start/completion dependencies, inputs/outputs, positive and mutation controls, runtime/capability requirements, evidence ceiling, timeout/retry/cleanup/rollback, required receipt, claims-not-proven, stop conditions, and next authority. Hidden prior chat memory is never required.

## GitHub / Google authority

- **GitHub** is canonical publication metadata: issues, PRs, exact commits/trees, code review, Actions receipts.
- **Google Docs** may be an advisory narrative/review copy.
- **Google Sheets** may be an advisory dashboard/matrix.
- Docs/Sheets are `ADVISORY_ONLY`; URL existence or wording cannot write task/workflow/effect/Human/release state.
- EAS-A #10 owns future GitHub/Google projection adapters and remains `NOT_IMPLEMENTED` until an exact implementation subject exists.

## Open evidence lanes

```text
physical power-loss / multi-host durability        NOT_EXERCISED
network / gVisor isolation                         NOT_EXERCISED
provider capability / enrollment                   NOT_EXERCISED
external independent semantic verification         NOT_EXERCISED
private evidence                                    NOT_EXERCISED
exact external Model/Data/Trace terms              PARTIAL_OR_UNBOUND
live telemetry export/store/delete                 NOT_EXERCISED
external candidate benchmark                       NOT_EXERCISED
real external effect / remote readback             NOT_PERFORMED
compensation                                        NOT_EXERCISED
business/user outcome                               NOT_VERIFIED
Human legal/security/admission                      HUMAN_ADMIT_REQUIRED
merge / release / rollback                         NOT_PERFORMED
```

A docs/CI PASS cannot promote these states.

## Next authority

P7 consumes an external exact-head EAS-D verification and Shadow receipt; that receipt is intentionally not written back into the branch it reviews. Stronger execution remains under Local Handoff #14 and canonical owner issues. P7 execution is `NOT_PERFORMED` until the queue/runtime/capability/receipt contract admits a concrete epoch. No root documentation state authorizes merge, provider activation, private-data egress, Human admission, release, or rollback.