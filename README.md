# enterprise_agent_system

Cross-repository management, routing, traceability, and closure control plane for enterprise Agent programs. EAS binds source requirements to exact Git subjects, dispatches Tech Lead DAG work, records evidence ceilings, runs read-only Shadow reconciliation, and hands stronger work to typed Local Handoff. It does **not** become the canonical runtime, durable workflow/effect engine, provider adapter, independent verifier, Human authority, or release authority.

## Current integrated public state

This tree is the public-main integration candidate produced after the EAS-A rebind and P7 queue/runner/reducer rebuild.

```text
EAS-A #68                                  MERGED_TO_MAIN_AT_ADVISORY_CEILING
public stack integration carrier           ecdb6bb0bbc6e058882e2eeabc49796cde3bebda
carrier tree                               55a1de45870e19dbc0b29a2b402d7a08dd5a3a1e
carrier parent 1                           main after #68 @ 0832cd7e7b5a486fd8924ff9b667bcb6205c1a35
carrier parent 2                           H4RR #107 @ 4a44e9cf9ece133e8117ecc100e419f359d8e1a1
P7 public queue/runner/reducer              COMPLETE_AT_DECLARED_PUBLIC_CEILINGS
ACTIVE local execution                      NOT_PERFORMED
real local receipt                          NOT_OBSERVED
canonical queue advancement                 NOT_PERFORMED
requirements                                15
required evidence lanes satisfied            1
requirement closure credit                   0
contradictions                               14 preserved
stronger no-credit lanes                     13
vertical canary                              PLAN_ONLY / execution_receipt=null
full architecture                            BLOCKED_FOR_CLOSURE
profile release                              NOT_ADMITTED
Human / release / rollback                   NOT_PERFORMED
```

**Main integration is not operational closure.** The public mechanisms are integration-ready; the source/PDF requirement set is not closed because the stronger local/provider/private/effect/user/Human lanes have not earned their required receipts.

## Exact current public lineage

```text
EAS-A #68
  250717db1cad584d50890c0d851153fa2cd755e8
  verify #72 / 32295871632 PASS
  Shadow 4976213414
  ADVISORY_ONLY / PROCESS_DEPENDENCY_NOT_GIT_PARENT

Generic-X #31
  b295eabec7b4c9d4e1f65f7fb0238034f454ae7f
  verify #75 / 32296886625 PASS
  Shadow 4976304922

Profile-X #80
  df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0
  verify #83 / 32321499909 PASS
  Shadow 4978282030

Profile-D #84
  f04f9fc78270c8f97ce978e2ccc161ab4d724ca4
  verify #90 / 32326260896 PASS
  Shadow 4978669357

Root-D #94
  6981c700f9f2f9128ebeebdf80e627178b2be336
  verify #97 / 32342272177 PASS
  Shadow 4979950874

Queue-v4 #99
  75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4
  verify #101 / 32348407481 PASS
  Shadow 4980564966 primary; 4980566877 corroborating

H4R #103
  7be0a69b0046b66799baee2ddb5e305c90d60ec6
  verify #105 / 32349394151 PASS
  Shadow 4980654571

H4RR #107
  4a44e9cf9ece133e8117ecc100e419f359d8e1a1
  tree d088e4fa7a21958efc73f7246a707c2a77b5640a
  verify #109 / 32350502938 PASS
  Shadow 4980770691
```

Verification-only siblings are evidence, never Git parents. EAS-A is a process/advisory dependency of convergence and never a third Profile-X parent.

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

No CI PASS, issue closure, PR merge, Doc/Sheet projection, provider 2xx, model agreement, or transport acknowledgement may jump this ladder.

## Directory → State Machine → DAG → data-flow map

