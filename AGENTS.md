# AGENTS.md — enterprise_agent_system operating contract

This file is mandatory instruction for Agents working in this repository. It describes the integrated public stack and the evidence ceilings that remain after main integration.

## Mandatory read order

1. `README.md`
2. `CONTEXT.md`
3. `ARCHITECTURE.md`
4. `docs/INDEX.md`
5. `docs/traceability/MOLECULAR_STACK_INDEX.md`
6. `docs/traceability/PUBLIC_MAIN_CLOSURE.md` when present
7. `docs/architecture/STATE_MACHINES.md` and `docs/architecture/DATA_FLOW.md`
8. `handoff/README.md` for any P7/local work
9. owning issue + matching fresh-session prompt
10. nearest profile/repository `AGENTS.md`

Do not rely on previous chat memory when an exact Git/Issue/receipt subject is available.

## Current public facts

```text
main                   85ad1210ee27d105773ae20aaaac7a1a17dfe446
main tree              96c666c2c1e803573944b923838d72c36d47609a
closeout               #110 MERGED / #111 32364024569 PASS / Shadow 4982176517
open current PRs       0
open canonical issues  #1 #5 #6 #7 #14 #15 #16 #17 #18
EAS-A #68              merged to main at ADVISORY_ONLY ceiling
public convergence     ecdb6bb0bbc6e058882e2eeabc49796cde3bebda
queue-v4 #99           75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4
H4R #103               7be0a69b0046b66799baee2ddb5e305c90d60ec6
H4RR #107              4a44e9cf9ece133e8117ecc100e419f359d8e1a1
ACTIVE local item      LH-P7-01-ROOT-D-V3-LOCAL-READBACK
ACTIVE execution       NOT_PERFORMED
real local receipt     NOT_OBSERVED
closure credit         0
```

The public mechanisms are integrated and bounded delivery/verification metadata has been cleaned up. Program #1/#6, stronger-lane owners #5/#7/#15/#16/#17/#18, and Local Handoff #14 remain open because the source/PDF real-problem denominator is not closed.

### Freshness precedence

When older issue or PR prose disagrees with current exact Git state:

```text
exact current commit/tree + typed external receipt
> newest current owner issue receipt
> current README/AGENTS/CONTEXT projection
> historical issue/PR prose
```

A closed historical/superseded issue or PR remains useful denominator evidence but carries no current execution or convergence authority. Do not reopen or resurrect it merely because it once had a green Gate.

## Evidence lane classification

```text
CLOUD_DETERMINISTIC
PUBLIC_REVERSIBLE
LOCAL_PHYSICAL
PROVIDER_LIVE
PRIVATE_EVIDENCE
EXTERNAL_EFFECT
USER_OUTCOME
HUMAN_ADMIT
RELEASE_ROLLBACK
```

A cheaper lane never proxies a stronger one. `NOT_EXERCISED`, `NOT_PERFORMED`, `NOT_OBSERVED`, `UNKNOWN_EFFECT`, `BLOCKED`, and `HUMAN_ADMIT_REQUIRED` earn zero closure credit.

## One-interface / one-owner law

EAS routes and reconciles. Runtime, durable workflow/effects, provider adapters, independent verification, source anchoring, Human authority and release remain in their canonical owners. A process dependency is not Git ancestry. A verification-only sibling is never product ancestry.

## Tech Lead authority

Tech Lead may:

- compile problem/capability/task DAGs;
- bind exact repository/commit/tree subjects;
- grant writer/resource leases;
- dispatch Workers;
- retain failure/retry denominators;
- converge verified candidates;
- classify completed bounded issues/PRs for close/merge;
- compile Local Handoff packets when cloud/public capability is insufficient.

Tech Lead may not invent evidence, reinterpret a stronger lane as satisfied, grant Human/release authority, or use a merge as proof of operational closure.

## Shadow Architect authority

Shadow is independent and read-only. It checks:

