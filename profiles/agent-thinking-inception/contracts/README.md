# Agent Thinking Inception detailed contracts

This directory freezes the source-specific contract boundary consumed by profile Tech Lead issue #4. It does not implement a VFS, checkpointer, runtime, provider, verifier, effect ledger or release controller.

The source PDF proposes a token watchdog, structured state snapshot, VFS persistence and context reconstruction, then states that complete assistant/tool/result transactions must not be split. It also separates external Domain State from conversation history and places deterministic Gates before writeback. Those are source proposals; the records below convert them into falsifiable contracts without treating the sample code as production evidence.

## Contract State Machine

```text
SOURCE_REQUIREMENTS_COMPILED
→ RECORD_DENOMINATOR_FROZEN
→ STRICT_SHAPES_VALIDATED
→ CROSS_RECORD_INVARIANTS_ASSERTED
→ OWNER_INTERFACES_BOUND
→ MUTATION_CONTROLS_PASSED
→ CONTRACT_CANDIDATE
→ PROFILE_K_INPUT_READY
```

## Record denominator

| Record | Owns | Does not prove |
|---|---|---|
| `context-budget-policy/v1` | provider/model/tokenizer identity, advertised limit, reserve, soft/hard thresholds and measured use | a universal 75%/80% threshold or live token accounting |
| `safe-tool-transaction/v1` | ordered assistant tool calls, ordered results and safe compaction boundary | provider message compatibility without a live canary |
| `compaction-request/v1` | state-version-bound checkpoint request at a safe transaction boundary | checkpoint execution |
| `compaction-checkpoint-binding/v1` | version transition, manifests, unresolved work, leases, pending effects, rollback and recovery receipt | durable crash recovery without a physical fault matrix |
| `steering-capability-requirement/v1` | observed provider capabilities and bounded visible actions | hidden-reasoning access, prefill or abort support by assumption |
| `code-evidence-requirement/v1` | repository/commit/tree/path/line/snippet/symbol/parser/readback identity | semantic correctness of the claim |
| `citation-claim-requirement/v1` | source digest, locator, lexical Gate, semantic review and final disposition | zero hallucination from a model Judge |
| `four-tier-provenance-requirement/v1` | Code/Model/Data/Trace lineage, terms, obligations, blockers and review expiry | legal advice or commercial clearance |
| `ingress-writeback-requirement/v1` | event identity, authenticity, dedupe, durable admission, WriteIntent, effect reservation and remote readback | effect completion from HTTP acknowledgement |
| `profile-owner-binding/v1` | one canonical owner for each A1–A6 interface and required evidence lane | owner implementation |
| `profile-closure-record/v1` | literal requirement/contradiction denominator, lane states, blockers and Human operations | runtime, user, Human or release closure |

## Machine authority

```text
inception-contract-bundle.v1.schema.json
  → strict Draft 2020-12 field denominator

../examples/inception-contract-bundle.example.json
  → honest positive candidate with zero operational closure credit

../tests/contracts/verify_contracts.py
  → cross-record semantic laws + planted disagreement controls
```

Run:

```bash
python3 profiles/agent-thinking-inception/tests/contracts/verify_contracts.py
python3 profiles/agent-thinking-inception/tests/contracts/verify_contracts.py --selftest
```

A green result means only `CONTRACT_CANDIDATE_ONLY`. It cannot advance profile K unless the exact parent commit/tree and bundle digest are rebound in the downstream packet. It never authorizes provider enrollment, private-source egress, external writes, issue closure, semantic-conflict resolution, merge, release or rollback.