| Directory / surface | Canonical role | State Machine / DAG responsibility | Input | Output / evidence | Current next authority |
|---|---|---|---|---|---|
| `contracts/control-plane/**` | EAS-C contract plane | `REQUEST_BOUND → CONTRACT_LOCKED → SUBJECT_BOUND` | source/owner declarations | strict schemas + fail-closed validator | consumed by EAS-K/EAS-E |
| `src/enterprise_agent_system/**` | EAS-K/E control plane | task DAG, leases, reducer, read-only Shadow | EAS-C records + exact Git subjects | deterministic candidate + Shadow findings | Generic-X convergence |
| `integrations/**` | EAS-A advisory projection plane | `SOURCE_REFERENCE → CAPABILITY_CHECK → REVISION/DIGEST → ADVISORY_PROJECTION` | public Git or provider metadata | `ADVISORY_ONLY`; no canonical mutation | live Google/provider work remains separate |
| `profiles/agent-thinking-inception/**` | profile C/K/E/X/D | requirement/contradiction DAG and profile convergence | bound local source identity + owner receipts | 15 requirements / 14 contradictions / 1 required lane satisfied / 0 closure credit | stronger evidence lanes |
| `evidence/**` | evidence records | immutable receipt/snapshot denominator | exact subjects + Gate observations | PASS/FAIL/BLOCKED/etc. without laundering | Shadow / convergence |
| `plans/**` | orchestration projection | start/completion dependencies + owner routing | capabilities, leases, issue graph | executable task packets / blocked handoff | owning Worker or Local Handoff |
| `prompts/**`, `docs/prompts/**` | fresh-session instruction plane | zero-context P0–P7 packets | exact current machine state | deterministic Agent instructions | Agent Worker / Shadow |
| `docs/architecture/**` | Agent-readable architecture | State Machine + DAG + data flow | canonical machine records | advisory documentation | no state mutation authority |
| `docs/traceability/**` | Git Town / Molecular Stack index | issue→PR→subject→Gate→Shadow→next owner | GitHub receipts | human/Agent navigation index | closure review |
| `handoff/**` | Local Handoff plane | `QUEUE_BOUND → ONE_ACTIVE → EXECUTE → RECEIPT → CLEANUP → REDUCER` | exact queue/runner + admitted local runtime | secret-free receipt candidate | canonical reducer / next epoch |
| `.github/workflows/**` | hosted deterministic Gate plane | immutable target verification | exact commit/tree | deterministic external receipt | Shadow; never local/Human proxy |

## End-to-end DAG and data flow

```text
Local source/PDF proposal
        │
        ▼
C0 source identity ──► C1 strict contracts ──► K profile packets/DAG
        │                                      │
        │                                      ├──► A1/A2R/A2/A3/A4/A5/A6 owner evidence
        │                                      │
        ▼                                      ▼
Generic EAS-C ─► EAS-K ─► EAS-E ─► Generic-X ◄── EAS-A (ADVISORY_ONLY process dependency)
                                            │
                      Profile-E ─────────────┤
                                            ▼
                                      Profile-X #80
                                            ▼
                                      Profile-D #84
                                            ▼
                                        Root-D #94
                                            ▼
                                       Queue-v4 #99
                                            ▼
                                         H4R #103
                                            ▼
                                        H4RR #107
                                            ▼
──────────────────────────── PUBLIC GITHUB BOUNDARY ────────────────────────────
                                            ▼
                   real local ACTIVE execution (NOT_PERFORMED)
                                            ▼
                          external secret-free receipt
                                            ▼
                         H4RR exact semantic readback
                                            ▼
                 canonical reducer / next queue epoch
                                            ▼
        provider/private/physical/effect/user/Human/release lanes
```

Forbidden flows:

```text
Docs/Sheets/GitHub status ─X─► canonical execution state
CI/synthetic fixture       ─X─► LOCAL_PHYSICAL / PROVIDER_LIVE evidence
Shadow                     ─X─► Builder mutation / merge / Human admit
runner                     ─X─► queue advancement
public reducer             ─X─► real-local evidence credit
```

## git-town-stacked-pr-worker — Molecular Stack index

Current implementation stack is intentionally split into product atoms and evidence-only siblings.

