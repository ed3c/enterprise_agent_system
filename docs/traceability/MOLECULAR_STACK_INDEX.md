# Molecular Stack traceability index

## Generic Stack

| Atom | Class | Issue / PR | Exact subject | Relationship / state |
|---|---|---|---|---|
| EAS-C | root | #8 / PR #20 | `ac0a7645392f689ae488328a53e7b6f3bb6ad02d` / tree `51c94cb43ed1e4a3a3ac05e42838532c3ec2e598` | deterministic contract candidate |
| EAS-K | child | #9 / PR #24 | `b1362f48b6edc0b4cd6d301da2a5d0e94d970f8c` / tree `19353937e8d642a0bd731e20b3f61ffa3af2b913` | Tech Lead deterministic candidate |
| EAS-A | sibling | #10 / no PR | `subject=null` | **NOT_IMPLEMENTED / credit 0** |
| EAS-E | review-only | #11 / PR #25 | `177ba870c41cc5605532ea79770d54aea124fa0c` / tree `20073aa3b719f30c95a6cbf449f0d6a2144f71c3` | read-only Shadow candidate |
| EAS-X | convergence | #12 / PR #31 | `3f8af3d75b28ca1904fe07b8ea9ee0d291f5989c` / tree `e1be41234ff336297ce591b564291c9a0cd819ed` | Shadow `4973461122`; downstream review admitted |
| EAS-D | convergence | #13 | current root D branch | Generic-X + Profile-D real multi-parent convergence; docs only |

## Agent Thinking Inception Stack

| Atom | Issue / PR | Canonical owner | Exact subject | Evidence/state |
|---|---|---|---|---|
| C0 | #2 / PR #21 | EAS | `1f0d196c19b7fa4505894ff1fb8b27cd33c5fb9f` / `924967e5fb51dad8ad09e321109063d4f7b2ec70` | 15 requirements / 14 contradictions source graph |
| C1 | #3 / PR #28 | EAS | current head `c7a474e4f3e501a21a1a10c14fd1982ec710d079` / `a15e98938df11e4659805daf760fbd37fe476b65`; payload `1977c015...` | 11 contracts / 20 mutations |
| K | #4 / PR #29 | EAS | `6e0a916fd06dd8635d77c9a8c4d1b475185ea13e` / `c3851a6953d456d0342a9776eed28561c1af0ca1` | 11 tasks / 10 packets / 12 capabilities / 25 mutations |
| A1 | #5 / bettor PR #194 | bettor-arena | `21ac4fdcd6ce4c5acea920dc4e59a53d13ecd328` / `31ea6bec01899a4c9e4f994998ea6041116db49d` | public crash/recovery; LIVE_PHYSICAL open |
| A2R | #7 / runtime-env PR #68 | runtime-env | `2ff4efe7bee3d12fb3063fed93631f8d323cd64a` / `273c6873e7075d90a7f11275c5d39e746dd075dc` | deterministic runtime contract |
| A2 | #7 / Shield PR #154 | agent-shield-monorepo | `8ec782b78ec9e13f78f2faf14e6ffa722c1b78f2` / `51adf9791485d597849c026a3828ded0088b3805` | reversible local process; provider/network open |
| A3 | #15 / Truth Verify PR #30 | truth-verify-loop | `5ea4dd42d2ee5bbd22537f5426cd276f10222980` / `fc6486b9ab6a48752e32a536a847c6e5635f8547` | public Git-object evidence; external independent semantic open |
| A4 | #16 / EAS PR #30 | enterprise_agent_system | `bf976c7c33e315d1743733a79c15521e645ff6dc` / `c09bef2457ad507433f253c8a5fd211147fae247` | synthetic provenance/telemetry evidence; legal/live open |
| A5 | #17 / bettor PR #195 | bettor-arena | `81f02f4148273ffe5f5571c8605e1ee0afc59866` / `f9612314e47ced69796db00703dd5d34ab592e36` | matched fixture; external benchmark/Human open |
| A6 | #18 / bettor PR #196 | bettor-arena | `c2613432736c65756ed13d871feb2df486c69118` / `53680d47048f88b9402c6320355121b7ec2f7244` | UNKNOWN_EFFECT restart; real effect/compensation open |
| E | #19 / PR #32 | EAS Shadow | `9f25b94ca891faf0d926b0fc22b67be88925aa81` / `1452d1b9931c70ef70ed3b7dec78cedc51d6db35` | public denominator admitted; full closure blocked |
| X | #22 / PR #33 | EAS convergence | `a27aa552f1c258e09f515b4a5d117ba37f4d6615` / `71eaa3f4acafd0b004ccdff16e4aa14bc2599649` | XV `32268112684 PASS`; Shadow `4973663047` |
| D | #23 / PR #37 | EAS docs | `690154a5f7154d551bef6942fe5d1f34091c2197` / `1a2e02d4c92b882f51f8c8d28f70771648a6a528` | DV `32270454491 PASS`; Shadow `4973885537` |

## Important relationship laws

- Generic X is a true child of EAS-E.
- Profile X is a true child of Profile-K. Generic X is a process/evidence dependency of Profile-X, not its Git parent.
- Profile-D is a true child of Profile-X.
- Root EAS-D uses a real multi-parent convergence base containing both Generic-X and Profile-D bytes.
- EAS-E/Profile-E are review-only atoms; process order alone never makes them merge parents.
- EAS-A remains visible while absent.
- A2R current owner head is distinct from A2's consumed contract pin `cdfe74ac993cb0b4795fa80df237e8bb542409d2` / tree `0b2db695cdd812f81924b82689d96e3557b80158`.

## Historical evidence that must not be rewritten

```text
Profile-X inherited K run 32267670154 RED
  ancestry/consumed bytes PASS
  P2 K writer lease rejected P5 child paths
  classification K_WRITER_GATE_NOT_APPLICABLE_TO_P5_CHILD

Profile-D DV run 32270129840 RED
  semantic controls PASS
  README trailing whitespace found by git diff --check
  fixed by 690154a5...
  rebound run 32270454491 PASS
```

## Closure projection

```text
requirements 15/15 exact owner subjects
required evidence lanes satisfied 1/15
requirement closure credit 0
contradictions 14/14 preserved
profile Shadow BLOCKED_FOR_CLOSURE
vertical canary PLAN_ONLY / execution receipt null
profile release NOT_ADMITTED
```

A Stack row records traceability, not automatic closure.