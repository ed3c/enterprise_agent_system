# Directory → State Machine → DAG ownership

This document is a root projection. Canonical machine details live in generic `plans/**` and `profiles/agent-thinking-inception/plans/**`.

| Directory / surface | State Machine | Canonical owner / atom | Inputs | Outputs / next owner | Gate / blocker | Evidence ceiling |
|---|---|---|---|---|---|---|
| `contracts/control-plane/**` | `UNBOUND -> STRICT_CONTRACT -> CONSUMER_READY` | EAS-C / #8 | source identity, authority laws | generic records → K/E/X | shape + semantic mutation gates | contract candidate |
| `src/enterprise_agent_system/orchestration.py` | `REQUEST_BOUND -> DAG -> PACKETS -> CANDIDATES -> REDUCTION` | EAS-K / #9 | C contracts, frozen objective | deterministic packets/reducer → owners/X | DAG/lease/parent-binding controls | deterministic only |
| `src/enterprise_agent_system/shadow.py` + `evidence/shadow/**` | `PUBLIC_SUBJECT_BOUND -> MUTATIONS -> ADMIT_FOR_REVIEW | BLOCKED` | EAS-E / #11 | immutable candidate | findings/verdict → X | read-only Shadow | evaluator only |
| `src/enterprise_agent_system/convergence.py` + generic X ledgers | `P4_SUBJECTS_BOUND -> OWNER_UNIQUENESS -> LANE_RECONCILIATION -> PLAN_ONLY_CANARY -> DOWNSTREAM_REVIEW` | EAS-X / #12 | exact owner receipts | aggregate closure candidate → profile X/D/Handoff | current A1 run `32259216877`; stronger denominator preserved | P5 routing only |
| `integrations/github/**`, `integrations/google-drive/**` | `REFERENCE -> REVISION/DIGEST -> CURRENT|STALE|REFUSED` | EAS-A / #10 | provider references | advisory projection → D | **NOT_IMPLEMENTED** | zero credit |
| profile `source/**` | `SOURCE_REGISTERED -> DIGEST_BOUND -> SOURCE_PROPOSAL` | INCEPTION-C0 / #2 | local-only PDF digest/pages | source manifest → requirements | local-only/coverage law | source graph candidate |
| profile `requirements/**` | `CLAIM -> REAL_PROBLEM -> OWNER -> REQUIRED_LANE -> CONTROL -> BLOCKER` | INCEPTION-C0 / #2 | source proposal | 15 requirements + 14 contradictions | denominator cannot shrink | source/contract only |
| profile `contracts/**` | `PROFILE_CONTRACT_READY -> STRICT_RECORDS -> OWNER_LANES_BOUND` | INCEPTION-C1 / #3 | requirements + generic C | 11 records → profile K | current C1 run `32155153945`; 20 mutations | deterministic contract |
| profile `orchestration/**` | `PROFILE_REQUEST -> START_DAG + COMPLETION_DAG -> PACKETS -> OWNER_WAVES` | INCEPTION-K / #4 | C1 + generic K | 10 packets / 11 tasks → A1-A6/E | disjoint leases + 25 mutations | deterministic plan |
| A1 external owner | `SAFE_BOUNDARY -> CHECKPOINT -> CRASH/RECOVERY -> ACTIVE|ROLLBACK` | `bettor-arena` #191 | compaction packet | public receipt → E/X | run `32259216877`; LIVE_PHYSICAL open | partial public |
| A2R external owner | `CONTRACT_BOUND -> WORKLOAD/POLICY -> CAPABILITY_RECORD` | `runtime-env` #67 | runtime requirements | exact runtime contract → A2 | runs `32249588945/32249588946` | deterministic |
| A2 external owner | `RUNTIME_BOUND -> SANDBOX -> EXECUTE -> CLEANUP -> RECEIPT` | `agent-shield-monorepo` #153 | A2R pin + steering packet | reversible local receipt → E/X | provider/network open | partial public |
| A3 external owner | `CLAIM_BOUND -> EXACT_READBACK -> PHYSICAL/LEXICAL -> SEMANTIC -> RECEIPT` | `truth-verify-loop` #23 | exact claim/source | public Git evidence → E/X | external independent semantic open | partial public |
| A4 profile owner | `SUBJECT -> LINEAGE -> POLICY -> SYNTHETIC_LEAK_CANARY -> HUMAN_REVIEW` | EAS #16 | Code/Model/Data/Trace | policy/synthetic receipt → E/X | legal/live telemetry open | partial public |
| A5 external owner | `SOURCE -> TERMS -> FIT -> ISOLATED_CANDIDATE -> BENCHMARK -> HUMAN_ADMIT` | `bettor-arena` #192 | exact source/candidate | matched fixture → E/X | external benchmark/Human open | partial public |
| A6 external owner | `EVENT -> INBOX -> EFFECT_RESERVED -> ATTEMPT -> READBACK -> COMMITTED|UNKNOWN|COMPENSATE|HUMAN` | `bettor-arena` #193 | event + WriteIntent | restart/reconciliation receipt → E/X | real effect/compensation open | partial public |
| profile `shadow/**` | `PUBLIC_DENOMINATOR -> 15/14 REPLAY -> LANE_RECONCILE -> ADMIT_FOR_PROFILE_CONVERGENCE | BLOCK` | INCEPTION-E / #19 | seven owner subjects | Shadow snapshot → X | review `4973593318`; stronger lanes open | evaluator only |
| profile `evidence/convergence/**` | `FRESH_X+E -> 7 OWNERS -> 15 RECONCILE -> 14 PRESERVE -> 13 STRONGER -> PLAN_ONLY_CANARY -> P6` | INCEPTION-X / #22 | fresh Generic-X + Profile-E + requirements | closure candidate → D | PR #40 / Shadow `4974017388`; hosted Profile-X Gate `ABSENT` | routing only |
| profile `docs/**` + profile D indexes | `PROFILE_X_PINNED -> ROUTES/STACK/DATAFLOW -> DOCS_GATE -> ROOT_D_HANDOFF` | INCEPTION-D / #23 | Profile-X #40 | Profile-D #44 → Root-D | DV `32282726313`; Shadow `4975046170` | docs only |
| root `README/AGENTS/ARCHITECTURE/CONTEXT`, `docs/**`, `prompts/README`, `handoff/README` | `PROFILE_D_V4_PINNED -> ROOT_ROUTES_RENDERED -> CONSISTENCY_GATE -> EXTERNAL_VERIFY -> SHADOW -> P7_PREP` | EAS-D / #13 | Profile-D #44 exact subject | Root-D v2 receipt → #14 | external exact-target verification + fresh Shadow required | docs only |
| `handoff/local-handoff-queue.json` | `CURRENT_ROOT_D_BOUND -> EXACTLY_ONE_ACTIVE -> EXECUTE -> RECEIPT+CLEANUP -> ADVANCE|BLOCK|HUMAN` | #14 | current Root-D external receipt + unresolved stronger lanes | local/provider receipts → reducer/Human | **BLOCKED_PENDING_CURRENT_ROOT_D_RECEIPT**; execution `NOT_PERFORMED` | queue contract only |

## Current P6 chain

```text
Generic-X #31 + Profile-E #32
          ↓ true multi-parent input
Profile-X v3 #40
          ↓ true child
Profile-D v4 #44
          ↓ true child
Root-D v2 candidate
          ↓ external verifier + read-only Shadow
P7 preparation
```

Verification siblings are evidence only and are never Git parents.

## Edge law

Start readiness never equals completion readiness. Completion requires exact outputs, declared Gates, cleanup/receipt denominator, and canonical-owner readback.

## Documentation law

Every governed directory names Canonical owner, State Machine, inputs, outputs, Gate, blocker, Evidence ceiling, and next owner. Missing runtime/provider/Human evidence remains visible rather than normalized to documentation PASS. Google projections remain `ADVISORY_ONLY`; superseded branches have `authority NONE`.