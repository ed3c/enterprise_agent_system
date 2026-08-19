# P7 Local Handoff runner runbook

This runbook belongs to issue #52. It explains how an admitted local runtime may execute the single ACTIVE queue item **after** the public runner implementation is exact-target verified and Shadow-admitted.

The runbook is not an execution receipt and does not advance the queue.

## Immutable parent

```text
queue PR       #50
queue commit   00b9ae644352485e4779102b1c3c2d18f6a7155c
queue tree     4effe7ce338753ee61972890f676700ad33c3e04
queue XV       32282597889 PASS
queue Shadow   4975029921
ACTIVE          LH-P7-01-FINAL-P6-LOCAL-READBACK
queue execution NOT_PERFORMED
```

The runner is a true child of that exact queue subject. If the queue, receipt schema or queue verifier bytes differ from the parent, the runner fails closed.

## Modes

### Plan mode

Plan mode is the default and executes **no queue commands**:

```text
python3 handoff/run_active.py --mode plan
```

It prints only public queue metadata: queue parent, ACTIVE item, command IDs, cleanup IDs, required runtime kinds, required environment names and receipt contract. It does not resolve or print local path values.

### Execute mode

Execution is allowed only in an admitted local runtime:

```text
CODEX_CLI_LOCAL
or
CLAUDE_CODE_LOCAL
```

The operator binds environment **names** locally. Do not commit actual filesystem paths or credential values:

```text
EAS_CHECKOUT
EAS_WORKTREES
EAS_RECEIPT_DIR
```

These three roots must be absolute, pairwise disjoint and non-nested. In particular, the receipt directory and worktree root must not live inside `EAS_CHECKOUT`.

Execution additionally consumes the immutable runner commit/tree from the final external #54 Shadow receipt. Pass those exact values at runtime; they are intentionally not self-written into the branch they review:

```text
python3 handoff/run_active.py \
  --mode execute \
  --runtime-kind CODEX_CLI_LOCAL \
  --admitted-runner-commit <FINAL_SHADOW_ADMITTED_RUNNER_COMMIT> \
  --admitted-runner-tree <FINAL_SHADOW_ADMITTED_RUNNER_TREE>
```

or use `CLAUDE_CODE_LOCAL` with the same exact-subject arguments.

Execution mode is not authorized by CI. Public GitHub verification must use `--mode plan` only.

## Environment and path law

- environment roots must be absolute local paths;
- `EAS_CHECKOUT`, `EAS_WORKTREES`, and `EAS_RECEIPT_DIR` must be pairwise disjoint/non-nested;
- queue paths must be relative to their declared root;
- absolute queue-relative paths and `..` traversal are refused;
- only names present in the queue environment allowlist can be resolved;
- secret/credential values are never serialized to Git, plan output or portable receipts;
- subprocesses receive only a bounded host environment plus the environment names needed by the ACTIVE item;
- `GIT_TERMINAL_PROMPT=0` is forced to prevent an unattended command from opening a credential prompt.

## Preflight residue law

Before the first queue command, the runner requires:

```text
EAS_CHECKOUT dirty state                         CLEAN
${EAS_WORKTREES}/root-d-final directory          absent
root-d-final Git worktree registration           absent
refs/remotes/origin/p7-root-d                    absent
```

Pre-existing residue is a blocker, not something this run is allowed to clean up. This prevents a new attempt from deleting a worktree or ref owned by an earlier/other attempt.

## Command execution law

Every queue command is executed as an argv array with `shell=False`. Source, issue or user text is never interpolated into a shell command.

For each main command the receipt retains:

```text
command ID and unresolved command spec
exit code
stdout SHA-256 digest
stderr SHA-256 digest
```

Raw stdout/stderr payloads and resolved local path values are not written to the portable receipt.

A non-zero exit, timeout, OS-level launch failure or exact-subject mismatch changes the candidate result to `FAIL`; it cannot advance the queue.

## Cleanup and residue

Cleanup runs from `finally`, regardless of main command success:

```text
REMOVE_ROOT_D_WORKTREE
PRUNE_WORKTREES
DELETE_TEMP_ROOT_D_REF
```

The final residue gate requires:

```text
${EAS_WORKTREES}/root-d-final directory          absent
root-d-final Git worktree registration           absent
refs/remotes/origin/p7-root-d                    absent
EAS_CHECKOUT dirty state                         equal to pre-execution state
```

A cleanup command failure or residue mismatch forces `cleanup_result=FAIL` and the item result to `FAIL`.

## Receipt

The declared receipt path is:

```text
${EAS_RECEIPT_DIR}/LH-P7-01-FINAL-P6-LOCAL-READBACK.json
```

It must validate against:

```text
handoff/local-handoff-receipt.schema.json
```

The runner validates the final receipt shape/enums/subjects/digests against that immutable schema **before** writing it. It then writes by temporary file + flush/fsync + atomic replace.

The receipt contains exact before/after subjects, observed Root-D subject, command outcomes, digest-only outputs, evidence lane, dirty state, residue inventory, cleanup state, failures/retries, claims-not-proven and next transition. Resolved local path values are not serialized.

The runner does **not** edit `handoff/local-handoff-queue.json`.

## Canonical reducer handoff

A local receipt, even `PASS`, is only a candidate:

```text
local runner
-> v2 receipt
-> exact subject + cleanup readback
-> canonical reducer/owner
-> next queue epoch or BLOCKED
```

Command exit code, receipt existence, GitHub Issue state, CI PASS or Shadow agreement alone cannot advance ACTIVE state.

## Stop conditions

Do not execute when any of these are true:

- runner commit/tree differs from the final external Shadow-admitted subject;
- queue parent/receipt schema/queue verifier bytes drifted;
- required runtime kind is not admitted;
- an environment root is missing, non-absolute, overlapping/nested or escapes confinement;
- `EAS_CHECKOUT` is dirty before execution;
- Root-D worktree directory/registration or temporary fetch ref already exists;
- a command would require interactive credential enrollment;
- private data or a secret value would enter a portable artifact;
- external/provider/Human authority would be widened;
- cleanup or residue cannot be verified.

## Evidence ceiling

A public runner implementation and CI can prove only:

```text
runner contract and plan path              VERIFIED where declared
hermetic process / failure / validation     VERIFIED where declared
preflight / cleanup / residue logic         VERIFIED where declared
real ACTIVE local execution                 NOT_PERFORMED
canonical queue advancement                 NOT_PERFORMED
provider / physical / private               NOT_EXERCISED
vertical canary                             PLAN_ONLY
Human / merge / release / rollback          NOT_PERFORMED
```

Only an admitted local execution can create the first real `LOCAL_DETERMINISTIC` receipt for the ACTIVE item.
