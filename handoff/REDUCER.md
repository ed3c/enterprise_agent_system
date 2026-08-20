# H4RR Local Receipt Reducer v4

Status: **PUBLIC RECEIPT-SEMANTICS REDUCER CANDIDATE**. This file does not prove a real local receipt exists and does not authorize queue advancement.

## Exact current lineage

```text
Queue-v4 #99
  75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4
  tree eef641a94dec755267ebe8086b68ecbe98c5b68a
  verify 32348407481 PASS
  Shadow 4980566877
        ↓ true child
H4R #103
  7be0a69b0046b66799baee2ddb5e305c90d60ec6
  tree e8a5643b7379acca281387727c203aa9c9559acb
  verify 32349394151 PASS
  Shadow 4980654571 = ADMIT_FOR_PUBLIC_RECEIPT_REDUCER_REBIND_AFTER_EAS_A
        ↓ true child
H4RR current candidate
```

The reducer consumes queue-v4, receipt schema, and H4R subject as read-only inputs.

## Implementation structure

```text
handoff/reduce_receipt_core.py
  exact byte-identical historical H3RR #71 core
  blob 4c5581eabb265346865963c74c573ffc057381b8
  reuse authority CODE_REUSE_ONLY
  canonical advancement authority NONE

handoff/reduce_receipt.py
  current queue-v4 / H4R / Root-D-v3 / EAS-A binding wrapper

handoff/local-receipt-reducer-contract.json
  current authority, denial and evidence-ceiling contract

tests/test_receipt_reducer.py
  inherited receipt semantic/failure denominator tests

tests/test_receipt_reducer_v4.py
  current-epoch subject, EAS-A, stale-authority and zero-credit tests
```

Code reuse never restores old H3RR #71 authority.

## State Machine

```text
H4R_SUBJECT_BOUND
→ REDUCER_CONTRACT_VALIDATED
→ QUEUE_V4_REVALIDATED
→ RECEIPT_LOOKUP
    ├─ ABSENT → BLOCKED_BY_MISSING_REAL_LOCAL_RECEIPT
    └─ PRESENT
       → RECEIPT_SCHEMA_VALIDATED
       → EXACT_QUEUE_ITEM_RUNNER_VALIDATED
       → LOCAL_DETERMINISTIC_LANE_VALIDATED
       → 9_MAIN_PLUS_3_CLEANUP_DENOMINATOR_VALIDATED
       → ROOT_D_V3_OBSERVATION_VALIDATED
       → CLEAN_RESIDUE_AND_DIRTY_STATE_VALIDATED
       → PORTABLE_SECRET_FREE_SURFACE_VALIDATED
       → RESULT_REDUCED
           ├─ NON_PASS → BLOCKED_BY_LOCAL_RECEIPT_RESULT
           └─ PASS → NEXT_EPOCH_CANDIDATE_READY
```

`NEXT_EPOCH_CANDIDATE_READY` is not canonical advancement.

## Anti-laundering laws

```text
missing receipt                         => BLOCKED
synthetic fixture real-local credit     = 0
REAL_LOCAL_RECEIPT label credit         = 0
real-local credit                       requires external execution/readback authority
queue_mutation_performed                = false
canonical_advancement_performed         = false
stronger_lane_credit                    = []
```

Receipt `result=PASS` is never trusted by itself. PASS is admitted semantically only after exact current runner subject, Root-D-v3 observation, complete command/cleanup denominator, zero exit status, no hidden failures, clean residue, clean dirty-state readback and exact success transition all pass.

## Public verification boundary

Allowed:

```text
python3 handoff/reduce_receipt.py --mode plan
python3 handoff/reduce_receipt.py --mode inspect   # missing receipt must BLOCK
synthetic receipt fixtures
python3 tests/test_receipt_reducer.py
python3 tests/test_receipt_reducer_v4.py
```

Forbidden in GitHub-hosted verification:

```text
H4R --mode execute
creation of the canonical real local receipt
write/mutation of handoff/local-handoff-queue.json
real-local evidence credit grant
provider/private/physical/external-effect/Human actions
merge/release/rollback
```

## Current evidence ceiling

```text
queue execution          NOT_PERFORMED
ACTIVE execution         NOT_PERFORMED
real local receipt       NOT_OBSERVED
canonical advancement    NOT_PERFORMED
EAS-A                     ADVISORY_ONLY
Google connectivity/write NOT_PERFORMED
source correctness       NOT_PROVEN
vertical canary          PLAN_ONLY / receipt=null
full architecture        BLOCKED_FOR_CLOSURE
```

Evidence ceiling: `PUBLIC_QUEUE_V4_RECEIPT_REDUCER_SEMANTICS_ONLY`.

After exact-target verification and fresh read-only Shadow, the public GitHub queue/runner/reducer lineage may be declared complete at its public evidence ceiling. The next stronger edge is real local ACTIVE execution and external receipt generation, not another synthetic GitHub PASS.
