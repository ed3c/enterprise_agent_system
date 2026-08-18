# Control-plane contracts

This directory is the machine boundary owned by `enterprise_agent_system`.

It may define source identities, cross-repository bindings, closure records and orchestration-run records. It must never redefine the five Dual-Agent runtime wire contracts owned by `ed3c/runtime-env`, or copy the portable method schema owned by `ed3c/skills-shared`.

## State machine

```text
UNBOUND
→ SOURCE_SUBJECT_BOUND
→ OWNER_PLANE_BOUND
→ CONTRACT_IDS_BOUND
→ EVIDENCE_LANES_DECLARED
→ CLOSURE_RECORD_VALIDATED
→ CONSUMER_READY
```

## Files

| File | Owns | Does not prove |
|---|---|---|
| `source-subject.v1.schema.json` | revisioned/content-addressed source identity | source correctness |
| `cross-repo-binding.v1.schema.json` | one owner per interface and consumer routing | compatibility or execution |
| `closure-record.v1.schema.json` | lane-by-lane evidence state, blockers and next transition | live closure |
| `orchestration-run.v1.schema.json` | tasks, dual edges, leases, reducer/Shadow authority | Worker execution |
| `verify.py` | cross-record semantic refusal laws | JSON Schema completeness |
| `test_verify.py` | positive and planted negative controls | production readiness |

## Deterministic gate

```bash
python3 contracts/control-plane/verify.py contracts/control-plane/examples/*.json
python3 contracts/control-plane/test_verify.py
```

Exit `0` means only that the named records passed this deterministic semantic gate. Exit `2` is a named refusal. No result authorizes merge, issue closure, permission changes, provider enrollment, data egress, irreversible effects, release or rollback.
