# CONTEXT — mutable exact-subject handoff

This file is a convenience projection. Immutable evidence remains the named repository/commit/tree and external typed receipt. Update only in EAS-D documentation convergence; never use it as canonical task/effect/Human/release state.

## Current phase

```text
program issue  #6
phase          P6 root documentation convergence
owner issue    #13
state          ROOT_D_V2_CANDIDATE
Git parent     Profile-D #44 @ a7a034ef1db778fcee586fff8d8ff7848bc9a1ab
next gate      external immutable-target Root-D verification + fresh Shadow
P7 execution   NOT_PERFORMED
```

The Root-D final commit/tree, hosted verification run and Shadow review are external receipts and are intentionally not self-written into the branch they review.

## Exact current inputs

```text
Generic EAS-X #31
commit 8b1bfa38c103e1c064b8ef0aafecfc8f2a2642dc
tree   9c8fb0e8e25f357fdb695a94c4ab74fc3dcd4631
Shadow 4973896050

Profile-E #32
commit 9f25b94ca891faf0d926b0fc22b67be88925aa81
tree   1452d1b9931c70ef70ed3b7dec78cedc51d6db35
Shadow 4973593318

Profile-X v3 #40
commit fe2748e09a5222f439f09c5d0d71e486e1ade3e8
tree   0425916bea831c125702696544ae2848fdf9bd0e
Shadow 4974017388
hosted Profile-X Gate ABSENT

Profile-D v4 #44
commit a7a034ef1db778fcee586fff8d8ff7848bc9a1ab
tree   62796ebb2e48e60ab30809470d3b6c02f44009fc
DV run 32282726313 PASS
Shadow 4975046170 = ADMIT_FOR_ROOT_EAS_D
```

Root-D v2 is now a direct child of current Profile-D. Current Profile-X v3 already contains fresh Generic-X + Profile-E true multi-parent ancestry, so Root-D does not create a redundant second Generic-X/Profile-D merge base.

## Literal closure projection

```text
requirements                 15
contradictions               14
stronger no-credit lanes     13
required lanes satisfied      1
requirement closure credit    0
vertical canary               PLAN_ONLY
execution receipt             null
full architecture             BLOCKED_FOR_CLOSURE
EAS-A                         NOT_IMPLEMENTED / subject null / credit 0
profile release               NOT_ADMITTED
Human admission               NOT_PERFORMED
```

Canary digest: `sha256:7a881bbe4b2b9605d56838f5f1e9a3c76dbf45ebc1b0aa7a973fd1329f88efbb`.

Current A1 run is `32259216877`; stale `32259476821` is excluded from current machine authority.

## P6 Profile-D receipt history

```text
32274026438 RED  missing ADVISORY_ONLY projection token
32282142421 RED  missing authority NONE projection token
32282357314 RED  stale A1 numeric id in current machine data-flow
32282726313 PASS current immutable Profile-D target
Shadow 4975046170 ADMIT_FOR_ROOT_EAS_D
```

## Historical subjects with no current authority

- Profile-X #33 and #36: superseded.
- Profile-D #37 and verification #39: children/evidence of obsolete Profile-X.
- Root-D #41 and verification #43: bound to obsolete Generic-X/Profile-D subjects.
- P7 #50/#51: bound to obsolete Root-D #41 and must be rebound after current Root-D v2 verification.
- EAS-D blueprint #26: design input only.

## Open stronger lanes

Physical/multi-host recovery, network/gVisor isolation, provider capability/enrollment, external independent semantic/private evidence, exact external Model/Data/Trace terms, live telemetry, external candidate benchmark, real external effect/readback, compensation, business/user outcome, Human legal/security admission, merge/release/rollback remain unresolved.

## Operating note

No issue is auto-closed and no PR is merged by this documentation phase. Local Handoff execution remains `NOT_PERFORMED`. Secret/private source bytes are not stored here. Google Docs/Sheets remain `ADVISORY_ONLY`.