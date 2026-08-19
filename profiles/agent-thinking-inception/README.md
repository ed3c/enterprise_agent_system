# Agent Thinking Inception integration profile

This profile compiles the 26-page **Agent Thinking Inception: Dynamic Intervention** PDF into a source-bound requirement graph. The PDF remains `SOURCE_PROPOSAL`; it is not copied into this public repository and earns no implementation, live, user, Human, release, or operational closure credit.

## Current verdict

```text
source digest and page map              CANDIDATE
real-problem requirement denominator    CANDIDATE
contradiction/evidence-ceiling ledger   CANDIDATE
profile contract shape                  CANDIDATE
generic EAS-K orchestration             NOT_ADMITTED
owner implementations                   NOT_BOUND
local/provider/live canaries            NOT_EXERCISED
Human admission/release/rollback        NOT_PERFORMED
```

## State Machine

```text
SOURCE_REGISTERED
→ PAGE_LOCATORS_CAPTURED
→ CLAIMS_CLASSIFIED
→ REQUIREMENTS_ASSIGNED
→ OWNER_LANES_PROPOSED
→ CONTROLS_AND_EVIDENCE_CEILINGS_BOUND
→ CONTRADICTIONS_ROUTED
→ PROFILE_CONTRACT_READY
→ EAS-K_CONSUMER_DAG
```

## Files

| Path | Authority |
|---|---|
| `source/source-subject.json` | content-addressed source identity; no source correctness claim |
| `source/source-map.json` | page-to-requirement-family navigation |
| `requirements/requirements.json` + shards | complete current denominator and owner routes |
| `requirements/contradictions.json` | source gaps that must stay visible |
| `contracts/inception-profile.v1.schema.json` | source-specific profile bundle shape |
| `examples/inception-profile.example.json` | positive candidate |
| `tests/verify_profile.py` | deterministic semantic checks and planted mutations |
| `prompts/*.system.md` | zero-context P0/P1 session packets |

## Owner split

```text
enterprise_agent_system     source/profile/DAG/closure routing
skills-shared               portable Tech Lead, Shadow, Stack and handoff laws
runtime-env                 secret-free runtime/capability/workload contracts
bettor-arena                durable workflow/state/VFS/effect ledger and E2E
agent-shield-monorepo       sandbox/provider/API/browser/webhook adapters
truth-verify-loop           independent evidence verification
openwiki-source-anchoring   exact lexical/source anchors
```

One interface or canonical state has one owner. This profile must not add a second runtime, VFS, workflow reducer, effect ledger, verifier, or release authority.

## Deterministic gate

```bash
python3 profiles/agent-thinking-inception/tests/verify_profile.py
python3 profiles/agent-thinking-inception/tests/verify_profile.py --selftest
```

A green result proves only that the checked profile bytes satisfy the declared source/requirement routing laws. It does not prove any owner implementation or live behavior.
