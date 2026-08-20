# Architecture

`enterprise_agent_system` is the management/routing/traceability/closure control plane. It does not duplicate canonical runtime, workflow/effect, provider, verification or Human authority.

## Stable planes

```text
Source/Contract     source registry, requirements, contradictions, strict contracts
Control             Tech Lead DAG, fresh-session packets, leases, candidate reducer
Execution           external canonical owners
Verification        deterministic Gates + Truth Verify + read-only Shadow
Convergence         exact owner/evidence graph and evidence ceilings
Documentation       Agent-readable projections only
Local/Human         Local Handoff receipts + Human irreversible decisions
```

## Core invariants

1. One interface/state has one canonical owner.
2. Source proposal, mechanism, deterministic receipt, live/physical receipt, user outcome, Human admit and release are distinct states.
3. Start readiness differs from completion readiness.
4. Process dependencies are not automatically Git parents.
5. Immutable identity is repository + commit + tree plus typed receipt when needed.
6. Writer leases are exclusive.
7. Shadow is read-only and separately attributable.
8. Failed/retried/skipped/blocked/unknown attempts remain in the denominator.
9. Cleanup/residue/rollback is part of correctness.
10. Docs/projections cannot advance execution/Human state.

## Current Git topology

```text
Generic-X #31 b295eabec7b4c9d4e1f65f7fb0238034f454ae7f
                 \
                  +→ Profile-X v4 #80 df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0
                 /                         |
Profile-E #32 9f25b94ca891faf0d926b0fc22b67be88925aa81
                                           v
                                  Profile-D v5 #84
                                  f04f9fc78270c8f97ce978e2ccc161ab4d724ca4
                                           |
                                           v
                                     Root-D v3
```

EAS-A #68 is a verified `ADVISORY_ONLY` process dependency of convergence, not a third Profile-X parent. Profile-D v5 is a true child of Profile-X v4; Root-D v3 is a true child of Profile-D v5. Verification siblings are evidence only and never Git parents.

## Exact evidence ceiling

```text
EAS-A verify / Shadow          32295871632 / 4976213414
Profile-X verify / Shadow      32321499909 / 4978282030
Profile-D verify / Shadow      32326260896 / 4978669357
requirements                   15
contradictions                 14
stronger no-credit lanes       13
required lanes satisfied        1
requirement closure credit      0
vertical canary                PLAN_ONLY / receipt null
full architecture              BLOCKED_FOR_CLOSURE
profile release                NOT_ADMITTED
Google connectivity/write      NOT_PERFORMED
source correctness             NOT_PROVEN
```

## Closure ladder

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

A CI PASS, Google revision, provider 2xx, model agreement, or issue/PR state cannot jump this ladder.

## Current stale denominator

Profile-X #40, Profile-D #44, Root-D #57, P7 #59, H3R #67 and H3RR #71 remain historical/no-current-authority after the EAS-A rebind. No history is deleted or force-rewritten.