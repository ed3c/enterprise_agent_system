# Agent Thinking Inception prompt catalogue — P6 v5

Prompt text is executable instruction, not evidence. Every session must bind exact
current subjects; prior chat memory is not an admissible execution input.

## Current profile prompts

| Phase | Prompt | Role |
|---|---|---|
| P0 | `00-source-auditor.system.md` | source/authority auditor |
| P1 | `01-profile-contract-worker.system.md` | source-specific contract lock |
| P2 | `02-tech-lead-profile-controller.system.md` | Tech Lead DAG/lease compiler |
| P3 | `03-profile-worker-envelope.system.md` | bounded owner Worker envelope |
| P4 | `10-shadow-architect-profile.system.md` | read-only Profile Shadow |
| P5 | `11-profile-convergence.system.md` | Profile-X exact-subject convergence |
| P6 | `12-profile-docs-convergence.system.md` | Profile-D documentation convergence |
| P7 | root `docs/prompts/P7-local-handoff-compiler.system.md` after current Root-D rebind | Local Handoff compilation |

## Current immutable P5/P6 input

```text
Profile-X v4 PR #80
df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0
9290a2822ba30309a9d44933ce0ea4d640501a39
external verification 32321499909 PASS
Shadow 4978282030
```

EAS-A is consumed only as:

```text
250717db1cad584d50890c0d851153fa2cd755e8
fbf6a75b6e89e906f227110dc5a61e4355b8a891
ADVISORY_ONLY
PROCESS_DEPENDENCY_NOT_GIT_PARENT
Google connectivity/write NOT_PERFORMED
source correctness NOT_PROVEN
```

## Fresh-session packet law

Each prompt execution binds:

```text
exact repo / commit / tree / receipt
objective / non-goals / invariants / unknowns
one role and canonical owner
writable / read-only / forbidden paths and resources
start dependencies / completion dependencies
input / output contracts
positive + planted mutation controls
runtime / capability requirements
evidence lane / evidence ceiling
retry / timeout / cleanup / rollback
required receipt / claims_not_proven
stop conditions / next authority
```

## Authority law

Google Docs/Sheets may mirror narratives/dashboards only and remain
`ADVISORY_ONLY`; they cannot silently rewrite an admitted prompt, Task/Workflow,
Effect, Human, merge, release or rollback state.

Old Profile-X #40 / Profile-D #44 / Root-D #57 / P7 #59 / H3R #67 / H3RR #71
are historical/stale and have `authority NONE` for current execution until the
post-EAS-A lineage is rebuilt. Do not select their prompt/queue state as current.

The current canary remains `PLAN_ONLY`, digest
`sha256:869842575cae80c62227699f576728f3331fa25a573a3cc27c052f23f32944c2`,
with `execution_receipt=null`.
