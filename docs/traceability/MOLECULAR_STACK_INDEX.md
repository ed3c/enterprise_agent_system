# Molecular Stack traceability index

This index records immutable delivery relationships. A Stack row is traceability, not automatic closure credit.

## Generic Stack

| Atom | Class | Issue / PR | Exact current subject | State |
|---|---|---|---|---|
| EAS-C | root | #8 / PR #20 | `ac0a7645392f689ae488328a53e7b6f3bb6ad02d` / tree `51c94cb43ed1e4a3a3ac05e42838532c3ec2e598` | deterministic contract candidate |
| EAS-K | child | #9 / PR #24 | `b1362f48b6edc0b4cd6d301da2a5d0e94d970f8c` / tree `19353937e8d642a0bd731e20b3f61ffa3af2b913` | deterministic Tech Lead candidate |
| EAS-A | sibling | #10 / no PR | `subject=null` | **NOT_IMPLEMENTED / credit 0** |
| EAS-E | read-only | #11 / PR #25 | `177ba870c41cc5605532ea79770d54aea124fa0c` / tree `20073aa3b719f30c95a6cbf449f0d6a2144f71c3` | evaluator candidate |
| EAS-X | convergence | #12 / PR #31 | `8b1bfa38c103e1c064b8ef0aafecfc8f2a2642dc` / tree `9c8fb0e8e25f357fdb695a94c4ab74fc3dcd4631` | Shadow `4973896050`; current A1 run `32259216877` |
| EAS-D | docs convergence | #13 / Root-D v2 | direct child of current Profile-D #44 | candidate pending external exact-target verification |

## Agent Thinking Inception Stack

| Atom | Issue / PR | Owner | Exact current subject | Evidence/state |
|---|---|---|---|---|
| C0 | #2 / PR #21 | EAS | `1f0d196c19b7fa4505894ff1fb8b27cd33c5fb9f` / `924967e5fb51dad8ad09e321109063d4f7b2ec70` | 15 requirements / 14 contradictions |
| C1 | #3 / PR #28 | EAS | `c7a474e4f3e501a21a1a10c14fd1982ec710d079` / `a15e98938df11e4659805daf760fbd37fe476b65` | run `32155153945`; 11 contracts |
| K | #4 / PR #29 | EAS | `6e0a916fd06dd8635d77c9a8c4d1b475185ea13e` / `c3851a6953d456d0342a9776eed28561c1af0ca1` | run `32163284481`; 10 packets / 11 tasks |
| A1 | #5 / bettor PR #194 | bettor-arena | `21ac4fdcd6ce4c5acea920dc4e59a53d13ecd328` / `31ea6bec01899a4c9e4f994998ea6041116db49d` | run `32259216877`; stronger physical lane open |
| A2R | #7 / runtime-env PR #68 | runtime-env | `2ff4efe7bee3d12fb3063fed93631f8d323cd64a` / `273c6873e7075d90a7f11275c5d39e746dd075dc` | runs `32249588945/32249588946` |
| A2 | #7 / Shield PR #154 | agent-shield-monorepo | `8ec782b78ec9e13f78f2faf14e6ffa722c1b78f2` / `51adf9791485d597849c026a3828ded0088b3805` | runs `32262032532/32262032583/32262032553`; provider/network open |
| A3 | #15 / Truth Verify PR #30 | truth-verify-loop | `5ea4dd42d2ee5bbd22537f5426cd276f10222980` / `fc6486b9ab6a48752e32a536a847c6e5635f8547` | runs `32260293092/32260291970`; external independent lane open |
| A4 | #16 / EAS PR #30 | EAS | `bf976c7c33e315d1743733a79c15521e645ff6dc` / `c09bef2457ad507433f253c8a5fd211147fae247` | run `32261864341`; legal/live lanes open |
| A5 | #17 / bettor PR #195 | bettor-arena | `81f02f4148273ffe5f5571c8605e1ee0afc59866` / `f9612314e47ced69796db00703dd5d34ab592e36` | run `32260835956`; external benchmark/Human open |
| A6 | #18 / bettor PR #196 | bettor-arena | `c2613432736c65756ed13d871feb2df486c69118` / `53680d47048f88b9402c6320355121b7ec2f7244` | run `32262080676`; real effect/compensation open |
| E | #19 / PR #32 | EAS Shadow | `9f25b94ca891faf0d926b0fc22b67be88925aa81` / `1452d1b9931c70ef70ed3b7dec78cedc51d6db35` | Shadow `4973593318`; admitted for convergence |
| X v3 | #22 / PR #40 | EAS convergence | `fe2748e09a5222f439f09c5d0d71e486e1ade3e8` / `0425916bea831c125702696544ae2848fdf9bd0e` | Shadow `4974017388`; hosted Profile-X Gate `ABSENT`; canary `PLAN_ONLY` |
| D v4 | #23 / PR #44 | EAS docs | `a7a034ef1db778fcee586fff8d8ff7848bc9a1ab` / `62796ebb2e48e60ab30809470d3b6c02f44009fc` | DV `32282726313 PASS`; Shadow `4975046170 = ADMIT_FOR_ROOT_EAS_D` |
| Root-D v2 | #13 | EAS root docs | current branch child of D v4 | external verification + Shadow pending |
| P7 | #14 | EAS Local Handoff | current queue must be rebound after Root-D v2 | execution `NOT_PERFORMED` |

## Current Git relationships

```text
C0 -> C1
C1 + generic K bytes -> Profile-K
Profile-K + generic EAS-E bytes -> Profile-E
Generic EAS-X + Profile-E -> Profile-X v3       (true multi-parent input)
Profile-X v3 -> Profile-D v4                    (true child)
Profile-D v4 -> Root-D v2                       (true child)
Root-D v2 -> future P7 queue candidate          (only after external verify + Shadow)
```

Verification siblings are evidence only, never Git parents.

## Important relationship laws

- Process/evidence order is not Git ancestry.
- A2R owner head stays distinct from A2's consumed runtime pin `cdfe74ac993cb0b4795fa80df237e8bb542409d2` / tree `0b2db695cdd812f81924b82689d96e3557b80158`.
- Generic X is already an ancestor of current Profile-D through Profile-X v3; Root-D v2 does not need a duplicate Generic-X/Profile-D merge base.
- EAS-A remains in the denominator while `NOT_IMPLEMENTED`.
- External Shadow/verification receipts are intentionally not self-written into the exact branch they review.

## Historical/no-authority denominator

```text
Profile-X PR #33                         authority NONE
Profile-X PR #36                         authority NONE
Profile-D PR #37                         authority NONE
Profile-D verifier PR #39                authority NONE
Root-D PR #41 / verifier PR #43          authority NONE for current P6
P7 PR #50 / verifier PR #51              authority NONE for current P7 until rebound
EAS-D blueprint PR #26                   documentation blueprint only
```

Historical Profile-D v4 verification failures remain visible:

```text
32274026438 RED  ADVISORY_ONLY projection token missing
32282142421 RED  authority NONE projection token missing
32282357314 RED  stale A1 run id in current machine flow
32282726313 PASS current Profile-D target
```

## Closure projection

```text
requirements                  15
contradictions                14
stronger no-credit lanes      13
required evidence lanes satisfied 1
requirement closure credit    0
Profile-X hosted Gate         ABSENT
vertical canary               PLAN_ONLY / execution_receipt=null
full architecture             BLOCKED_FOR_CLOSURE
profile release               NOT_ADMITTED
```

A Stack row records traceability and authority boundaries, not release readiness.