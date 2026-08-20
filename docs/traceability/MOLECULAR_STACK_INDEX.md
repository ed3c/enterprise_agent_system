# Molecular Stack traceability index

This is the Agent-readable `git-town-stacked-pr-worker` index for the public EAS stack. It distinguishes implementation ancestry, process dependencies, verification-only siblings, historical candidates, and the Local Handoff boundary.

## Integration strategy

```text
EAS-A #68
  exact head 250717db1cad584d50890c0d851153fa2cd755e8
  merged to main through 0832cd7e7b5a486fd8924ff9b667bcb6205c1a35

Public convergence carrier
  exact H4RR #107 4a44e9cf9ece133e8117ecc100e419f359d8e1a1
        +
  main-after-EAS-A 0832cd7e7b5a486fd8924ff9b667bcb6205c1a35
        ↓ genuine two-parent convergence
  ecdb6bb0bbc6e058882e2eeabc49796cde3bebda
  tree 55a1de45870e19dbc0b29a2b402d7a08dd5a3a1e
```

The integration tree preserves the complete H4RR public lineage and overlays exactly the eight admitted EAS-A blobs from main. It is an integration carrier, not a new evidence lane.

## Generic Stack

| Atom | Owner issue / product PR | Exact current subject | Evidence / state | Main disposition |
|---|---|---|---|---|
| EAS-C | #8 / #20 | `ac0a7645392f689ae488328a53e7b6f3bb6ad02d` | strict contracts / fail-closed checker | integrated through convergence |
| EAS-K | #9 / #24 | `b1362f48b6edc0b4cd6d301da2a5d0e94d970f8c` | deterministic Tech Lead DAG | integrated through convergence |
| EAS-E | #11 / #25 | `177ba870c41cc5605532ea79770d54aea124fa0c` | hosted Shadow mechanism | integrated through convergence |
| EAS-X | #12 / #31 | `b295eabec7b4c9d4e1f65f7fb0238034f454ae7f` | verify `32296886625`; Shadow `4976304922` | integrated through convergence |
| EAS-A | #10 / #68 | `250717db1cad584d50890c0d851153fa2cd755e8` | verify `32295871632`; Shadow `4976213414`; `ADVISORY_ONLY` | merged direct |
| EAS-D | #13 / #94 | `6981c700f9f2f9128ebeebdf80e627178b2be336` | verify `32342272177`; Shadow `4979950874` | integrated through convergence |

EAS-A is `PROCESS_DEPENDENCY_NOT_GIT_PARENT` for Generic/Profile convergence.

## Agent Thinking Inception Stack

| Atom | Owner / current product PR | Exact current subject | Verification / Shadow | Main disposition |
|---|---|---|---|---|
| C0 | #2 / #21 | `60f994f5f9da55168911d19fb32489775a5f4599` | source identity only; LOCAL_ONLY source | integrated through convergence |
| C1 | #3 / #28 | `e131a9be...` current strict-contract branch | deterministic gates | integrated through convergence |
| Profile-K | #4 / #29 | `6e0a916fd06dd8635d77c9a8c4d1b475185ea13e` | deterministic packet/DAG gates | integrated through convergence |
| A4 profile evidence | owner PR #30 | `bf976c7c33e315d1743733a79c15521e645ff6dc` | public deterministic evidence | integrated through convergence |
| Profile-E | #19 / #32 | `9f25b94ca891faf0d926b0fc22b67be88925aa81` | read-only Shadow | integrated through convergence |
| Profile-X v4 | #22 / #80 | `df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0` | #83 / `32321499909 PASS`; Shadow `4978282030` | integrated through convergence |
| Profile-D v5 | #23 / #84 | `f04f9fc78270c8f97ce978e2ccc161ab4d724ca4` | #90 / `32326260896 PASS`; Shadow `4978669357` | integrated through convergence |
| Root-D v3 | #13 / #94 | `6981c700f9f2f9128ebeebdf80e627178b2be336` | #97 / `32342272177 PASS`; Shadow `4979950874` | integrated through convergence |
| P7 Queue-v4 | #14 / #99 | `75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4` | #101 / `32348407481 PASS`; Shadow `4980564966` | integrated through convergence |
| H4R | #102 / #103 | `7be0a69b0046b66799baee2ddb5e305c90d60ec6` | #105 / `32349394151 PASS`; Shadow `4980654571` | integrated through convergence |
| H4RR | #106 / #107 | `4a44e9cf9ece133e8117ecc100e419f359d8e1a1` | #109 / `32350502938 PASS`; Shadow `4980770691` | convergence carrier |

A1/A2R/A2/A3/A5/A6 remain cross-repository canonical owner evidence and are not duplicated inside EAS.

## True Git ancestry / process relationships

```text
EAS-C #20 → EAS-K #24 → EAS-E #25 → Generic-X #31
                                         │
Profile source/C1/K → Profile-E #32 ─────┤
                                         ▼
                                   Profile-X #80
                                         ▼
                                   Profile-D #84
                                         ▼
                                     Root-D #94
                                         ▼
                                    Queue-v4 #99
                                         ▼
                                      H4R #103
                                         ▼
                                     H4RR #107

EAS-A #68 ── PROCESS_DEPENDENCY_NOT_GIT_PARENT ──► Generic/Profile convergence
```

## Verification-only siblings — evidence, not product ancestry

These should not merge into main. Their exact receipts remain useful after closure:

```text
#72   EAS-A verifier
#75   Generic-X verifier
#83   Profile-X verifier
#90   Profile-D verifier
#97   Root-D verifier
#101  Queue-v4 verifier
#105  H4R verifier
#109  H4RR verifier
```

Historical verifier siblings for superseded subjects likewise remain evidence only.

## Historical / no-current-authority denominator

```text
old queue        #27 / #50 / #59      authority NONE
Profile-X        #40 / #77            authority NONE for current convergence
Profile-D        #44                  authority NONE
Root-D           #57 / #92            authority NONE
old runners      #55 / #67            authority NONE
old reducers     #71                  authority NONE
historical XV/DV #79 / #95            current credit 0
```

Exact historical PASS/RED results remain valid for the immutable subjects they tested; they never regain current execution authority.

## Molecular terminal state vocabulary

```text
INTEGRATED_THROUGH_PUBLIC_CONVERGENCE
MERGED_DIRECT_TO_MAIN
VERIFICATION_EVIDENCE_ONLY
HISTORICAL_NO_CURRENT_AUTHORITY
BLOCKED_BY_LOCAL_RECEIPT
HUMAN_ADMIT_REQUIRED
```

Closing a PR/issue changes publication/task metadata only. It does not rewrite the immutable evidence state.

## Real-problem closure projection

```text
requirements                        15
required evidence lanes satisfied    1
requirement closure credit           0
contradictions                       14 preserved
stronger no-credit lanes             13
vertical canary                      PLAN_ONLY / execution receipt null
EAS-A                               ADVISORY_ONLY
Google connectivity/write           NOT_PERFORMED
source correctness                  NOT_PROVEN
full architecture                   BLOCKED_FOR_CLOSURE
profile release                     NOT_ADMITTED
```

Therefore completed molecular implementation issues can close after main integration only when their residual stronger lanes remain explicitly owned by program #6, Local Handoff #14, or canonical cross-repository owner issues.