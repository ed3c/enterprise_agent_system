# Molecular Stack traceability index

## Generic Stack

| Atom | Issue / PR | Exact subject | State |
|---|---|---|---|
| EAS-C | #8 / #20 | `ac0a7645392f689ae488328a53e7b6f3bb6ad02d` | contract candidate |
| EAS-K | #9 / #24 | deterministic orchestration subject | Tech Lead candidate |
| EAS-A | #10 / #68 | `250717db1cad584d50890c0d851153fa2cd755e8` / `fbf6a75b6e89e906f227110dc5a61e4355b8a891` | verify `32295871632`; Shadow `4976213414`; `ADVISORY_ONLY` |
| EAS-E | #11 / #25 | `177ba870c41cc5605532ea79770d54aea124fa0c` | read-only evaluator |
| EAS-X | #12 / #31 | `b295eabec7b4c9d4e1f65f7fb0238034f454ae7f` / `25bd4c7e934690b3ac15692ba04af4418a46b1f2` | verify `32296886625`; Shadow `4976304922` |
| EAS-D | #13 | Root-D v3 current candidate | docs only |

EAS-A is a process/advisory dependency, not EAS-X/Profile-X Git ancestry.

## Agent Thinking Inception current Stack

| Atom | Current issue / PR | Exact subject / receipt | Evidence/state |
|---|---|---|---|
| C0 | #2 / #21 | source graph | 15 requirements / 14 contradictions |
| C1 | #3 / #28 | strict profile contracts | deterministic |
| K | #4 / #29 | profile DAG/packets | deterministic |
| A1-A6 | canonical owner PRs | public verification receipts | stronger lanes remain open |
| E | #19 / #32 | `9f25b94ca891faf0d926b0fc22b67be88925aa81` | read-only Shadow |
| X v4 | #22 / #80 | `df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0` / `9290a2822ba30309a9d44933ce0ea4d640501a39`; verify `32321499909`; Shadow `4978282030` | P5 current |
| D v5 | #23 / #84 | `f04f9fc78270c8f97ce978e2ccc161ab4d724ca4` / `9740f25f9b1fa8f6533c49642381955b953dd12a`; verify `32326260896`; Shadow `4978669357` | P6 current |
| Root-D v3 | #13 | current branch child of #84 | external verify + Shadow pending |
| P7 | #14 | post-EAS-A recompile required | execution `NOT_PERFORMED` |

## True ancestry

```text
Generic-X #31 + Profile-E #32
              ↓
        Profile-X v4 #80
              ↓
        Profile-D v5 #84
              ↓
          Root-D v3
              ↓
      P7 after exact receipt
```

EAS-A #68 feeds Generic/Profile convergence as `PROCESS_DEPENDENCY_NOT_GIT_PARENT`.

## Historical/no-current-authority denominator

```text
Profile-X v3 #40   authority NONE
Profile-D v4 #44   authority NONE
Root-D v2 #57      authority NONE
P7 #59              authority NONE
H3R #67             authority NONE
H3RR #71            authority NONE
```

Historical verification results remain valid for their immutable subjects but receive zero current execution authority.

## Closure projection

```text
requirements 15
required evidence lanes satisfied 1
requirement closure credit 0
contradictions 14 preserved
stronger no-credit lanes 13
vertical canary PLAN_ONLY / execution receipt null
EAS-A ADVISORY_ONLY
Google connectivity/write NOT_PERFORMED
source correctness NOT_PROVEN
full architecture BLOCKED_FOR_CLOSURE
profile release NOT_ADMITTED
```