# EAS-X — cross-repository P5 convergence

Status: **P5 CROSS-REPO CONVERGENCE CANDIDATE**  
Owner: `ed3c/enterprise_agent_system#12`  
Git parent: `EAS-E` PR #25 at `177ba870c41cc5605532ea79770d54aea124fa0c` / tree `20073aa3b719f30c95a6cbf449f0d6a2144f71c3`.

EAS-X is the aggregate ownership, subject and evidence-consistency layer. It does not own runtime execution, durable workflow state, effect state, provider adapters, independent verification, Human admission or release. Those facts remain with their canonical repositories.

## Why seven owner interfaces

A2 is deliberately split into two owners:

```text
A2R_RUNTIME_CONTRACT  → runtime-env
A2_SANDBOX_STEERING   → agent-shield-monorepo
```

A consumer sandbox PASS must not back-prove that a provider/runtime capability was observed. The same no-proxy rule applies across all owner lanes.

## Exact P4 inputs

| Interface | Canonical owner | Exact subject | P4 receipt class |
|---|---|---|---|
| A1 compaction/recovery | `ed3c/bettor-arena` | `21ac4fdcd6ce4c5acea920dc4e59a53d13ecd328` / `31ea6bec01899a4c9e4f994998ea6041116db49d` | process-crash SQLite readback |
| A2R runtime contract | `ed3c/runtime-env` | `cdfe74ac993cb0b4795fa80df237e8bb542409d2` / `0b2db695cdd812f81924b82689d96e3557b80158` | deterministic runtime contract |
| A2 sandbox/steering | `ed3c/agent-shield-monorepo` | `a611d9a4fd0122977539074b2d9009e422379c3f` / `597393c94fdd7733ac3fe0c4311c7f3c7dce18a3` | reversible local process + cleanup |
| A3 exact evidence | `ed3c/truth-verify-loop` | `5ea4dd42d2ee5bbd22537f5426cd276f10222980` / `fc6486b9ab6a48752e32a536a847c6e5635f8547` | public Git object readback |
| A4 provenance/telemetry | `ed3c/enterprise_agent_system` | `ee4602423424b716f12fea7797372a7dc4f3e288` / `f81c41b1e725517f610b671fb00d28af3af4dfbb` | synthetic sanitize-before-export canary |
| A5 discovery/admission | `ed3c/bettor-arena` | `81f02f4148273ffe5f5571c8605e1ee0afc59866` / `f9612314e47ced69796db00703dd5d34ab592e36` | matched sealed fixture benchmark |
| A6 ingress/effects | `ed3c/bettor-arena` | `8cd4aea59ff203a6620cb834e6a0df82b5e8ecaa` / `b95b5abe6bcc28df38f9758da790356ade990a59` | UNKNOWN_EFFECT restart reconciliation |

The canonical machine copy is `evidence/ledgers/cross-repo-closure.json`. Branch names and URLs are navigation only.

## P5 State Machine

```text
P4_SUBJECTS_BOUND
→ OWNER_UNIQUENESS_VERIFIED
→ EXACT_SUBJECTS_READ_BACK
→ EVIDENCE_LANES_RECONCILED
→ STRONGER_LANES_PRESERVED
→ PUBLIC_VERTICAL_CANARY_SELECTED
→ SHADOW_REVIEW_REQUIRED
→ READY_FOR_PROFILE_X_AND_P6
```

The current implementation is limited to the aggregate validation path through `PUBLIC_VERTICAL_CANARY_SELECTED`. An independent Shadow review of the final PR head is required before downstream handoff.

## Data flow

```text
P4 owner commits/trees + hosted runs + Shadow reviews
                  ↓
        cross-repo closure ledger
                  ↓
     fail-closed convergence validator
        ├─ one canonical owner/interface
        ├─ exact immutable subjects
        ├─ no lane substitution
        ├─ no false Git ancestry
        ├─ EAS-A remains NOT_IMPLEMENTED
        └─ stronger lanes remain no-credit
                  ↓
  INCEPTION-P5-PUBLIC-REVERSIBLE-CHAIN
                  │
                  └── PLAN_ONLY / no private data / no external effects
                  ↓
          independent X Shadow
          ├─ profile X #22
          ├─ P6 docs #13
          └─ stronger lanes → Local Handoff #14
```

## Git ancestry versus process dependencies

The X branch is a true child of EAS-E because it consumes the unmerged EAS-E `shadow.py` and inherited control-plane vocabulary. EAS-K, EAS-A and A1–A6 are process/evidence dependencies, not automatic Git parents.

The branch originally existed at stale merge-base `327d9b9efc9b5f913fe3e135083ab9e5c67e303b` with zero X commits. Shadow detected that it was 21 commits behind current EAS-E; Tech Lead fast-forwarded it without force to `177ba870c41cc5605532ea79770d54aea124fa0c` before writing X bytes. No X history was discarded.

## Missing EAS-A is part of the denominator

Issue `enterprise_agent_system#10` owns GitHub/Google Docs/Sheets advisory projection adapters. It currently has no implementation PR/subject. EAS-X therefore records:

```text
EAS-A
state   NOT_IMPLEMENTED
subject null
credit  0
```

P5 does not fabricate an adapter just to make the Molecular Stack look complete. P6 must continue showing this gap.

## Selected vertical canary

```text
id                INCEPTION-P5-PUBLIC-REVERSIBLE-CHAIN
state             PLAN_ONLY
interfaces         all seven owner interfaces
private data       false
external effects   false
Human operation    false
```

The plan composes evidence identities, not their side effects. It is useful as a bounded integration contract, but it is not an executed end-to-end agent run.

## Stronger lanes that remain unresolved

```text
physical power-loss / multi-host durability     NOT_EXERCISED
network / gVisor isolation                      NOT_EXERCISED
provider capability observation/enrollment      NOT_EXERCISED
external independent semantic provider          NOT_EXERCISED
private evidence                                 NOT_EXERCISED
exact external Model/Data/Trace terms            PARTIAL_OR_UNBOUND
live telemetry export/store/delete              NOT_EXERCISED
external candidate benchmark                    NOT_EXERCISED
real external effect / remote readback          NOT_PERFORMED
compensation                                     NOT_EXERCISED
business/user outcome                            NOT_VERIFIED
Human legal/security/admission                   HUMAN_ADMIT_REQUIRED
merge/release/rollback                           NOT_PERFORMED
```

A deterministic/public fixture cannot promote any of these states.

## Writer lease

EAS-X writes only its aggregate convergence lease:

```text
src/enterprise_agent_system/convergence.py
src/enterprise_agent_system/__init__.py          # export-only
src/enterprise_agent_system/README.md            # route-only
 tests/test_convergence.py
plans/architecture-closure.yaml
plans/task-dag.json
plans/molecular-stack-index.json
evidence/ledgers/cross-repo-closure.json
docs/integration/**
prompts/04-cross-repo-convergence.system.md
```

Root `README.md`, root `AGENTS.md`, `ARCHITECTURE.md`, `CONTEXT.md`, `docs/architecture/**`, `docs/traceability/**`, `integrations/**`, `handoff/**` and `.github/**` are not X-owned.

## Next authority

After exact-head validation plus independent Shadow:

```text
profile-specific P5 convergence  → enterprise_agent_system#22
root P6 docs/Stack convergence   → enterprise_agent_system#13
stronger local/provider lanes    → enterprise_agent_system#14
Human release/rollback           → bettor-arena#68
```

EAS-X itself cannot merge, close owner issues, authorize provider enrollment, approve private egress, perform an external effect, Human-admit, release or roll back.
