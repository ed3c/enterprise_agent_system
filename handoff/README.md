# Local Handoff — current root narrative

This directory contains the Local Handoff contract and historical queue/runner/reducer artifacts. **A queue is continuation authority, not execution evidence.**

## Current authority state

```text
Profile-X current              #80 / df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0
Profile-D current              #84 / f04f9fc78270c8f97ce978e2ccc161ab4d724ca4
Root-D v3                      candidate bytes only; final external verifier + Shadow required
P7 current queue recompile     BLOCKED_PENDING_CURRENT_ROOT_D_RECEIPT
P7 local execution             NOT_PERFORMED
```

Historical subjects:

```text
Root-D #57   authority NONE
queue #59    authority NONE
H3R #67      authority NONE
H3RR #71     authority NONE
```

Do not execute their ACTIVE item, runner, or reducer as current authority.

## Why P7 is suspended

EAS-A #68 became an admitted `ADVISORY_ONLY` process dependency, which required Generic-X/Profile-X/Profile-D/Root-D descendants to be rebound. Profile-X #80 and Profile-D #84 are now current; Root-D v3 still needs its own immutable-target hosted verification and fresh read-only Shadow before any P7 queue can be recompiled.

## Required next P7 input

The future queue compiler must consume:

```text
current Root-D repository + exact commit + tree
Root-D external verification run = PASS
Root-D Shadow verdict = ADMIT_FOR_P7_RECOMPILE
requirements=15
contradictions=14
stronger_no_credit_lanes=13
required_lanes_satisfied=1
closure_credit=0
EAS-A=ADVISORY_ONLY
vertical_canary=PLAN_ONLY
P7_execution=NOT_PERFORMED
```

The Root-D exact final subject is intentionally external to Root-D branch prose to avoid self-reference.

## Queue laws

- exactly one item may be `ACTIVE` on a current admitted queue;
- blocked successors cannot execute early;
- every item binds exact subjects, argv/cwd/timeouts, env-name allowlist, required evidence lane, receipt schema/path, cleanup/residue, rollback/compensation and next authority;
- secret values and private/local-only data never enter Git or portable receipts;
- GitHub CI may verify queue shape/fixtures but does not create real local/provider evidence;
- advancement requires exact receipt readback + clean residue + canonical reducer;
- `UNKNOWN_EFFECT`, dirty cleanup, subject drift, missing capability or Human conflict blocks advancement;
- merge/release/rollback remain Human/trusted-policy operations.

## Historical failure preservation

Profile-D upstream verification history is part of the current denominator:

```text
32325143724 RED
32325653265 RED
32325967828 RED
32326260896 PASS
```

P7 must not erase that history when recompiling current subjects.

## Evidence ceiling

Until a new queue/runner/reducer chain is built from the admitted Root-D v3 subject:

```text
queue validation              NOT_CURRENT_YET
ACTIVE execution              NOT_PERFORMED
provider/private/physical     NOT_EXERCISED
external effects              NOT_PERFORMED
vertical canary               PLAN_ONLY
business/user outcome         NOT_VERIFIED
Human admission               NOT_PERFORMED
merge/release/rollback        NOT_PERFORMED
```

Next authority after Root-D admission is P7 issue #14, starting with **queue recompilation**, not execution of old artifacts.