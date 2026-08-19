# Agent Thinking Inception prompt catalogue

This catalogue is a documentation projection for P0-P7. It does not execute a task or create authority. Every entry is either an existing immutable Git blob or a deterministic prompt rendered from the exact Profile-K packet specification.

## Exact catalogue inputs

```text
profile-X parent
  commit a27aa552f1c258e09f515b4a5d117ba37f4d6615
  tree   71eaa3f4acafd0b004ccdff16e4aa14bc2599649

Profile-K packet source
  profiles/agent-thinking-inception/orchestration/profile-worker-packet-specs.json
  blob e088ead98d9f11590bd8b9621dce64f2e25fcbbe

packet renderer
  profiles/agent-thinking-inception/orchestration/compile_profile_packets.py
  blob 7e320dbfce8119002ad53b3a20291598490d3610

rendered packet bundle
  sha256:dc4473b3195a738e55eb49c43661b6e1f4ea7f95c66749454776f2003b18ebc3
```

## Catalogue

| Phase | Role | Prompt source | Content identity / route |
|---|---|---|---|
| P0 | Source & Authority Auditor | `00-source-auditor.system.md` | Git blob `e786de9d2465d551bab625e03a8dbf3321bdb102` |
| P1 | Profile Contract Worker | `01-profile-contract-worker.system.md` | Git blob `53d6752f246062f537b24f14ad6ff2fb5253e654` |
| P2 | Profile Tech Lead Controller / DAG Compiler | `02-tech-lead-profile-controller.system.md` | Git blob `e3115597a6344b0fb26bc3f3e2d6beba973614ee` |
| P3 | A1 compaction owner | render `TASK-INCEPTION-A1` | Profile-K packet bundle digest above |
| P3 | A2 runtime/sandbox/steering owner | render `TASK-INCEPTION-A2` plus exact A2R runtime contract binding | Profile-K packet bundle digest above |
| P3 | A3 exact evidence owner | render `TASK-INCEPTION-A3` | Profile-K packet bundle digest above |
| P3 | A4 provenance/telemetry owner | render `TASK-INCEPTION-A4` | Profile-K packet bundle digest above |
| P3 | A5 discovery/admission owner | render `TASK-INCEPTION-A5` | Profile-K packet bundle digest above |
| P3 | A6 ingress/effect owner | render `TASK-INCEPTION-A6` | Profile-K packet bundle digest above |
| P4 | Profile Shadow Architect | render `TASK-INCEPTION-E` | Profile-K packet bundle digest above; final Shadow implementation subject is PR #32 |
| P5 | Profile Convergence Owner | `11-profile-convergence.system.md` | Git blob `84bcf05fb30353e750225cd0d054faffe6d16834` |
| P6 | Profile Docs / Stack Convergence | `12-profile-docs-convergence.system.md` | current Profile-D branch; exact blob must be rebound in P6 receipt |
| P7 | Profile Local Handoff Compiler | render `TASK-INCEPTION-H` / consume EAS-H #27 queue contract | Profile-K packet bundle + exact EAS-H receipt |

`03-profile-worker-envelope.system.md` (blob `c8073d5ccc250e61a4bb0e78c0e60744473ac40b`) is the common owner Worker envelope consumed by the deterministic packet renderer; it is not an extra phase.

## Fresh-session contract

Every direct or rendered system prompt must be executable without hidden prior chat context and must bind:

```text
exact repository / commit / tree
source/profile digest and class
objective + non-goals
invariants + unknowns
one role + one owner issue
writable / read-only / forbidden paths and resources
start dependencies + completion dependencies
input/output contracts
positive controls + planted disagreement controls
runtime/capability requirements
retry budget + timeout
cleanup/residue/retention/rollback limits
required evidence lane + evidence ceiling
required receipt fields
stop conditions
claims_not_proven
next authority
```

## Deterministic rendering

The canonical renderer is:

```text
python3 profiles/agent-thinking-inception/orchestration/compile_profile_packets.py --output <isolated-dir>
```

The output must contain ten task JSON packets, ten system prompts and one manifest. Generated prompts are candidates until their exact bytes/digests are read back; a task packet existing does not mean the task executed.

## Authority boundary

- GitHub issues/PRs/commits/trees/Actions receipts are canonical publication metadata.
- Google Docs may contain long-form prompt review copies; Google Sheets may contain a human matrix/dashboard.
- Google Docs/Sheets are `ADVISORY_ONLY`; their wording cannot mutate task, workflow, effect, Human or release state.
- Chat memory is not an input to a fresh-session prompt.
- Prompt agreement or execution success cannot self-authorize merge, release or rollback.
