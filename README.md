# enterprise_agent_system

Cross-repository **management, routing, traceability, and closure control plane** for enterprise Agent programs. EAS binds proposals to immutable subjects, compiles Tech Lead DAGs and fresh-session packets, reconciles read-only Shadow findings, projects Molecular Stack state, and routes stronger work to Local Handoff. It is not a second runtime, durable workflow/VFS/effect ledger, provider adapter, independent verifier, Human authority, or release authority.

## Current literal verdict

```text
P0-P5 control/profile candidates        COMPLETE_AT_DECLARED_PUBLIC_EVIDENCE_CEILING
P6 Profile-D                            ADMIT_FOR_ROOT_EAS_D / PR #44
P6 Root-D v2                            ROOT_D_CANDIDATE / external verification required
P7 Local Handoff                        BLOCKED_PENDING_CURRENT_ROOT_D_RECEIPT
requirements                            15
contradictions                          14
stronger no-credit lanes                13
source-required lanes satisfied         1
requirement closure credit              0
Profile-X hosted Gate                   ABSENT
vertical canary                         PLAN_ONLY / execution_receipt=null
EAS-A projection adapters               NOT_IMPLEMENTED / subject=null / credit=0
full architecture                       BLOCKED_FOR_CLOSURE
profile release                         NOT_ADMITTED
Human admission                         NOT_PERFORMED
merge / release / rollback              NOT_PERFORMED
```

Documentation completeness is not operational closure.

## Exact current P5/P6 inputs

```text
Generic EAS-X PR #31
  commit 8b1bfa38c103e1c064b8ef0aafecfc8f2a2642dc
  tree   9c8fb0e8e25f357fdb695a94c4ab74fc3dcd4631
  Shadow 4973896050 = ADMIT_FOR_PROFILE_X_REBIND

Profile-E PR #32
  commit 9f25b94ca891faf0d926b0fc22b67be88925aa81
  tree   1452d1b9931c70ef70ed3b7dec78cedc51d6db35
  Shadow 4973593318 = ADMIT_FOR_PROFILE_CONVERGENCE

Profile-X v3 PR #40
  commit fe2748e09a5222f439f09c5d0d71e486e1ade3e8
  tree   0425916bea831c125702696544ae2848fdf9bd0e
  Shadow 4974017388 = ADMIT_FOR_P6_DOCUMENTATION_PREPARATION
  hosted Profile-X Gate ABSENT

Profile-D v4 PR #44
  commit a7a034ef1db778fcee586fff8d8ff7848bc9a1ab
  tree   62796ebb2e48e60ab30809470d3b6c02f44009fc
  hosted verification 32282726313 PASS
  Shadow 4975046170 = ADMIT_FOR_ROOT_EAS_D
```

Root-D v2 is a **direct Git child of Profile-D v4**. A second Generic-X + Profile-D merge is unnecessary because current Profile-X v3 already has Generic-X + Profile-E as true multi-parent ancestry. Historical PR #41 used an obsolete multi-parent base and is no longer current authority.

Current A1 hosted receipt is `32259216877`. The stale value `32259476821` is forbidden in current machine authority and is retained only in explicit historical/failure records.

## Closure ladder

```text
SOURCE_PROPOSAL
→ OWNER_AND_CONTRACT_BOUND
→ MECHANISM_IMPLEMENTED
→ DETERMINISTIC_EVIDENCE_VERIFIED
→ LIVE_OR_PHYSICAL_EVIDENCE_VERIFIED
→ USER_OUTCOME_VERIFIED
→ HUMAN_ADMITTED
→ RELEASED
→ OPERATED_WITH_ROLLBACK
```

Every transition requires its own lane-literal exact-subject receipt. CI, PR state, issue state, model agreement, API acknowledgement, local fixture, or documentation cannot proxy a stronger lane.

## Canonical repository roles

