# Agent Thinking Inception profile Tech Lead plan

This directory consumes exact EAS-C, EAS-K, profile C0 and detailed C1 subjects, then compiles the source profile into a deterministic macro DAG and content-addressed fresh-session packets. It prepares owner work; it does not implement owner repositories or execute runtime, provider, effect, Human or release lanes.

## Exact input State Machine

```text
EXACT_C_K_C0_C1_SUBJECTS_DECLARED
→ MULTI_PARENT_PROFILE_K_BASE_BOUND
→ PROFILE_K_INPUTS_VALIDATED
→ CAPABILITY_PLAN_COMPILED
→ START_AND_COMPLETION_DAGS_ASSERTED
→ DISJOINT_WRITER_AND_RESOURCE_LEASES_BOUND
→ TEN_ZERO_CONTEXT_PACKETS_EMITTED
→ PROFILE_STACK_DERIVED
→ OWNER_SESSIONS_READY
```

Current evidence ceiling:

```text
PROFILE_K_PLAN_CANDIDATE_ONLY
```

## Parallel waves

```text
Wave 0  TASK-INCEPTION-K
Wave 1  A1 A2 A3 A4 A5 A6
Wave 2  E  read-only profile Shadow
Wave 3  X  profile convergence
Wave 4  D  profile docs/State Machines/data flow/Stack
Wave 5  H  profile request for the canonical EAS Local Handoff queue
```

A1–A6 are process siblings after the profile controller. They are not Git children of one another and must not be serialized when path and external-resource leases are disjoint.

## Machine files

| File | Owns | Does not prove |
|---|---|---|
| `profile-input-binding.json` | exact C/K/C0/C1/base/Shadow identities and digests | source or implementation correctness |
| `profile-run.json` | task DAG, separate start/completion edges, writer/path/resource leases and reducer authority | Worker execution |
| `profile-capability-plan.json` | selected capability transitions, fallbacks and authority ceilings | live capability receipts |
| `profile-worker-packet-specs.json` | ten zero-context owner/Shadow/X/D/H specifications | generated packet execution |
| `compile_profile_packets.py` | deterministic packet rendering and digesting through generic EAS-K | owner repository mutation |
| `profile-molecular-stack-index.json` | observed C/K/C0/C1 and planned K/A/E/X/D/H atoms | merge schedule or operational closure |

## Generate fresh-session packets

```bash
python3 profiles/agent-thinking-inception/orchestration/compile_profile_packets.py \
  --output /tmp/inception-profile-packets
```

The output contains:

```text
manifest.json
10 machine packet .json files
10 complete fresh-session .system.md files
```

Each packet carries the exact input subjects, owner issue/interface, writable/read-only paths, start/completion dependencies, required evidence lane, positive and planted disagreement controls, runtime/capability requirements, budgets, cleanup/residue/rollback contract, required receipt, evidence ceiling and next authority.

## Deterministic gate

```bash
python3 profiles/agent-thinking-inception/tests/dag/verify_profile_dag.py
python3 profiles/agent-thinking-inception/tests/dag/verify_profile_dag.py --selftest
```

The gate validates both DAG edge classes, six-way parallelism, packet and bundle digests, capability causality, owner uniqueness, Shadow read-only authority, observed versus planned Stack atoms, Human-only operations and source/private-data boundaries.

## Stop boundary

Packet generation cannot mark any A1–A6 task executed. Owner exact subjects must be rebound before mutation. Profile Shadow waits for exact owner candidates. Profile X cannot infer live or Human closure. Profile H emits only a request; the single canonical queue remains owned by generic EAS-H issue #14.

No controller or packet may approve private-source egress, resolve semantic conflicts, perform irreversible effects, close issues, merge, release or roll back.
