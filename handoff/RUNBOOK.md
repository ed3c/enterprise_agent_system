# P7 queue-v3 Local Handoff runner runbook

This runbook belongs to issue #61. It is an execution contract, not an execution receipt and not queue advancement authority.

## Current immutable parent

```text
queue PR       #59
queue commit   a6dbbc52fba70c9732a1bf664f52a072cd83d608
queue tree     7b54d0c56d088bf7edcf7b4c8984366a89ee9e36
queue verify   32286101504 PASS
queue Shadow   4975366131
ACTIVE          LH-P7-01-ROOT-D-V2-LOCAL-READBACK
queue execution NOT_PERFORMED
```

Historical queue-v2 PR #50 and runner-v2 PR #55 have `authority NONE` for current execution. Their PASS/Shadow history remains traceability only.

## Plan mode

Default mode executes no queue command and resolves no local path values:

```text
python3 handoff/run_active.py --mode plan
```

The output contains only public queue metadata, IDs, environment **names**, command/cleanup IDs, receipt route and explicit non-execution state.

## Execute admission

Execution is allowed only on an admitted local runtime:

```text
CODEX_CLI_LOCAL
or
CLAUDE_CODE_LOCAL
```

The following environment names are bound locally; their values never enter Git or the portable plan:

```text
EAS_CHECKOUT
EAS_WORKTREES
EAS_RECEIPT_DIR
```

All three roots must already exist, be absolute, pairwise distinct and non-nested. The receipt/worktree roots must not live inside the checkout.

Execution also requires the **external final Shadow-admitted H3R commit/tree**. Those values are intentionally not self-written into the runner branch:

```text
python3 handoff/run_active.py \
  --mode execute \
  --runtime-kind CODEX_CLI_LOCAL \
  --admitted-runner-commit <FINAL_H3R_SHADOW_COMMIT> \
  --admitted-runner-tree <FINAL_H3R_SHADOW_TREE>
```

Use the equivalent `CLAUDE_CODE_LOCAL` runtime kind when appropriate.

Public GitHub CI must never invoke this execute command against the real ACTIVE queue.

## Preflight

Before the first queue command the runner requires:

```text
runner is a true child of queue-v3 #59
queue/schema/verify_handoff bytes equal the queue-v3 parent
runner HEAD/tree equals the external Shadow-admitted H3R subject
EAS_CHECKOUT dirty state = CLEAN
${EAS_WORKTREES}/root-d-v2 directory = ABSENT
root-d-v2 Git worktree registration = ABSENT
refs/remotes/origin/p7-root-d-v2 = ABSENT
required receipt path = ABSENT
```

Pre-existing residue is a blocker. A new attempt must not silently clean another attempt's resource. An existing receipt is also a blocker so failed/retried attempts are not overwritten.

## Command law

The ACTIVE item currently contains nine main commands. Every command is executed as a structured argv array with `shell=False`; issue/source/user text is never interpolated into a shell string.

The child process receives only a bounded environment plus the three required environment names. `GIT_TERMINAL_PROMPT=0` prevents unattended credential prompting.

Portable records keep:

```text
phase + command ID
unresolved cwd/argv spec
exit code
stdout SHA-256 digest
stderr SHA-256 digest
```

Raw stdout/stderr and resolved local filesystem paths are not serialized.

## Root-D observation

A successful main sequence must leave the detached worktree temporarily at exactly:

```text
commit 68828ec8de5f3ad5aa133a5c772eefb80c775568
tree   bf338e0cd959a2b97adee79af7459222bd5211b9
```

The main sequence also replays current Generic-X, Profile-X, Profile-X mutations, Profile-D, Profile-D mutations and Root-D projection controls from queue-v3. Those are local deterministic readbacks only; they do not grant provider/private/physical/Human evidence.

## Finally cleanup

All three cleanup commands are attempted even after a main-command failure:

```text
REMOVE_ROOT_D_WORKTREE
PRUNE_WORKTREES
DELETE_TEMP_ROOT_D_REF
```

Final residue must show:

```text
${EAS_WORKTREES}/root-d-v2 directory       absent
root-d-v2 worktree registration            absent
refs/remotes/origin/p7-root-d-v2           absent
EAS_CHECKOUT dirty state                    unchanged
```

Any cleanup command failure or residue mismatch makes the candidate receipt `FAIL`.

## Receipt

The one current receipt route is:

```text
${EAS_RECEIPT_DIR}/LH-P7-01-ROOT-D-V2-LOCAL-READBACK.json
```

It must validate against the immutable `handoff/local-handoff-receipt.schema.json` (`local-handoff-receipt/v2`) before write. The runner writes by temporary file + flush/fsync + atomic replace and refuses to overwrite an existing receipt.

A PASS receipt requires exact Root-D observation, all recorded command exit codes zero, cleanup PASS and unchanged runner subject. A FAIL receipt remains evidence of the failed attempt and must not be normalized into PASS.

## Canonical reducer boundary

Even a local PASS is only a candidate:

```text
H3R local runner
→ external v2 receipt
→ exact subject/lane/cleanup readback
→ canonical reducer #65
→ next queue epoch candidate or BLOCKED
```

Runner, CI, Shadow, Issue state or command exit alone cannot advance ACTIVE state.

## Stop conditions

Stop rather than improvise on:

- queue-v3 parent/head/tree drift;
- old queue-v2/runner-v2 subject presented as current authority;
- missing external H3R Shadow subject;
- unadmitted runtime kind;
- missing/relative/overlapping execution roots;
- path traversal/root escape;
- dirty checkout;
- pre-existing worktree directory/registration/temp ref;
- existing canonical receipt path;
- interactive credential requirement;
- secret/private value entering a portable artifact;
- cleanup/residue uncertainty;
- any attempt to widen provider/private/effect/Human/merge/release/rollback authority.

## Evidence ceiling

```text
queue-v3 runner contract / plan path          public verification candidate
hermetic process/failure/cleanup behavior     public verification candidate
real ACTIVE local execution                    NOT_PERFORMED
canonical reducer advancement                  NOT_PERFORMED
provider / physical / private / external      NOT_EXERCISED
vertical canary                                PLAN_ONLY
business/user outcome                          NOT_VERIFIED
Human / merge / release / rollback             NOT_PERFORMED
```
