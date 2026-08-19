# Inception A4 — Code, Model, Data and Trace provenance

Status: **FIRST PUBLIC IMPLEMENTATION CANDIDATE**  
Upstream profile issue: `ed3c/enterprise_agent_system#16`  
True parent: `agent/inception-k-profile-dag@6e0a916fd06dd8635d77c9a8c4d1b475185ea13e`

This leaf implements a bounded, deterministic policy-candidate surface for four separately attributable provenance dimensions plus a sanitize-before-export telemetry-flow contract. It does not produce legal advice, commercial clearance, provider activation, telemetry deployment, Human admission, merge, release or rollback.

## Exact lineage

```text
repository        ed3c/enterprise_agent_system
base commit       6e0a916fd06dd8635d77c9a8c4d1b475185ea13e
base tree         c3851a6953d456d0342a9776eed28561c1af0ca1
branch            agent/inception-a4-provenance-policy
controller PR     #29
packet digest     sha256:b5c26bce1f39a9523b3b15585ac7a7d2a1618cbbc5a8e4cc980daea079e5e9de
packet bundle     sha256:dc4473b3195a738e55eb49c43661b6e1f4ea7f95c66749454776f2003b18ebc3
source digest     sha256:a6f1245ff865cae24838ed8ec4828330be684f3c03b29b9064ade8bfac94d8da
```

## Implementation subjects

```text
policies/provenance/four-tier-policy-candidate.schema.json
policies/provenance/telemetry-flow.schema.json
evidence/compliance/four-tier-policy.example.json
evidence/compliance/telemetry-flow.example.json
owners/compliance/verify_policy.py
```

Every Code, Model, Data and Trace dimension retains its own subject, explicit version, content digest, terms digest, obligations, blockers, expiry trigger, policy state and optional Human review subject. Allowed automated states are only:

```text
CANDIDATE
BLOCKED
UNKNOWN
HUMAN_REVIEW_REQUIRED
EXPIRED
```

The deterministic verifier refuses missing dimensions, mutable/missing terms digests, missing obligations, automated `COMMERCIALLY_SAFE` / `ADMITTED` outcomes and telemetry flows in which sanitization and negative leak controls occur after export.

## State Machine

```text
FOUR_TIER_SUBJECTS_DECLARED
→ EXACT_CONTENT_AND_TERMS_DIGESTS_BOUND
→ OBLIGATIONS_AND_EXPIRY_TRIGGERS_CLASSIFIED
→ DATA_FLOW_AND_SANITIZE_BEFORE_EXPORT_ASSERTED
→ AUTOMATED_POLICY_CANDIDATE_EMITTED
→ INDEPENDENT_SECURITY_REVIEWED
→ HUMAN_LEGAL_DISPOSITION_RECORDED
→ ADMITTED | BLOCKED | UNKNOWN | EXPIRED
```

The current implementation covers the deterministic candidate portion through `AUTOMATED_POLICY_CANDIDATE_EMITTED`. Independent security and Human legal disposition remain separate lanes.

## Telemetry data flow

```text
runtime event
→ CLASSIFY
→ SANITIZE
→ NEGATIVE_LEAK_CONTROLS
→ EXPORT to an allowlisted destination
→ STORE under explicit retention/training-use policy
```

A local or self-hosted route does not by itself prove zero leakage.

## Writer lease

```text
profiles/agent-thinking-inception/owners/compliance/**
profiles/agent-thinking-inception/policies/provenance/**
profiles/agent-thinking-inception/evidence/compliance/**
profiles/agent-thinking-inception/prompts/07-provenance-owner.system.md
.github/workflows/inception-a4-provenance.yml
```

Profile source, requirements, orchestration, generic Shadow, root docs, aggregate closure and Local Handoff remain read-only.

## Next transition

`BIND_EXACT_TERMS_SUBJECTS_AND_RUN_TELEMETRY_LEAK_CANARY`

The next atom must bind real external terms/version subjects and run an isolated leak-control canary. Automated checks still cannot make the Human legal/security disposition.

## Evidence ceiling

```text
four-tier policy schema      DETERMINISTIC_CANDIDATE
telemetry-flow schema        DETERMINISTIC_CANDIDATE
mutation controls            DETERMINISTIC_CANDIDATE
exact external terms         UNBOUND
live telemetry canary        NOT_EXERCISED
independent security review  NOT_EXERCISED
Human legal disposition      HUMAN_ADMIT_REQUIRED
merge / release / rollback   NOT_PERFORMED
```

Machine authority: [`preflight.json`](preflight.json).
