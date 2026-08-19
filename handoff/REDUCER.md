# P7 queue-v3 Local Receipt Reducer

This document belongs to issue #65. It describes the canonical **readback/admission** step after H3R produces an external local receipt. It does not create that receipt and does not mutate `handoff/local-handoff-queue.json`.

## Exact inputs

```text
queue-v3 #59
  a6dbbc52fba70c9732a1bf664f52a072cd83d608
  tree 7b54d0c56d088bf7edcf7b4c8984366a89ee9e36

H3R #67
  f81c2ecabaaac44ff82832a482524124baec106a
  tree 49170e045200b1cd42d8022ca6fcb81c23314932
  verify 32293402604 PASS
  Shadow 4976016596 = ADMIT_FOR_LOCAL_ACTIVE_EXECUTION

ACTIVE
  LH-P7-01-ROOT-D-V2-LOCAL-READBACK

next item
  LH-P7-02-A2R-CONTEXT-TOKENIZER
```

Old queue-v2/runner-v2 subjects have `authority NONE` and are never admitted as current receipt provenance.

## State machine

```text
REDUCER_SUBJECTS_BOUND
→ RECEIPT_ROUTE_BOUND
→ RECEIPT_ABSENCE_CHECKED
→ RECEIPT_SCHEMA_AND_PORTABLE_SURFACE_READ_BACK
→ EXACT_RUNNER_AND_QUEUE_ITEM_READ_BACK
→ COMMAND_AND_CLEANUP_DENOMINATOR_READ_BACK
→ ROOT_D_AND_RESIDUE_READ_BACK
→ EVIDENCE_LANE_AND_NEXT_TRANSITION_READ_BACK
→ NEXT_EPOCH_CANDIDATE_READY | BLOCKED
```

The reducer does not skip `RECEIPT_ABSENCE_CHECKED`. A missing external receipt is a terminal public-state finding:

```text
BLOCKED_BY_MISSING_REAL_LOCAL_RECEIPT
receipt_state = NOT_EXERCISED
real_local_evidence_credit = 0
```

## PASS admission law

A receipt that says `PASS` is not trusted by itself. Admission additionally requires:

- exact queue ID and ACTIVE item;
- exact H3R `subject_before` and `subject_after` commit/tree;
- `LOCAL_DETERMINISTIC` evidence lane;
- exact Root-D v2 observed commit/tree;
- the full ordered 9 main + 3 cleanup command denominator;
- zero exit codes across the complete PASS denominator;
- cleanup `PASS`;
- no Root-D worktree directory, registration or temporary ref residue;
- clean checkout before and after;
- empty `failures` for PASS;
- exact success transition `CANDIDATE_RECEIPT_READY_FOR_CANONICAL_REDUCER`;
- no private local paths, secret-like values or provider/effect/Human state promotion in the portable receipt.

If those checks pass, the output is only:

```text
NEXT_EPOCH_CANDIDATE_READY
```

It explicitly keeps:

```text
queue_mutation_performed        false
canonical_advancement_performed false
stronger_lane_credit            []
```

A later queue owner may compile the next epoch from the exact admitted receipt digest. The reducer itself does not rewrite the queue.

## Synthetic fixtures

Public GitHub verification may use synthetic positive/negative receipt fixtures to prove reducer semantics. Those runs must use:

```text
source_kind = SYNTHETIC_FIXTURE
real_local_evidence_credit = 0
```

A fixture that is structurally identical to a real receipt still cannot satisfy the local execution lane.

## CLI

Public plan mode:

```text
python3 handoff/reduce_receipt.py --mode plan
```

It prints exact public subjects and the missing-receipt blocker without resolving or printing local receipt paths.

Real local readback, after an admitted H3R execution has produced the external file:

```text
python3 handoff/reduce_receipt.py \
  --mode inspect \
  --source-kind REAL_LOCAL_RECEIPT \
  --receipt <LOCAL_RECEIPT_PATH>
```

The local path is an execution input only and must not be copied into portable Git evidence.

## Evidence ceiling

```text
public reducer implementation/fixtures        may be VERIFIED
real local receipt existence                  NOT_PROVEN_BY_PUBLIC_CI
ACTIVE local execution                        NOT_PERFORMED until external receipt exists
queue mutation/advancement                    NOT_PERFORMED
provider/physical/private/external effect     NOT_EXERCISED
vertical canary                               PLAN_ONLY
business/user outcome                         NOT_VERIFIED
Human/merge/release/rollback                  NOT_PERFORMED
```
