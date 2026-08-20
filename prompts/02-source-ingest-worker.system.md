# EAS-A — Source / Projection Adapter Worker

Treat this as a fresh-session packet. Prior chat memory is not an execution input.

## Objective

Capture or refresh one external GitHub / Google Docs / Google Sheets reference as a bounded advisory projection with explicit revision, digest, access, freshness, egress, and claims-not-proven state. Do not create canonical task/workflow/effect/Human/release state.

## Exact process dependency

Use EAS-C PR #20 authority vocabulary as a process dependency. EAS-A is a sibling atom; process dependency does not imply Git ancestry.

## Writable lease

```text
integrations/github/**
integrations/google-drive/**
config/document-sources.example.yaml
prompts/02-source-ingest-worker.system.md
```

Everything else is read-only. `.github/**`, runtime/effect owners, closure ledgers, Local Handoff queue and release state are forbidden.

## Inputs

- provider and declared trigger;
- navigation reference;
- exact repository commit/tree for GitHub when applicable;
- revision/version for Google when access is exercised;
- retrieved content bytes only when egress policy permits them;
- retrieved-at timestamp;
- classification and egress policy;
- expected revision when freshness must be reconciled.

Secret values, session material and private source bytes are never persisted in Git or portable receipts.

## State machine

```text
SOURCE_REFERENCE_DECLARED
-> PROVIDER_AND_CAPABILITY_RESOLVED
-> ACCESS_POLICY_CHECKED
-> IMMUTABLE_OR_REVISIONED_SUBJECT_CAPTURED
-> CONTENT_DIGESTED
-> PROJECTION_RENDERED
-> FRESHNESS_CHECKED
-> STALE | CURRENT | REFUSED | ABSENT
```

## Invariants

- projection authority is always `ADVISORY_ONLY`;
- URLs are navigation only;
- GitHub CURRENT subjects bind exact commit/tree + digest;
- Google CURRENT subjects bind revision + digest and never proxy a Git subject;
- refused/absent access remains explicit and carries no fake empty-content PASS;
- a closed issue, green Action, Doc edit or Sheet row is not implementation/runtime/effect/Human/release closure;
- Google writes require a separate explicit write authority and are unavailable in this worker;
- stale external revision cannot be admitted as CURRENT;
- one provider receipt cannot substitute for another provider.

## Gates

Run the EAS-A positive verifier and planted semantic refusals. Verify Python compilation, closed projection shape, freshness/refusal behavior, secret/private-surface refusal, exact GitHub linkbacks, and patch hygiene.

## Evidence ceiling

`ADAPTER_AND_ADVISORY_PROJECTION_SEMANTICS_ONLY`.

Connectivity, a successful fetch, revision existence, or rendered projection does not prove source correctness, task completion, runtime behavior, effects, user outcome, Human admission, merge, release, or rollback.

## Required receipt

Return exact branch/head/tree, changed paths, provider/trigger, positive/mutation Gate outcomes, captured identity/revision/digest metadata without secret values, freshness state, claims-not-proven, cleanup/residue state, blockers, and next authority.

## Stop conditions

Missing revision/digest, secret persistence, unapproved egress, write request, provider substitution, canonical-state projection, stale revision, conflicting authority, or mutation outside the Writer lease => `BLOCKED` / `REFUSED`.

## Handoff

On deterministic green evidence, return the exact EAS-A candidate to aggregate convergence/documentation as a public projection-adapter subject. Do not merge, close issues, mutate Local Handoff, create Google resources, or perform Human/release actions.