| Plane | Canonical repository | Owns | Does not own |
|---|---|---|---|
| Control / closure | `enterprise_agent_system` | source/requirement graph, contracts, Tech Lead routing, convergence, docs projection, Local Handoff contract | runtime execution, durable business workflow/effects, independent truth, Human release |
| Portable method | `skills-shared` | Tech Lead/Shadow/Stack/Local-Handoff methodology | repo-specific operational state |
| Runtime contract | `runtime-env` | workload/capability/policy/environment contracts | provider secrets, workflow/effect state |
| Workflow/effect | `bettor-arena` | durable Domain State, compaction/recovery, ingress/effect identity, retries/reconciliation | provider-specific runtime adapters |
| Provider/runtime | `agent-shield-monorepo` | sandbox, steering, provider/runtime/telemetry adapters | EAS closure or Human release |
| Independent verification | `truth-verify-loop` | exact source/code/effect/user-result verification and disagreement receipts | implementation mutation or canonical reduction |
| Source anchoring | `openwiki-source-anchoring` | lexical/path/span anchors | semantic or release authority |

One interface or canonical state has one owner.

## Eight phases

| Phase | Role | Current profile state |
|---|---|---|
| P0 | Source & Authority Auditor | source denominator frozen |
| P1 | Contract Lock Worker | deterministic contracts |
| P2 | Tech Lead Controller | deterministic DAG/packets |
| P3 | Parallel Owner Wave | public/deterministic partial evidence |
| P4 | Shadow Architect | admitted for convergence; stronger lanes open |
| P5 | Convergence Owner | Profile-X v3 admitted for P6 preparation |
| P6 | Docs / Stack Convergence | Profile-D v4 admitted; Root-D v2 candidate |
| P7 | Local Handoff Compiler | blocked until current Root-D external receipt |

## Current Molecular Stack

```text
C0 → C1 → K
            ├─ A1
            ├─ A2R → A2
            ├─ A3
            ├─ A4
            ├─ A5
            └─ A6
                 ↓ evidence
              Profile-E
Generic EAS-X ──┬── true multi-parent input
Profile-E ──────┘
                 ↓
          Profile-X v3 PR #40
                 ↓ true child
          Profile-D v4 PR #44
                 ↓ true child
          Root-D v2 candidate
                 ↓ external verification + Shadow only
          P7 Local Handoff preparation
```

Process/evidence order is not automatically Git ancestry. See `docs/traceability/MOLECULAR_STACK_INDEX.md`.

## Repository map

```text
enterprise_agent_system/
├── README.md / AGENTS.md / ARCHITECTURE.md / CONTEXT.md
├── contracts/control-plane/
├── src/enterprise_agent_system/
├── plans/ + evidence/
├── profiles/agent-thinking-inception/
│   ├── source/ requirements/ contracts/ orchestration/
│   ├── shadow/ evidence/convergence/
│   ├── plans/ prompts/ docs/ tests/
├── docs/architecture/ prompts/ traceability/
├── prompts/README.md
└── handoff/
```

Directory presence is not execution evidence.

## GitHub / Google authority

- GitHub exact commits/trees plus typed Actions/review receipts are canonical publication metadata.
- Google Docs and Google Sheets are `ADVISORY_ONLY` projections.
- Google wording or URL existence cannot mutate task/workflow/effect/Human/release state.
- EAS-A #10 remains `NOT_IMPLEMENTED` until an exact projection-adapter subject exists.

## Historical/no-authority denominator

```text
old Profile-X PR #33                         authority NONE
Profile-X v2 PR #36                          authority NONE
old Profile-D PR #37                         authority NONE
old Profile-D verifier PR #39                authority NONE
old Root-D PR #41 / verifier #43             authority NONE for current P6
old P7 PR #50 / verifier #51                 authority NONE for current P7 until rebound
historical EAS-D blueprint PR #26             blueprint only
```

No force rewrite hides these paths.

## Open stronger lanes

```text
physical power-loss / multi-host durability       NOT_EXERCISED
network / gVisor isolation                        NOT_EXERCISED
provider capability / enrollment                  NOT_EXERCISED
external independent semantic verification        NOT_EXERCISED
private evidence                                   NOT_EXERCISED
exact external Model/Data/Trace terms              UNBOUND
live telemetry export/store/delete                NOT_EXERCISED
external candidate benchmark                      NOT_EXERCISED
real external effect / remote readback            NOT_PERFORMED
compensation                                       NOT_EXERCISED
business/user outcome                              NOT_VERIFIED
Human legal/security/admission                     HUMAN_ADMIT_REQUIRED
merge / release / rollback                         NOT_PERFORMED
```

## Next authority

Root-D v2 must receive an **external immutable-target hosted verification** and a fresh read-only Shadow review. Only that external receipt may authorize P7 preparation. P7 execution, provider/private/physical work, external effects, Human admission, merge, release, and rollback remain separate authorities.