| Molecular atom | Current product PR | Exact role | Verification sibling | Integration disposition |
|---|---:|---|---:|---|
| EAS-C | #20 | control-plane contracts | inherited downstream Gates | `INTEGRATED_THROUGH_PUBLIC_CONVERGENCE` |
| EAS-K | #24 | Tech Lead DAG / leases / packets | inherited downstream Gates | `INTEGRATED_THROUGH_PUBLIC_CONVERGENCE` |
| EAS-E | #25 | read-only Shadow mechanism | hosted E Gate | `INTEGRATED_THROUGH_PUBLIC_CONVERGENCE` |
| EAS-X | #31 | generic cross-repo convergence | #75 | `INTEGRATED_THROUGH_PUBLIC_CONVERGENCE` |
| EAS-A | #68 | advisory GitHub/Google adapter | #72 | `MERGED_DIRECT_TO_MAIN` |
| Profile C0/C1 | #21 / #28 | source + strict contracts | profile Gates | `INTEGRATED_THROUGH_PUBLIC_CONVERGENCE` |
| Profile-K/A4/E | #29 / #30 / #32 | profile packets/provenance/Shadow | profile Gates | `INTEGRATED_THROUGH_PUBLIC_CONVERGENCE` |
| Profile-X | #80 | current profile convergence | #83 | `INTEGRATED_THROUGH_PUBLIC_CONVERGENCE` |
| Profile-D | #84 | current profile docs/traceability | #90 | `INTEGRATED_THROUGH_PUBLIC_CONVERGENCE` |
| Root-D | #94 | root Agent-readable docs | #97 | `INTEGRATED_THROUGH_PUBLIC_CONVERGENCE` |
| P7 Queue | #99 | one-ACTIVE Local Handoff queue | #101 | `INTEGRATED_THROUGH_PUBLIC_CONVERGENCE` |
| H4R | #103 | fail-closed local runner | #105 | `INTEGRATED_THROUGH_PUBLIC_CONVERGENCE` |
| H4RR | #107 | public receipt semantic reducer | #109 | `PUBLIC_CONVERGENCE_CARRIER` |

Historical/no-current-authority PRs remain searchable rather than rewritten: #27, #40, #44, #50, #55, #57, #59, #67, #71, #77, #79, #92, #95 and their associated historical verifiers. See `docs/traceability/MOLECULAR_STACK_INDEX.md`.

## Real-problem closure audit

The bound Agent Thinking Inception source/PDF problem is **not operationally closed**.

```text
requirements total                  15
required evidence lanes satisfied    1
requirement closure credit           0
contradictions preserved            14
stronger no-credit lanes            13
source correctness                  NOT_PROVEN
Google connectivity/write           NOT_PERFORMED
vertical canary                     PLAN_ONLY
business/user outcome               NOT_VERIFIED
Human admission                     NOT_PERFORMED
release/rollback                    NOT_PERFORMED
```

Implemented public mechanisms therefore may be merged/closed at their bounded objectives while program issue #6 and Local Handoff #14 remain open for the unresolved real-world denominator.

## Local Handoff — current execution queue

Current public queue truth:

```text
queue_id              LH-EAS-INCEPTION-P7-V4-2026-08-20
items                 11
ACTIVE                 1 = LH-P7-01-ROOT-D-V3-LOCAL-READBACK
blocked successors     9
Human terminal         1
main commands          9
cleanup commands       3
queue execution       NOT_PERFORMED
```

Execution authority remains exact H4R #103, not an arbitrary future main HEAD. H4RR #107 may inspect the resulting external receipt but cannot self-grant real-local credit or mutate the queue. See `handoff/README.md` and issue #14.

## Repository ownership

| Plane | Canonical owner | Owns | Does not own |
|---|---|---|---|
| Control / closure | `enterprise_agent_system` | source/requirement graph, Tech Lead routing, convergence, docs projection, Local Handoff contract | runtime/effect execution, Human release |
| Portable method | `skills-shared` | Tech Lead/Shadow/Stack/Handoff methodology | repo-specific canonical state |
| Runtime contract | `runtime-env` | workload/capability/policy contracts | provider secrets/effect state |
| Workflow/effect | `bettor-arena` | durable state, compaction/recovery, ingress/effects | provider adapter runtime |
| Provider adapter | `agent-shield-monorepo` | sandbox, steering, provider/runtime/telemetry adapters | EAS closure/Human authority |
| Independent verification | `truth-verify-loop` | exact source/code/effect/user-result verification | implementation mutation |
| Source anchoring | `openwiki-source-anchoring` | lexical source/path/span anchors | semantic/release authority |

One interface or canonical state has one owner. Process dependencies are not automatically Git ancestry.