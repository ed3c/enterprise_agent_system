# Root fresh-session prompt catalogue

Each phase prompt under `docs/prompts/` is a complete bounded packet for a new ChatGPT/Codex/Claude session. **Prior chat memory is not an execution input.**

## Current immutable inputs

```text
EAS-A #68
250717db1cad584d50890c0d851153fa2cd755e8
verify 32295871632 / Shadow 4976213414
ADVISORY_ONLY / PROCESS_DEPENDENCY_NOT_GIT_PARENT

Generic-X #31
b295eabec7b4c9d4e1f65f7fb0238034f454ae7f
verify 32296886625 / Shadow 4976304922

Profile-X #80
df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0
verify 32321499909 / Shadow 4978282030

Profile-D #84
f04f9fc78270c8f97ce978e2ccc161ab4d724ca4
verify 32326260896 / Shadow 4978669357
```

Root-D v3 is authored from Profile-D #84. Its final exact subject and final verifier/Shadow are external receipts and are not self-embedded in the prompt catalogue.

## Catalogue

| Phase | Prompt | Role | Current route |
|---|---|---|---|
| P0 | `docs/prompts/P0-source-authority-auditor.system.md` | Source & Authority Auditor | source/15/14 denominator |
| P1 | `docs/prompts/P1-contract-lock-worker.system.md` | Contract Lock Worker | strict deterministic contracts |
| P2 | `docs/prompts/P2-tech-lead-controller.system.md` | Tech Lead Controller | start/completion DAG, leases, packets |
| P3 | `docs/prompts/P3-owner-wave-worker.system.md` | bounded owner Worker | A1/A2R/A2/A3/A4/A5/A6 |
| P4 | `docs/prompts/P4-shadow-architect.system.md` | independent read-only Shadow | evidence ceiling / contradiction / cleanup review |
| P5 | `docs/prompts/P5-convergence-owner.system.md` | exact-subject convergence owner | Generic-X/Profile-E/EAS-A → Profile-X |
| P6 | `docs/prompts/P6-docs-stack-convergence.system.md` | Root-D docs/Stack owner | Profile-D #84 → Root-D v3 candidate |
| P7 | `docs/prompts/P7-local-handoff-compiler.system.md` | Local Handoff compiler | only after admitted Root-D v3 receipt |

## Packet requirements

Every packet binds:

```text
exact inputs
objective and non-goals
role / canonical owner
writable/read-only/forbidden paths and resources
start and completion dependencies
input/output contracts
positive and mutation controls
runtime/capability requirements
evidence lane and ceiling
retry/timeout/cleanup/retention/rollback
required receipt
stop conditions
claims not proven
next authority
```

## Authority law

- prompts are instructions, not execution evidence;
- Google Docs/Sheets copies are `ADVISORY_ONLY`;
- mutable issue/PR/branch URLs are navigation, not immutable subject identity;
- verification-only siblings and Shadow reviews are evidence, not Git ancestry;
- historical #40/#44/#57/#59/#67/#71 and concurrent #77/#79 have no current downstream authority;
- P7 remains `NOT_PERFORMED` until Root-D v3 admission, queue recompilation, and a separate local execution authority.

## Current closure ceiling

```text
requirements=15
contradictions=14
stronger_no_credit_lanes=13
required_lanes_satisfied=1
closure_credit=0
vertical_canary=PLAN_ONLY
execution_receipt=null
full_architecture=BLOCKED_FOR_CLOSURE
profile_release=NOT_ADMITTED
P7_execution=NOT_PERFORMED
```

Any packet that contradicts this current denominator must fail closed and return to Tech Lead/Shadow for rebind.