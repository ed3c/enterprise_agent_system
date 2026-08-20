# H4R Local Handoff Runner v4

Status: **PUBLIC RUNNER IMPLEMENTATION CANDIDATE**. This file does not authorize execution.

## Exact queue parent

```text
P7 queue #99
commit 75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4
tree   eef641a94dec755267ebe8086b68ecbe98c5b68a
verify 32348407481 PASS
Shadow 4980566877 = ADMIT_FOR_NEW_RUNNER_REBIND
```

H4R is a true Git child of that queue subject. Queue/schema/verifier bytes are read-only.

## Implementation structure

```text
handoff/run_active_core.py
  exact reused H3R execution-core blob
  source PR #67 / authority NONE for execution

handoff/run_active.py
  H4R binding + queue-v4/Root-D-v3 validation

handoff/local-handoff-runner-contract.json
  runner authority and evidence ceiling
```

Reuse is code reuse only; old H3R #67 cannot become current execution authority.

## Default State Machine

```text
QUEUE_V4_BOUND
→ RUNNER_CONTRACT_VALIDATED
→ PLAN
→ EXTERNAL_EXACT_RUNNER_ADMISSION_REQUIRED
→ RUNTIME_AND_ENV_PREFLIGHT
→ CLEAN_RESIDUE_REQUIRED
→ MAIN_COMMANDS
→ FINALLY_CLEANUP
→ EXACT_RECEIPT_VALIDATED
→ ATOMIC_RECEIPT_WRITE
→ CANONICAL_REDUCER_READBACK
```

Hosted CI stops at `PLAN` plus hermetic fixtures. It must never invoke `--mode execute`.

## Safety invariants

- default mode is `plan`;
- execute requires `CODEX_CLI_LOCAL|CLAUDE_CODE_LOCAL` plus exact externally admitted runner commit/tree;
- queue v4 has exactly one ACTIVE item and H4R cannot change it;
- structured argv, `shell=False`, bounded child environment, `GIT_TERMINAL_PROMPT=0`;
- only environment names are portable; resolved local paths and secret values are not serialized;
- checkout/worktree/receipt roots are absolute and pairwise disjoint;
- parent traversal/root escape is refused;
- dirty checkout, pre-existing `root-d-v3` worktree/registration/temp ref, or existing receipt blocks before commands;
- main failure still attempts all three cleanup commands in `finally`;
- PASS requires exact Root-D v3 observation and clean terminal residue;
- receipt v2 is validated before fsync + atomic replace and is never overwritten;
- runner never edits or advances `handoff/local-handoff-queue.json`;
- EAS-A remains `ADVISORY_ONLY`; Google connectivity/write remains `NOT_PERFORMED`; source correctness remains `NOT_PROVEN`.

## Public verification

Allowed:

```text
python3 handoff/run_active.py --mode plan
python3 tests/test_handoff_runner.py
hermetic subprocess/failure/cleanup fixtures
```

Forbidden in GitHub-hosted verification:

```text
python3 handoff/run_active.py --mode execute ...
real ACTIVE execution
real receipt creation
canonical queue advancement
provider/private/physical/external-effect/Human actions
```

## Evidence ceiling

`PUBLIC_QUEUE_V4_RUNNER_IMPLEMENTATION_ONLY`.

A green public runner Gate does not prove the ACTIVE queue item ran. The next public authority after exact-target verification + fresh Shadow is the receipt-reducer rebind; actual Local Handoff execution remains separate.
