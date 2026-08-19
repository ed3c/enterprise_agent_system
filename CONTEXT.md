# CONTEXT — mutable exact-subject handoff

This file is a convenience projection. Immutable evidence remains the named repository/commit/tree and external receipt. Update this file only in EAS-D documentation convergence; never use it as canonical task/effect/Human state.

## Current phase

```text
program issue  #6
phase          P6 root documentation convergence
owner issue    #13
state          IN_PROGRESS
next           exact-target docs verification -> Shadow -> P6 phase receipt
```

## Exact inputs

```text
Generic X
PR #31
commit 3f8af3d75b28ca1904fe07b8ea9ee0d291f5989c
tree   e1be41234ff336297ce591b564291c9a0cd819ed
Shadow 4973461122

Profile X
PR #33
commit a27aa552f1c258e09f515b4a5d117ba37f4d6615
tree   71eaa3f4acafd0b004ccdff16e4aa14bc2599649
run    32268112684 PASS
Shadow 4973663047

Profile D
PR #37
commit 690154a5f7154d551bef6942fe5d1f34091c2197
tree   1a2e02d4c92b882f51f8c8d28f70771648a6a528
run    32270454491 PASS
Shadow 4973885537

Root D convergence base
aa10bc13f2cfd4d33f0ffdf67f3e4923cb352c2f
parents:
  Generic X 3f8af3d75b28ca1904fe07b8ea9ee0d291f5989c
  Profile D 690154a5f7154d551bef6942fe5d1f34091c2197
```

## Literal closure projection

```text
requirements                 15/15 exact owner subjects
required lanes satisfied      1/15
requirement closure credit     0
contradictions               14/14 preserved
contradictions resolved        0
profile Shadow                BLOCKED_FOR_CLOSURE
vertical canary               PLAN_ONLY
vertical execution receipt    null
EAS-A                         NOT_IMPLEMENTED / subject null / credit 0
profile release               NOT_ADMITTED
```

Canary digest: `sha256:2146c02c23bbf87b6797900141c491a53f6936714b0b620a23016a2b20eaab79`.

## Historical receipts that must stay visible

- Profile-X inherited K workflow `32267670154 RED`: ancestry/consumed bytes passed; P2 K writer lease correctly rejected P5 child paths. Classification: `K_WRITER_GATE_NOT_APPLICABLE_TO_P5_CHILD`.
- Profile-D DV `32270129840 RED`: all semantic controls passed; patch hygiene found two README trailing spaces. Fixed by `690154a5...`; rebound DV `32270454491 PASS`.
- Historical docs PR #26: documentation blueprint only; not final P6 evidence.

## Open stronger lanes

Physical/multi-host recovery, network/gVisor isolation, provider capability/enrollment, external independent semantic/private evidence, exact external Model/Data/Trace terms, live telemetry, external candidate benchmark, real external effect/readback, compensation, business/user outcome, Human legal/security admission, merge/release/rollback remain unresolved.

## Operating note

No issue is auto-closed and no PR is merged by this documentation phase. Local Handoff ACTIVE state is unchanged. Secret/private source bytes are not stored here.