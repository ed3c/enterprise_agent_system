# Public main closure review — 2026-08-20

This document records the Tech Lead + Shadow Architect close/merge classification for the public `enterprise_agent_system` stack. It is a traceability projection, not a stronger execution/Human/release receipt.

## Decision rule

A bounded implementation or verification item may close when:

1. its exact current subject is identified;
2. its declared writer lease and required deterministic evidence are satisfied;
3. any required read-only Shadow verdict exists;
4. its bytes/evidence are either merged directly or integrated through the current convergence carrier;
5. every stronger unresolved real-world requirement has another explicit owner, program issue, or Local Handoff item.

A PR may merge only when it is a current canonical product subject or an explicit convergence carrier. Verification-only and superseded/historical PRs do not merge.

## Main integration decision

```text
main before integration     5f14173181e0383ec84c40839939963845279506
EAS-A exact product         #68 @ 250717db1cad584d50890c0d851153fa2cd755e8
EAS-A merge commit          0832cd7e7b5a486fd8924ff9b667bcb6205c1a35
public product carrier      H4RR #107 @ 4a44e9cf9ece133e8117ecc100e419f359d8e1a1
manual convergence commit   ecdb6bb0bbc6e058882e2eeabc49796cde3bebda
convergence tree            55a1de45870e19dbc0b29a2b402d7a08dd5a3a1e
```

`#107` could not be retargeted directly after #68 because GitHub reported a merge conflict. Shadow classified this as `CONVERGENCE_REPAIR_REQUIRED`. The explicit two-parent integration commit uses main-after-#68 as first parent and exact #107 as second parent, then preserves the exact eight admitted EAS-A blobs from main. No unknown semantic conflict was auto-resolved.

## Canonical implementation PR disposition

| PR | Atom | Decision | Reason |
|---:|---|---|---|
| #20 | EAS-C | close after convergence merge | exact contract bytes are ancestors of current public carrier |
| #24 | EAS-K | close after convergence merge | Tech Lead DAG bytes are ancestors of current public carrier |
| #25 | EAS-E | close after convergence merge | Shadow mechanism bytes are ancestors of current public carrier |
| #31 | EAS-X | close after convergence merge | current post-EAS-A convergence is represented by #31 and consumed by Profile-X |
| #68 | EAS-A | merged | independent `ADVISORY_ONLY` process sibling; exact 8-path lease |
| #21 | Profile C0 | close after convergence merge | source identity/contracts integrated; source correctness remains separately open |
| #28 | Profile C1 | close after convergence merge | strict detailed contracts integrated |
| #29 | Profile-K | close after convergence merge | profile DAG/packet mechanism integrated |
| #30 | Profile-A4 | close after convergence merge | bounded deterministic provenance/policy evidence integrated |
| #32 | Profile-E | close after convergence merge | read-only profile Shadow mechanism integrated |
| #80 | Profile-X | close after convergence merge | current profile convergence verified and consumed downstream |
| #84 | Profile-D | close after convergence merge | current docs/traceability candidate verified and consumed by Root-D |
| #94 | Root-D | close after convergence merge | root Agent-readable projection verified and consumed by P7 |
| #99 | Queue-v4 | close after convergence merge | public queue preparation complete; execution is tracked by #14 |
| #103 | H4R | close after convergence merge | public runner implementation complete; real execution tracked by #14 |
| #107 | H4RR | merge carrier / then close as merged | public receipt reducer semantics complete; real receipt/readback tracked by #14 |

Closing these bounded tasks does **not** close program #6 or Local Handoff #14.

## Verification-only PR disposition

These PRs are external evidence and should close unmerged after the current product lineage is integrated:

```text
#72   EAS-A exact verifier
#75   EAS-X exact verifier
#83   Profile-X exact verifier
#90   Profile-D exact verifier
#97   Root-D exact verifier
#101  Queue-v4 exact verifier
#105  H4R exact verifier
#109  H4RR exact verifier
```

Their Actions run IDs and Shadow receipts remain referenced by product issues/PRs after closure.

## Historical / superseded PR disposition

Historical current-credit=0/no-authority subjects may close unmerged once their superseding current subject is present in main. Their immutable RED/PASS history remains valid for the exact subject it tested.

Representative denominator:

```text
old queue                    #27 #50 #59
old Profile-X / verifier     #40 #77 #79
old Profile-D                #44
old Root-D / verifier        #57 #92 #95
old runner                   #55 #67
old reducer                  #71
```

Do not delete Git history or rewrite old PASS/RED receipts.

## Issues that must remain open

### Program #6

Keep open because the real source/PDF closure denominator remains:

```text
requirements                         15
required evidence lanes satisfied     1
requirement closure credit            0
contradictions                        14 preserved
stronger no-credit lanes              13
full architecture                     BLOCKED_FOR_CLOSURE
```

### Local Handoff #14

Keep open because the only ACTIVE item has not executed:

```text
LH-P7-01-ROOT-D-V3-LOCAL-READBACK
ACTIVE execution        NOT_PERFORMED
real local receipt      NOT_OBSERVED
queue advancement       NOT_PERFORMED
```

### Stronger canonical owner issues

Any issue owning physical durability, network/gVisor/provider capability, private/independent evidence, live telemetry, external benchmark, external effect/readback/compensation, business/user outcome, Human admission, release or rollback remains open until its own evidence lane closes.

## Source / PDF real-problem audit

The source-bound profile has mechanisms for source identity, requirements, contradictions, DAG routing, evidence receipts and Local Handoff, but the source itself remains `LOCAL_ONLY` and semantic/source correctness is `NOT_PROVEN` by the public GitHub lane.

Therefore the correct closure statement is:

> Public implementation and deterministic verification are integrated. The article/PDF-derived real-world requirement set is **not yet operationally closed**.

No issue/PR publication state may be cited as proof of source correctness, physical/provider behavior, user outcome, Human admission, release, or rollback.

## Local Handoff execution handoff

```text
queue #99
  75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4
        ↓
runner #103
  7be0a69b0046b66799baee2ddb5e305c90d60ec6
        ↓ real local runtime
receipt
  LH-P7-01-ROOT-D-V3-LOCAL-READBACK.json
        ↓
reducer #107
  4a44e9cf9ece133e8117ecc100e419f359d8e1a1
        ↓
canonical next-epoch authority
```

A public reducer decision always has `real_local_evidence_credit=0`; real local credit must be admitted by the external execution/readback authority.