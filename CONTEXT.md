# Context — exact current handoff snapshot

This file is a mutable navigation snapshot. Immutable authority is always the referenced repository + commit + tree + typed external receipt.

## Current chain

```text
EAS-A #68
  250717db1cad584d50890c0d851153fa2cd755e8
  tree fbf6a75b6e89e906f227110dc5a61e4355b8a891
  verify 32295871632 PASS
  Shadow 4976213414
  ADVISORY_ONLY / PROCESS_DEPENDENCY_NOT_GIT_PARENT

Generic-X #31
  b295eabec7b4c9d4e1f65f7fb0238034f454ae7f
  tree 25bd4c7e934690b3ac15692ba04af4418a46b1f2
  verify 32296886625 PASS
  Shadow 4976304922

Profile-E #32
  9f25b94ca891faf0d926b0fc22b67be88925aa81
  tree 1452d1b9931c70ef70ed3b7dec78cedc51d6db35
  Shadow 4973593318

Profile-X #80
  df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0
  tree 9290a2822ba30309a9d44933ce0ea4d640501a39
  external verify #83 / 32321499909 PASS
  Shadow 4978282030

Profile-D #84
  f04f9fc78270c8f97ce978e2ccc161ab4d724ca4
  tree 9740f25f9b1fa8f6533c49642381955b953dd12a
  external verify #90 / 32326260896 PASS
  Shadow 4978669357

Root-D v3
  branch candidate is a true child of Profile-D #84
  final exact commit/tree intentionally supplied by external PR receipt
  external hosted verification REQUIRED
  fresh Shadow REQUIRED
```

## Current literal closure projection

```text
requirements                    15
required lanes satisfied         1
requirement closure credit       0
contradictions                  14 preserved
stronger no-credit lanes        13
EAS-A                            ADVISORY_ONLY
Google connectivity/write       NOT_PERFORMED
source correctness              NOT_PROVEN
vertical canary                 PLAN_ONLY
execution receipt               null
full architecture               BLOCKED_FOR_CLOSURE
profile release                 NOT_ADMITTED
P7 queue recompilation          REQUIRED_AFTER_ROOT_D_ADMISSION
P7 execution                    NOT_PERFORMED
Human / merge / release         NOT_PERFORMED
```

## Historical no-current-authority subjects

```text
Profile-X #40
Profile-D #44
Root-D #57
P7 #59
H3R #67
H3RR #71
concurrent Profile-X #77
concurrent verifier #79
```

These remain exact historical evidence. They are not deleted or force-rewritten, but must not be consumed as current downstream/execution authority.

## Profile-D fault history

```text
32325143724 RED  stale denominator omitted Profile-X #40
32325653265 RED  stale-parent mutation was a no-op
32325967828 RED  canary-promotion mutation was a no-op
32326260896 PASS final hardened exact target
```

## Current Root-D work packet

Owner: issue #91 / root EAS-D #13.

Writable lease:

```text
README.md
AGENTS.md
ARCHITECTURE.md
CONTEXT.md
docs/INDEX.md
docs/architecture/**
docs/prompts/**
docs/traceability/**
prompts/README.md
handoff/README.md
```

Read-only: profile machine records, owner implementations, `handoff/local-handoff-queue.json`, runner/reducer bytes, `.github/**`, runtime/effect/Human/release state.

Stop on subject drift, lease overlap, evidence-lane promotion, EAS-A authority widening, Google/live promotion, canary execution, P7 execution, private/credential surface, or Human/release promotion.

## Next authority

After Root-D v3 authored bytes are published, create a verification-only sibling that checks out the immutable Root-D target, validates the exact root writer lease, replays current Profile-X/Profile-D semantics, checks all eight fresh-session prompts and root State Machine/data-flow/Stack projections, and runs patch/portable-surface hygiene. A fresh read-only Shadow must then admit that exact head before P7 may be recompiled.

Until that external receipt exists, old P7 #59/#67/#71 remain `authority NONE` and local execution remains `NOT_PERFORMED`.