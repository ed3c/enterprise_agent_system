# AGENTS.md — enterprise_agent_system operating contract

## Mandatory read order

1. `README.md`
2. `CONTEXT.md`
3. `ARCHITECTURE.md`
4. `docs/INDEX.md`
5. `docs/traceability/MOLECULAR_STACK_INDEX.md`
6. `docs/architecture/STATE_MACHINES.md` and `DATA_FLOW.md`
7. owning issue + matching fresh-session prompt
8. nearest profile/repository `AGENTS.md`

## Runtime classification

```text
CLOUD_DETERMINISTIC
PUBLIC_REVERSIBLE
LOCAL_PHYSICAL
PROVIDER_LIVE
PRIVATE_EVIDENCE
EXTERNAL_EFFECT
HUMAN_ADMIT
RELEASE_ROLLBACK
```

A cheaper lane never proxies a stronger one. `NOT_EXERCISED`, `NOT_PERFORMED`, `UNKNOWN_EFFECT`, `BLOCKED`, and `HUMAN_ADMIT_REQUIRED` earn zero closure credit.

## Current exact P6 inputs

```text
EAS-A #68 250717db1cad584d50890c0d851153fa2cd755e8 / fbf6a75b6e89e906f227110dc5a61e4355b8a891
  verify 32295871632 / Shadow 4976213414 / ADVISORY_ONLY
Generic-X #31 b295eabec7b4c9d4e1f65f7fb0238034f454ae7f / 25bd4c7e934690b3ac15692ba04af4418a46b1f2
Profile-X #80 df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0 / 9290a2822ba30309a9d44933ce0ea4d640501a39
  verify 32321499909 / Shadow 4978282030
Profile-D #84 f04f9fc78270c8f97ce978e2ccc161ab4d724ca4 / 9740f25f9b1fa8f6533c49642381955b953dd12a
  verify 32326260896 / Shadow 4978669357
```

Root-D v3 is the only current root-doc candidate once published from Profile-D #84. P7 #59, H3R #67 and H3RR #71 are historical `authority NONE` until rebuilt.

## One-interface / one-owner law

EAS routes and reconciles. Runtime, durable workflow/effects, provider adapters, independent verification, and Human release remain in their canonical owners. Process dependency is not Git ancestry.

## Writer lease law

Before mutation bind owner issue, branch/base commit+tree, writable/read-only/forbidden paths/resources, cleanup and rollback subject. Root-D #13 may write only:

```text
README.md
AGENTS.md
ARCHITECTURE.md
CONTEXT.md
docs/INDEX.md
docs/architecture/**
docs/prompts/**
docs/traceability/**
prompts/README.md
handoff/README.md
```

Profile machine records, owner implementation, queue JSON, `.github/**`, release state and external repositories are read-only.

## Role boundaries

Tech Lead compiles DAG/leases and routes receipts but cannot invent evidence. Worker writes only its lease. Gate fails closed. Shadow receives the same immutable subject through a separate read-only path and may block/admit downstream review but cannot edit Builder bytes, merge, release or Human-admit. Canonical owners alone advance owned state.

## GitHub / Google projection boundary

EAS-A is implemented only at `ADAPTER_AND_ADVISORY_PROJECTION_SEMANTICS_ONLY`. Google connectivity/write remains `NOT_PERFORMED`; source correctness remains `NOT_PROVEN`; Google Docs/Sheets are `ADVISORY_ONLY` and cannot mutate canonical task/workflow/effect/Human/release state.

## P7 boundary

Until Root-D v3 receives external hosted verification plus fresh Shadow:

```text
P7 recompile   BLOCKED_PENDING_CURRENT_ROOT_D_RECEIPT
P7 execution   NOT_PERFORMED
```

Even afterward, queue preparation is not queue execution. Secret values/private source bytes never enter Git or portable receipts.

## Completion packet

Return exact subject-before/after commit+tree, changed paths/lease, all Gate attempts including RED history, external receipts, Shadow verdict, cleanup/residue, claims-not-proven, blockers and next authority.