# Local Handoff — P7 queue v3

Status: **READY_FOR_LOCAL_EXECUTION_PREPARATION**

Current queue v3 is a direct child of Root-D v2 and is the only current P7 preparation candidate.

```text
Root-D PR #57
commit 68828ec8de5f3ad5aa133a5c772eefb80c775568
tree   bf338e0cd959a2b97adee79af7459222bd5211b9
verification 32284239386 PASS
Shadow 4975173485 = ADMIT_FOR_P7_PREPARATION

queue id LH-EAS-INCEPTION-P7-V3-2026-08-20
items 11
exactly one `ACTIVE`
ACTIVE LH-P7-01-ROOT-D-V2-LOCAL-READBACK
blocked successors 9
Human terminal 1
queue execution NOT_PERFORMED
vertical canary PLAN_ONLY
```

The ACTIVE item is a local deterministic **readback only** of current public Root-D bytes. It uses Git/Python and a detached worktree, replays Generic-X/Profile-X/Profile-D deterministic controls, writes an external receipt, then removes/prunes the worktree and temporary remote ref. It does not require PDF bytes, provider credentials, network enrollment, or external writes.

## Current authority

- Generic-X: `8b1bfa38c103e1c064b8ef0aafecfc8f2a2642dc` / `9c8fb0e8e25f357fdb695a94c4ab74fc3dcd4631` / Shadow `4973896050`.
- Profile-X v3: `fe2748e09a5222f439f09c5d0d71e486e1ade3e8` / `0425916bea831c125702696544ae2848fdf9bd0e` / Shadow `4974017388`; hosted Gate `ABSENT`.
- Profile-D v4: `a7a034ef1db778fcee586fff8d8ff7848bc9a1ab` / `62796ebb2e48e60ab30809470d3b6c02f44009fc` / hosted verify `32282726313 PASS` / Shadow `4975046170`.
- Root-D v2: `68828ec8de5f3ad5aa133a5c772eefb80c775568` / `bf338e0cd959a2b97adee79af7459222bd5211b9` / hosted verify `32284239386 PASS` / Shadow `4975173485`.

Literal closure stays `15 requirements / 14 contradictions / 13 stronger no-credit lanes / 1 required lane satisfied / 0 closure credit`; full architecture is `BLOCKED_FOR_CLOSURE`; EAS-A is `NOT_IMPLEMENTED`; canary digest is `sha256:7a881bbe4b2b9605d56838f5f1e9a3c76dbf45ebc1b0aa7a973fd1329f88efbb` and its execution receipt is null.

## Superseded denominator

```text
PR #27  SUPERSEDED_STALE_SUBJECT  authority NONE
PR #50  SUPERSEDED_STALE_ROOT_D   authority NONE
```

Neither old queue may execute or receive current evidence credit. Their historical attempts remain visible.

## Queue State Machine

```text
CURRENT_ROOT_D_RECEIPT_BOUND
→ QUEUE_V3_COMPILED
→ EXACTLY_ONE_ACTIVE
→ LOCAL_READBACK
→ EXACT_RECEIPT
→ CLEANUP_AND_RESIDUE_READBACK
→ CANONICAL_REDUCER
→ NEXT_ITEM | BLOCKED | HUMAN_ADMIT_REQUIRED
```

Only the canonical reducer may advance the ACTIVE item after exact receipt/readback and clean cleanup. Command exit alone cannot advance state.

## Successor DAG

```text
P7-01 Root-D local readback
→ P7-02 A2R tokenizer/context
→ P7-03 A1 physical durability
→ P7-04 A2 network/gVisor/provider
→ P7-05 A3 independent semantic/private evidence
→ P7-06 A4 exact terms/live telemetry
→ P7-07 A5 external benchmark/Human admission
→ P7-08 A6 provider effect/readback/compensation
→ P7-09 vertical canary
→ P7-10 final Truth Verify
→ P7-11 Human admission
```

Every stronger successor remains blocked until its predecessor has an admitted exact receipt. Provider enrollment, credentials, private-data egress approval, irreversible effects, semantic conflicts, Human admission, merge, release and rollback remain Human-owned.

## Safety

Commands use structured argv, declared cwd and timeout, environment **names** only, and no secret/credential values. Cleanup includes worktree removal, prune, and deletion of the temporary remote ref. Receipt schema is `handoff/local-handoff-receipt.schema.json`.

## Evidence ceiling

`P7_EXECUTABLE_QUEUE_PREPARATION_ONLY`. Queue preparation does not prove local execution, provider/physical/private evidence, external effects, user outcome, Human admission, merge, release or rollback.

P7 queue execution remains `NOT_PERFORMED`.
