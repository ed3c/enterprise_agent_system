# Inception A4 — Code, Model, Data and Trace provenance

Status: **PUBLIC SYNTHETIC TELEMETRY LEAK CANARY — DETERMINISTIC PASS CANDIDATE**
Upstream profile issue: `ed3c/enterprise_agent_system#16`
True parent: `agent/inception-k-profile-dag@6e0a916fd06dd8635d77c9a8c4d1b475185ea13e`

This leaf implements a bounded policy-candidate surface for four separately attributable provenance dimensions and an explicit sanitize-before-export telemetry-flow contract. It now also exercises that flow against a synthetic local-sink leak canary. It does not produce legal advice, commercial clearance, provider activation, live telemetry deployment, a zero-leakage claim, Human admission, merge, release or rollback.

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
owners/compliance/telemetry_canary.py
owners/compliance/test_telemetry_canary.py
prompts/07-provenance-owner.system.md
```

Every Code, Model, Data and Trace dimension retains its own subject, explicit version, content digest, terms digest, obligations, blockers, expiry trigger, policy state, Human review owner and optional Human review receipt subject. Automated states are limited to:

```text
CANDIDATE
BLOCKED
UNKNOWN
HUMAN_REVIEW_REQUIRED
EXPIRED
```

The deterministic verifier rejects missing dimensions, mutable or missing terms digests, missing obligations, absent Human owners, unknown nested fields, automated `COMMERCIALLY_SAFE` / `ADMITTED` outcomes and telemetry flows that omit required sanitization, access, retention, deletion or negative-control contracts.

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

This atom covers the deterministic candidate path through `AUTOMATED_POLICY_CANDIDATE_EMITTED` plus a synthetic leak canary. Independent security, exact external terms subjects, live telemetry and Human legal disposition remain separate lanes.

## Telemetry data flow

```text
runtime event
→ CLASSIFY payload classes
→ SANITIZE explicit fields
→ DROP disallowed fields
→ NEGATIVE_LEAK_CONTROLS
→ EXPORT through exact allowlisted exporter
→ STORE under explicit RBAC + tenant scope + retention policy
→ DELETE with required deletion receipt
```

Collector, exporter and storage are versioned and content-addressed by configuration digest. A local or self-hosted route still does not prove zero leakage.

## Synthetic leak canary

The public canary plants synthetic sensitive markers before sanitization:

```text
fixture bearer token
fixture cookie
fixture PII email
fixture proprietary prompt marker
fixture raw secret marker
fixture proprietary source marker
```

It validates the declared flow, refuses a non-allowlisted destination, redacts configured fields, drops configured fields, writes only the sanitized payload to a temporary local sink, reads the sink bytes back and scans them for every planted value. A planted-leak detector is itself exercised as a negative control. The temporary sink is deleted when the canary exits.

This evidence is deliberately bounded:

```text
synthetic sanitizer mechanics        tested
sanitize-before-export ordering       tested
local sink readback                   tested
live collector/exporter/storage       not exercised
real provider/runtime payloads        not exercised
zero-leakage claim                    forbidden
```

## Writer lease

```text
profiles/agent-thinking-inception/owners/compliance/**
profiles/agent-thinking-inception/policies/provenance/**
profiles/agent-thinking-inception/evidence/compliance/**
profiles/agent-thinking-inception/prompts/07-provenance-owner.system.md
.github/workflows/inception-a4-provenance.yml
```

Profile source, requirements, contracts, orchestration, generic Shadow, root docs, aggregate closure and Local Handoff remain read-only.

## Evidence ceiling

```text
four-tier policy schema       DETERMINISTIC_PASS
telemetry-flow schema         DETERMINISTIC_PASS
mutation controls             DETERMINISTIC_PASS
synthetic leak canary         DETERMINISTIC_PASS
exact external terms          UNBOUND
live telemetry canary         NOT_EXERCISED
independent security review   NOT_EXERCISED
Human legal disposition       HUMAN_ADMIT_REQUIRED
merge / release / rollback    NOT_PERFORMED
```

Machine authority: [`preflight.json`](preflight.json).

## Next transition

`BIND_EXACT_EXTERNAL_TERMS_AND_RUN_SCOPED_LIVE_TELEMETRY_CANARY`

The next atom must bind exact external Code/Model/Data/Trace terms/version subjects before any scoped live telemetry canary. Automated checks still cannot make the Human legal/security disposition.
