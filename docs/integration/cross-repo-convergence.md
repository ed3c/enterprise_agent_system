# EAS-X — cross-repository P5 convergence

Status: **P5 CROSS-REPO CONVERGENCE CANDIDATE — EAS-A REBOUND**
Owner: `ed3c/enterprise_agent_system#12`
Git parent: `EAS-E` PR #25 at `177ba870c41cc5605532ea79770d54aea124fa0c` / tree `20073aa3b719f30c95a6cbf449f0d6a2144f71c3`.

EAS-X is the aggregate ownership, subject and evidence-consistency layer. It does not own runtime execution, durable workflow state, effect state, provider adapters, independent verification, Human admission or release.

## Current admitted process dependencies

```text
EAS-K
  b1362f48b6edc0b4cd6d301da2a5d0e94d970f8c
  tree 19353937e8d642a0bd731e20b3f61ffa3af2b913
  state DETERMINISTIC_VERIFIED

EAS-A
  PR #68
  250717db1cad584d50890c0d851153fa2cd755e8
  tree fbf6a75b6e89e906f227110dc5a61e4355b8a891
  hosted verify 32295871632 PASS
  Shadow 4976213414 = ADMIT_FOR_CONVERGENCE_REBIND
  state DETERMINISTIC_VERIFIED
  authority ADVISORY_ONLY
  ceiling ADAPTER_AND_ADVISORY_PROJECTION_SEMANTICS_ONLY
```

EAS-A is a **process dependency, not a Git parent and not a runtime/workflow/effect owner**. Its admission proves only public adapter/advisory-projection semantics. Google connectivity, Doc/Sheet creation/write, live revision observation, private/credential access and canonical-state mutation remain unperformed/forbidden.

Historical EAS-A subject `dc7c5b57c3d175c861378474eff40e4b3ac9232d` with run `32295745774` / Shadow `4976203497` is content-equivalent history only; exact-subject law requires the current `250717db...` receipt.

## Seven canonical owner interfaces

A2 remains deliberately split:

```text
A2R_RUNTIME_CONTRACT  → runtime-env
A2_SANDBOX_STEERING   → agent-shield-monorepo
```

Current owner subjects remain unchanged by the EAS-A rebind:

| Interface | Owner | Exact commit | Current public lane |
|---|---|---|---|
| A1 | `ed3c/bettor-arena` | `21ac4fdcd6ce4c5acea920dc4e59a53d13ecd328` | process-crash SQLite readback |
| A2R | `ed3c/runtime-env` | `2ff4efe7bee3d12fb3063fed93631f8d323cd64a` | runtime contract |
| A2 | `ed3c/agent-shield-monorepo` | `8ec782b78ec9e13f78f2faf14e6ffa722c1b78f2` | reversible local process cleanup |
| A3 | `ed3c/truth-verify-loop` | `5ea4dd42d2ee5bbd22537f5426cd276f10222980` | public Git object readback |
| A4 | `ed3c/enterprise_agent_system` | `bf976c7c33e315d1743733a79c15521e645ff6dc` | synthetic telemetry leak canary |
| A5 | `ed3c/bettor-arena` | `81f02f4148273ffe5f5571c8605e1ee0afc59866` | matched sealed fixture benchmark |
| A6 | `ed3c/bettor-arena` | `c2613432736c65756ed13d871feb2df486c69118` | UNKNOWN_EFFECT restart reconciliation |

Machine authority remains `evidence/ledgers/cross-repo-closure.json`; model/Judge agreement is not Shadow evidence.

## State Machine

```text
P4_SUBJECTS_BOUND
→ OWNER_UNIQUENESS_VERIFIED
→ EXACT_SUBJECTS_READ_BACK
→ PROCESS_DEPENDENCIES_RECONCILED
→ SHADOW_PROVENANCE_TYPED
→ EVIDENCE_LANES_RECONCILED
→ STRONGER_LANES_PRESERVED
→ PUBLIC_VERTICAL_CANARY_SELECTED
→ FRESH_SHADOW_REVIEW_REQUIRED
→ READY_FOR_PROFILE_X_AND_P6
```

## Guarded data flow

```text
exact owner subjects + EAS-K + exact EAS-A advisory receipt
                         ↓
             cross-repo closure ledger
                         ↓
             fail-closed validator
        ├─ one canonical owner/interface
        ├─ exact current EAS-A commit/run/Shadow
        ├─ EAS-A authority = ADVISORY_ONLY
        ├─ no lane substitution
        ├─ no false Git ancestry
        └─ 13 stronger lanes remain no-credit
                         ↓
       public vertical canary = PLAN_ONLY
                         ↓
                 fresh X Shadow
            ├─ Profile-X rebind #22
            ├─ P6 rebind #13
            └─ P7 remains suspended until descendants rebind
```

## Stronger lanes remain unresolved

```text
physical power-loss / multi-host durability     NOT_EXERCISED
network / gVisor isolation                      NOT_EXERCISED
provider capability/enrollment                  NOT_EXERCISED
external independent semantic                   NOT_EXERCISED
private evidence                                NOT_EXERCISED
exact external Model/Data/Trace terms           PARTIAL_OR_UNBOUND
live telemetry export/store/delete              NOT_EXERCISED
external candidate benchmark                    NOT_EXERCISED
real external effect / remote readback          NOT_PERFORMED
compensation                                    NOT_EXERCISED
business/user outcome                           NOT_VERIFIED
Human legal/security/admission                  HUMAN_ADMIT_REQUIRED
merge/release/rollback                          NOT_PERFORMED
```

EAS-A admission does not grant credit to any of these lanes.

## Git ancestry

EAS-X remains a true child of EAS-E because it consumes EAS-E bytes. EAS-K, EAS-A and A1–A6 are process/evidence dependencies only. Do not create a false Git child edge from EAS-A.

## Freshness consequence

Profile-X #40, Profile-D #44, Root-D #57, queue-v3 #59, H3R #67 and H3RR #71 were built while their aggregate projections still said `EAS-A NOT_IMPLEMENTED`. They remain historical exact subjects, but **current downstream execution authority is suspended until each affected aggregate/document/handoff layer is rebound from the newly admitted EAS-X subject**.

## Writer lease

EAS-X writes only its aggregate convergence lease:

```text
src/enterprise_agent_system/convergence.py
src/enterprise_agent_system/__init__.py
src/enterprise_agent_system/README.md
tests/test_convergence.py
plans/architecture-closure.yaml
plans/task-dag.json
plans/molecular-stack-index.json
evidence/ledgers/cross-repo-closure.json
docs/integration/**
prompts/04-cross-repo-convergence.system.md
```

Root docs, `integrations/**`, `handoff/**` and `.github/**` are not X-owned.

## Next authority

After exact-head validation and fresh independent X Shadow:

```text
Profile-X #22   rebind current profile convergence
P6 #13          rebind root docs/Stack
P7 #14          recompile current Local Handoff only after P5/P6 descendants are current
```

No merge, provider enrollment, Google write, private-data egress, external effect, Human admission, release or rollback is authorized.
