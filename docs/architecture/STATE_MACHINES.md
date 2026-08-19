# Directory → State Machine → DAG ownership

This document is a root projection. Canonical machine details live in generic `plans/**` and the profile `profiles/agent-thinking-inception/plans/**` indexes.

| Directory / surface | State Machine | Canonical owner / atom | Inputs | Outputs / next owner | Gate / blocker | Evidence ceiling |
|---|---|---|---|---|---|---|
| `contracts/control-plane/**` | `UNBOUND -> STRICT_CONTRACT -> CONSUMER_READY` | EAS-C / #8 | source identity, authority laws | generic records → K/E/X | shape + semantic mutation gates | contract candidate |
| `src/enterprise_agent_system/orchestration.py` | `REQUEST_BOUND -> DAG -> PACKETS -> CANDIDATES -> REDUCTION` | EAS-K / #9 | C contracts, frozen objective | deterministic packets/reducer → owners/X | DAG/lease/parent-binding controls | deterministic only |
| `src/enterprise_agent_system/shadow.py` + `evidence/shadow/**` | `PUBLIC_SUBJECT_BOUND -> MUTATIONS -> ADMIT_FOR_REVIEW | BLOCKED` | EAS-E / #11 | immutable candidate | findings/verdict → X | read-only Shadow | evaluator only |
| `src/enterprise_agent_system/convergence.py` + generic X ledgers | `P4_SUBJECTS_BOUND -> OWNER_UNIQUENESS -> LANE_RECONCILIATION -> PLAN_ONLY_CANARY -> DOWNSTREAM_REVIEW` | EAS-X / #12 | exact owner receipts | aggregate closure candidate → D/Handoff | 7 interfaces + stronger-lane denominator | P5 routing only |
| `integrations/github/**`, `integrations/google-drive/**` | `REFERENCE -> REVISION/DIGEST -> CURRENT|STALE|REFUSED` | EAS-A / #10 | provider references | advisory projection → D | **NOT_IMPLEMENTED** | zero credit |
| profile `source/**` | `SOURCE_REGISTERED -> DIGEST_BOUND -> SOURCE_PROPOSAL` | INCEPTION-C0 / #2 | local-only PDF digest/pages | source manifest → requirements | local-only/coverage law | source graph candidate |
| profile `requirements/**` | `CLAIM -> REAL_PROBLEM -> OWNER -> CONTROL -> BLOCKER` | INCEPTION-C0 / #2 | source proposal | 15 requirements + 14 contradictions | denominator cannot shrink | source/contract only |
| profile `contracts/**` | `PROFILE_CONTRACT_READY -> STRICT_RECORDS -> OWNER_LANES_BOUND` | INCEPTION-C1 / #3 | requirements + generic C | 11 records → profile K | 20 mutations | contract candidate |
| profile `orchestration/**` | `PROFILE_REQUEST -> TASK_DAG -> PACKETS -> OWNER_WAVES` | INCEPTION-K / #4 | C1 + generic K | 10 packets / 11 tasks → A1-A6/E | start/completion + lease + 25 mutations | deterministic plan |
| A1 external owner | `SAFE_BOUNDARY -> CHECKPOINT -> CRASH/RECOVERY -> ACTIVE|ROLLBACK` | `bettor-arena` #191 | compaction packet | public crash/recovery receipt → E/X | live physical still open | partial public |
| A2R external owner | `CONTRACT_BOUND -> WORKLOAD/POLICY -> CAPABILITY_RECORD` | `runtime-env` #67 | runtime requirements | exact runtime contract → A2 | deterministic contract | deterministic |
| A2 external owner | `RUNTIME_BOUND -> SANDBOX -> EXECUTE -> CLEANUP -> RECEIPT` | `agent-shield-monorepo` #153 | A2R pin + steering packet | reversible local receipt → E/X | provider/network still open | partial public |
| A3 external owner | `CLAIM_BOUND -> EXACT_READBACK -> PHYSICAL/LEXICAL -> SEMANTIC -> RECEIPT` | `truth-verify-loop` #23 | exact claim/source | public Git evidence → E/X | external independent semantic open | partial public |
| A4 profile owner | `SUBJECT -> LINEAGE -> POLICY -> SYNTHETIC_LEAK_CANARY -> HUMAN_REVIEW` | EAS #16 | Code/Model/Data/Trace | policy/synthetic receipt → E/X | legal/live telemetry open | partial public |
| A5 external owner | `SOURCE -> TERMS -> FIT -> ISOLATED_CANDIDATE -> BENCHMARK -> HUMAN_ADMIT` | `bettor-arena` #192 | exact source/candidate | matched fixture → E/X | external benchmark/Human open | partial public |
| A6 external owner | `EVENT -> INBOX -> EFFECT_RESERVED -> ATTEMPT -> READBACK -> COMMITTED|UNKNOWN|COMPENSATE|HUMAN` | `bettor-arena` #193 | event + WriteIntent | restart/reconciliation receipt → E/X | real effect/compensation open | partial public |
| profile `shadow/**` | `PROFILE_SUBJECT -> 15/14 REPLAY -> LANE_RECONCILE -> ADMIT_FOR_PROFILE_CONVERGENCE | BLOCKED_FOR_CLOSURE` | INCEPTION-E / #19 | A1-A6 | Shadow denominator → X | stronger lanes block full closure | evaluator only |
| profile `evidence/convergence/**` | `EXACT_RECEIPTS -> 15 RECONCILE -> 14 PRESERVE -> PLAN_ONLY_CANARY -> PROFILE_CLOSURE_CANDIDATE` | INCEPTION-X / #22 | E + generic X + Truth Verify | P5 profile receipt → D | 50 refusals + 28 replays | routing only |
| profile `docs/**`, new profile indexes | `PROFILE_X_PINNED -> ROUTES/STACK/DATAFLOW -> DOCS_GATE -> ROOT_D_HANDOFF` | INCEPTION-D / #23 | Profile-X | profile docs receipt → root D | 12 docs mutations | docs only |
| root `README/AGENTS/ARCHITECTURE/CONTEXT`, `docs/**`, `prompts/README`, `handoff/README` | `GENERIC_X+PROFILE_D_PINNED -> ROOT_ROUTES_RENDERED -> CONSISTENCY_GATE -> P7_READY` | EAS-D / #13 | Generic-X + Profile-D | root Agent-readable route → #14 | docs consistency + Shadow | docs only |
| `handoff/local-handoff-queue.json` | `QUEUE_BOUND -> ONE_ACTIVE -> EXECUTE -> RECEIPT+CLEANUP -> ADVANCE|BLOCK|HUMAN` | #14 | unresolved stronger lanes | local/provider receipts → reducer/Human | ACTIVE item unchanged without exact receipt | queue contract only |

## Edge law

Start readiness never equals completion readiness. A task may begin when start dependencies are satisfied, but the completion edge requires the exact outputs, declared Gates, cleanup/receipt denominator, and canonical-owner readback.

## Documentation law

Every documented directory names owner, State Machine, inputs, outputs, Gate, blocker, evidence ceiling, and next authority. Missing runtime/provider/Human evidence remains visible rather than normalized to docs `PASS`.