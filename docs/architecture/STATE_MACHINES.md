# Root State Machines

## Program state machine

```text
P0 SOURCE_AND_AUTHORITY_BOUND
  ↓
P1 CONTRACTS_VERIFIED
  ↓
P2 TECH_LEAD_DAG_VERIFIED
  ↓
P3 OWNER_PUBLIC_IMPLEMENTATION
  ↓
P4 PUBLIC_REVERSIBLE_EVIDENCE
  ↓
P5 EXACT_SUBJECT_CONVERGENCE
  ↓
P6 PROFILE_DOCS_VERIFIED
  ↓
P6 ROOT_DOCS_CANDIDATE
  ↓ external exact-target verifier
P6 ROOT_DOCS_VERIFIED
  ↓ fresh read-only Shadow
P7 QUEUE_RECOMPILE_READY
  ↓
P7 CURRENT_QUEUE_PREPARED
  ↓ real local/provider execution only
P7 RECEIPT_REDUCED
  ↓
HUMAN_ADMIT_REQUIRED | NEXT_EPOCH | COMPLETE | BLOCKED
```

Current state inside this Root-D branch is `P6_ROOT_DOCS_CANDIDATE`. The exact Root-D final commit/tree and final verifier/Shadow must remain external receipts to avoid self-reference.

## Profile closure state machine

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

Current aggregate ceiling remains below `LIVE_OR_PHYSICAL_EVIDENCE_VERIFIED`; no documentation state may skip that ladder.

## Root-D v3 state machine

```text
PROFILE_D_EXACT_SUBJECT_BOUND
→ ROOT_WRITER_LEASE_BOUND
→ ROOT_PROJECTIONS_AUTHORED
→ ROOT_PROMPTS_REBOUND
→ ROOT_STACK_RECONCILED
→ ROOT_CANDIDATE_BYTES_COMPLETE
→ EXTERNAL_IMMUTABLE_TARGET_VERIFICATION_REQUIRED
→ SHADOW_REVIEW_REQUIRED
→ ADMIT_FOR_P7_RECOMPILE | BLOCKED
```

Current exact parent:

```text
Profile-D #84
f04f9fc78270c8f97ce978e2ccc161ab4d724ca4
9740f25f9b1fa8f6533c49642381955b953dd12a
verify 32326260896 PASS
Shadow 4978669357
```

## Local Handoff state machine

```text
CURRENT_ROOT_D_RECEIPT
→ QUEUE_SUBJECT_BOUND
→ EXACT_ACTIVE_ITEM_SELECTED
→ LOCAL_CAPABILITIES_REBOUND
→ COMMAND_CONTRACTS_MATERIALIZED
→ ACTIVE_ITEM_EXECUTED
→ RECEIPT_AND_CLEANUP_VERIFIED
→ CANONICAL_REDUCER_RECONCILED
→ NEXT_EPOCH_EMITTED | HUMAN_ADMIT_REQUIRED | COMPLETE | BLOCKED
```

The current state is before `CURRENT_ROOT_D_RECEIPT`. Historical queue #59 and H3R/H3RR #67/#71 have `authority NONE`; local execution is `NOT_PERFORMED`.

## Tech Lead state machine

```text
REQUEST_BOUND
→ SYSTEM_CONTRACT_EXTRACTED
→ CAPABILITY_PLAN_COMPILED
→ CONTEXT_ADMITTED
→ TASK_DAG_COMPILED
→ TASK_SEMANTICS_ASSERTED
→ WORKERS_ADMITTED
→ LEASES_BOUND
→ ATTEMPTS_EXECUTED
→ RESULTS_VERIFIED
→ CANDIDATES_COMPARED
→ CONVERGENCE_APPLIED
→ GLOBAL_OBJECTIVE_ASSERTED
→ DELIVERY_HANDOFF
→ HUMAN_ADMIT_REQUIRED
```

Tech Lead cannot promote a result above its evidence lane.

## Shadow Architect state machine

```text
IMMUTABLE_SUBJECT_READ
→ APPLICABILITY_CHECK
→ OWNER_AND_ANCESTRY_CHECK
→ DENOMINATOR_CHECK
→ EVIDENCE_CEILING_CHECK
→ FAILURE_HISTORY_CHECK
→ CLEANUP_ROLLBACK_CHECK
→ ADMIT_FOR_NEXT_REVIEW | BLOCKED
```

Shadow is read-only and never a second state writer.

## Current fail-closed denominators

```text
requirements                    15
required lanes satisfied         1
requirement closure credit       0
contradictions                  14
stronger no-credit lanes        13
EAS-A                            ADVISORY_ONLY
Google connectivity/write       NOT_PERFORMED
source correctness              NOT_PROVEN
vertical canary                 PLAN_ONLY
execution receipt               null
P7 execution                    NOT_PERFORMED
```

## Historical failure states retained

Profile-D verifier history:

```text
32325143724 RED
32325653265 RED
32325967828 RED
32326260896 PASS
```

Historical/current-authority distinction:

```text
#40/#44/#57/#59/#67/#71     authority NONE
#77/#79                     historical concurrent subjects; current authority NONE
#80/#83                     current Profile-X subject/evidence
#84/#90                     current Profile-D subject/evidence
```

No failure, stale branch, or superseded candidate is deleted from the denominator.