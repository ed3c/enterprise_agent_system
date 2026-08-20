# Molecular Stack Index — current root projection

This file projects the current observed Stack. It is not a second machine-state owner. Immutable authority remains exact commits/trees plus typed receipts.

## Relationship vocabulary

```text
TRUE_CHILD                consumes named unmerged bytes from the Git parent
SIBLING                   independent implementation with no unmerged-byte ancestry
PROCESS_DEPENDENCY        required method/advisory/process input, not Git ancestry
EXTERNAL_EVIDENCE         verification-only or Shadow receipt, not Git ancestry
CONVERGENCE               aggregate exact-subject reconciliation
REVIEW_ONLY               read-only evaluator; never a merge parent
HISTORICAL                preserved denominator with no current authority
```

## Required atoms

```text
C / K / A / E / X / D
```

## Current profile/root Stack

| Atom | Subject | Relationship / authority | Current evidence |
|---|---|---|---|
| C0 | profile issue #2 / PR #21 | ancestor / source graph | 15 requirements / 14 contradictions |
| C1 | profile issue #3 / PR #28 | ancestor / contracts | deterministic contract controls |
| K | profile issue #4 / PR #29 | ancestor / DAG packets | deterministic packet/lease controls |
| A1 | `bettor-arena#194 @ 21ac4fdcd6ce4c5acea920dc4e59a53d13ecd328` | sibling owner | `32259216877 PASS` |
| A2R | `runtime-env#68 @ 2ff4efe7bee3d12fb3063fed93631f8d323cd64a` | sibling owner | `32249588945/32249588946 PASS` |
| A2 | `agent-shield-monorepo#154` current owner lane | sibling owner | public/reversible receipts only |
| A3 | `truth-verify-loop#30 @ 5ea4dd42d2ee5bbd22537f5426cd276f10222980` | sibling owner | `32260293092/32260291970 PASS` |
| A4 | EAS #30 current policy/synthetic subject | sibling policy evidence | synthetic telemetry/provenance only |
| A5 | `bettor-arena#195 @ 81f02f4148273ffe5f5571c8605e1ee0afc59866` | sibling owner | `32260835956 PASS` |
| A6 | `bettor-arena#196` current ingress/effect subject | sibling owner | reversible deterministic evidence only |
| E | Profile-E #32 `9f25b94ca891faf0d926b0fc22b67be88925aa81` | REVIEW_ONLY | Shadow `4973593318` |
| A (advisory) | EAS-A #68 `250717db1cad584d50890c0d851153fa2cd755e8` | PROCESS_DEPENDENCY / ADVISORY_ONLY | verify `32295871632`, Shadow `4976213414` |
| X generic | EAS-X #31 `b295eabec7b4c9d4e1f65f7fb0238034f454ae7f` | CONVERGENCE | verify `32296886625`, Shadow `4976304922` |
| X profile | Profile-X #80 `df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0` | TRUE multi-parent child of Generic-X + Profile-E | verify `32321499909`, Shadow `4978282030` |
| D profile | Profile-D #84 `f04f9fc78270c8f97ce978e2ccc161ab4d724ca4` | TRUE_CHILD of Profile-X #80 | verify `32326260896`, Shadow `4978669357` |
| D root | Root-D v3 candidate | TRUE_CHILD of Profile-D #84 | external verifier + Shadow REQUIRED |
| P7 | future queue recompile | blocked successor | `NOT_PERFORMED` |

EAS-A #68 is not a Git parent of Profile-X/Profile-D/Root-D and cannot write canonical workflow/effect/Human/release state.

## Current ancestry

```text
Generic-X #31 ─┐
               ├─> Profile-X #80 ─> Profile-D #84 ─> Root-D v3 candidate
Profile-E #32 ─┘

EAS-A #68 --PROCESS_DEPENDENCY--> Generic/Profile convergence
```

Verification siblings #83/#90 and future Root-D verifier are `EXTERNAL_EVIDENCE`, not ancestry.

## Current closure projection

```text
requirements                    15
required lanes satisfied         1
requirement closure credit       0
contradictions                  14
stronger no-credit lanes        13
vertical canary                 PLAN_ONLY
execution receipt               null
full architecture               BLOCKED_FOR_CLOSURE
profile release                 NOT_ADMITTED
P7 execution                    NOT_PERFORMED
```

## Historical / superseded denominator

| Subject | Disposition |
|---|---|
| Profile-X #40 | `STALE_PENDING_EAS_A_REBIND / authority NONE` |
| Profile-D #44 | `STALE_PENDING_EAS_A_REBIND / authority NONE` |
| Root-D #57 | `STALE_PENDING_EAS_A_REBIND / authority NONE` |
| P7 #59 | `STALE_PENDING_EAS_A_REBIND / authority NONE` |
| H3R #67 | `STALE_PENDING_EAS_A_REBIND / authority NONE` |
| H3RR #71 | `STALE_PENDING_EAS_A_REBIND / authority NONE` |
| concurrent Profile-X #77 | `SUPERSEDED_BY_CANONICAL_CONCURRENT_WRITER_#80 / current authority NONE` |
| concurrent verifier #79 | `HISTORICAL_TARGET_ONLY / current credit 0` |

No force rewrite removes these subjects.

## Failure denominator

```text
Profile-D verifier 32325143724 RED
Profile-D verifier 32325653265 RED
Profile-D verifier 32325967828 RED
Profile-D verifier 32326260896 PASS
```

## Root-D v3 atom

```text
issue       #91 / root owner #13
class       final documentation/receipt convergence
parent      Profile-D #84 @ f04f9fc78270c8f97ce978e2ccc161ab4d724ca4
owns        root README/AGENTS/ARCHITECTURE/CONTEXT, docs architecture/prompts/traceability, prompts README, handoff README
lane        CLOUD_DETERMINISTIC
oracle      exact path lease + inherited profile controls + root projection/prompt consistency + portable/patch hygiene
next        external immutable-target verification → fresh Shadow → P7 queue recompile
ceiling     DOCUMENTATION_AND_TRACEABILITY_CONSISTENCY_ONLY
```

The Root-D final commit/tree and final external verifier/Shadow are intentionally not self-embedded in this branch projection.