- subject freshness and ancestry;
- writer lease violations;
- source/contract/runtime contradictions;
- evidence-lane substitution;
- denominator loss;
- stale or duplicate writer races;
- cleanup/residue/rollback gaps;
- documentation projections that exceed machine truth;
- missing owners/issues for unresolved real problems.

Shadow may block/admit downstream review. Shadow does not edit Builder bytes, execute ACTIVE, grant real-local credit, mutate canonical task/effect state, Human-admit, merge, release or roll back.

## Writer lease law

Before mutation bind:

```text
owner issue
base commit + tree
writable paths/resources
read-only paths/resources
forbidden paths/resources
required Gates
cleanup / residue / rollback subject
next authority
```

Do not broaden a writer lease merely to make a Gate green. If a controlled immutable code reuse path is added, record its exact blob/source subject and set reuse authority to `CODE_REUSE_ONLY`.

## Main integration law

Main integration follows these rules:

1. Only current canonical implementation subjects may enter main.
2. Verification-only siblings do not merge; close them after their exact receipts are externally retained.
3. Superseded/historical candidates do not merge; close them while retaining immutable evidence.
4. When concurrent admitted branches conflict, create an explicit convergence commit/tree; do not semantic-auto-resolve unknown conflicts.
5. Use merge commits when exact ancestor traceability matters.
6. A merged implementation issue may close only if every stronger residual has another explicit owner/Local Handoff item.
7. Program #1/#6 and #14 stay open until real closure, not merely publication closure.
8. With `open current product PRs = 0`, do not manufacture a new implementation PR unless a current open owner issue identifies a real uncovered mechanism or a verified freshness defect.

## Current real-problem denominator

```text
requirements                         15
required evidence lanes satisfied     1
requirement closure credit            0
contradictions                        14 preserved
stronger no-credit lanes              13
source correctness                    NOT_PROVEN
Google connectivity/write             NOT_PERFORMED
vertical canary                       PLAN_ONLY / receipt=null
business/user outcome                 NOT_VERIFIED
Human admission                       NOT_PERFORMED
release/rollback                      NOT_PERFORMED
```

Never describe the bound source/PDF problem as closed while this denominator remains.

## GitHub / Google projection boundary

EAS-A is implemented at `ADAPTER_AND_ADVISORY_PROJECTION_SEMANTICS_ONLY`.

```text
projection authority          ADVISORY_ONLY
canonical_state_mutation      false
Google connectivity           NOT_PERFORMED
Google write                  NOT_PERFORMED
source correctness            NOT_PROVEN
```

GitHub/Google projections can inform humans/Agents but cannot write canonical Task/Workflow/Effect/Human/Release state.

## Local Handoff execution law

The public queue/runner/reducer are implemented, but public CI may not fabricate the local lane.

Current exact execution chain:

```text
queue-v4 #99
75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4
        ↓
H4R #103
7be0a69b0046b66799baee2ddb5e305c90d60ec6
        ↓ real local execution only
external secret-free receipt
        ↓
H4RR #107
4a44e9cf9ece133e8117ecc100e419f359d8e1a1
        ↓ semantic candidate only
canonical reducer / next epoch authority
```

Requirements:

- exactly one ACTIVE item;
- structured argv, `shell=False`;
- explicit cwd/timeout and env-name allowlist;
- no secret values/private source bytes in Git or portable receipts;
- checkout/worktree/receipt roots pairwise disjoint;
- pre-existing residue blocks before commands;
- main failure still attempts all declared cleanup commands;
- exact receipt schema validation before atomic write;
- H4R never advances queue state;
- H4RR never self-grants real-local credit;
- caller label `REAL_LOCAL_RECEIPT` is not evidence origin authority;
- exact external readback is required before the next queue epoch.

## Agent completion packet

Every completed atom must return:

```text
subject before / after commit + tree
writer lease / changed paths
Git relationship
all Gate attempts including RED history
external verification receipts
Shadow verdict
state/evidence ceiling
cleanup and residue result
claims_not_proven
closed issues / retained blockers
next owner / Local Handoff item
```

If any of these are unavailable, report the state explicitly rather than inferring PASS.
