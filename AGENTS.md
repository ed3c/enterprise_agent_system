# AGENTS.md — enterprise_agent_system operating contract

`enterprise_agent_system` is the cross-repository control and closure plane. It must remain provider-neutral, secret-free and honest about evidence ceilings.

## Mandatory read order

1. `README.md` — current verdict, phase model, directory/DAG/data flow and Stack.
2. `CONTEXT.md` — mutable exact current subjects, active issues/PRs and handoff.
3. `ARCHITECTURE.md` — stable plane ownership, invariants and State Machines.
4. `contracts/control-plane/README.md` and exact schemas/examples/gates.
5. `docs/INDEX.md`, `docs/architecture/STATE_MACHINES.md`, `docs/architecture/DATA_FLOW.md`.
6. `docs/traceability/MOLECULAR_STACK_INDEX.md`.
7. `prompts/README.md` and the exact phase/session prompt.
8. The nearest profile/directory `README.md` and `AGENTS.md`.
9. The exact issue, PR base/head, commit/tree, changed paths, Gate receipt and evidence lane.
10. For physical/local/provider work, `handoff/README.md` and the canonical queue item.

Do not infer missing content from sibling repositories, chat memory, branch names, issue state or prose. Missing route/owner/contract/receipt is `ABSENT` or `NOT_IMPLEMENTED`.

## Runtime classification before mutation

Classify by observed capability, not prompt/model name:

```text
trusted explicit runtime override
→ GitHub Actions exact-run evidence
→ local checkout + git/shell/launcher evidence
→ Desktop-created worktree evidence
→ GitHub connector/API capability
→ UNKNOWN
```

`CHATGPT_GITHUB_CONNECTOR` is not a local checkout, GitHub Actions runner, provider runtime or Forgejo host. `UNKNOWN` fails closed for irreversible actions.

## Source and evidence laws

- A PDF, article, diagram, prompt or model response is `SOURCE_PROPOSAL` until admitted.
- Repository bytes and deterministic controls do not prove provider/live/user/Human/release state.
- `PASS`, `FAIL`, `ABSENT`, `NOT_IMPLEMENTED`, `NOT_EXERCISED`, `BLOCKED`, `STALE_SOURCE_PIN`, `UNKNOWN_EFFECT`, `HUMAN_ADMIT_REQUIRED`, `RELEASED` and `OPERATED_WITH_ROLLBACK` remain distinct.
- Every promoted claim binds exact repository/commit/tree/digest, tool/runtime identity, lane and readback.
- A URL is navigation; mutable branch, Doc wording, Sheet row, issue state or PR head is not immutable evidence.
- Failed, blocked, retried, abstained, conflicted and skipped attempts remain in the denominator.

## One-interface / one-owner law

```text
enterprise_agent_system   routing, closure, indexes, handoff compilation
skills-shared             portable procedural methods
runtime-env               runtime/workload/capability contracts
bettor-arena              durable workflow/state/VFS/effects/E2E
agent-shield-monorepo     sandbox/provider/API/browser/telemetry adapters
truth-verify-loop         independent verification
openwiki-source-anchoring lexical anchors
Human/trusted policy      merge, release, legal/security/egress/irreversible decisions
```

Never copy an owner contract or implementation merely because its issue is absent. Emit a typed owner packet and keep the state `ABSENT`/`NOT_IMPLEMENTED`.

## Tech Lead / Worker / Gate / Shadow / reducer / Human boundaries

- **Tech Lead:** freezes objective/contracts, compiles capability/task/evidence DAGs, start/completion edges, prompts, leases, gates and handoff.
- **Worker:** writes only its leased paths/resources and returns candidate artifacts/receipts.
- **Gate:** executes declared deterministic or live assertions on the exact subject; it cannot widen authority.
- **Shadow:** read-only independent applicability, contradiction, false-promotion, global-objective, cleanup and rollback monitor. It receives no private chain of thought and edits no Builder path.
- **Reducer:** the one canonical writer that reconciles candidates and lane-literal receipts.
- **Human/trusted policy:** semantic conflict, provider enrollment, egress, irreversible effects, legal/security admission, merge, release and destructive rollback.

Worker/provider/model self-report is never canonical closure.

## Dependency and lease laws

- Freeze contracts before Worker fan-out.
- Separate start-readiness from completion-readiness.
- A true Git child consumes named unmerged parent bytes. Path-disjoint process siblings are not serialized for convenience.
- One active writer owns each branch/worktree/path/interface/database namespace/port/provider session/document projection/aggregate index.
- Overlapping leases fail closed.
- Parent movement, rebase, conflict resolution or synchronization invalidates stale exact-head evidence for affected children.
- Shared/root/index/closure paths converge once through their named owner.
- Semantic conflicts stop; do not auto-resolve them.

## Fresh-session prompt packet

Every session packet must contain exact subjects/digests, objective/non-goals/invariants/unknowns, one role/issue/atom, writable/read-only/forbidden paths/resources, start/completion dependencies, schemas, positive and mutation controls, runtime/capability requirements, evidence ceiling, retry/budget/timeout/cleanup/rollback limits, receipt and next authority. Prior conversation memory is never a dependency.

## Google and GitHub projection boundary

- GitHub issues/PRs/commits/Actions are delivery metadata and exact source links.
- Google Docs/Sheets are `ADVISORY_ONLY` views.
- Canonical machine records live in versioned Git bytes and reducer-owned state.
- Read-only is the default. Writes require explicit adapter/action authority.
- Missing/forbidden/partial access remains explicit; never treat it as empty content or PASS.
- Do not persist OAuth/session tokens, API keys, browser/device sessions or secret values.

## Pre-side-effect Gate

Before any external write, bind:

```text
exact task/attempt/state version
WriteIntent and effect identity
least-privilege capability
expected remote version
applicable deterministic/semantic/Human Gates
idempotency reservation
timeout and unknown-effect handling
remote readback
compensation/rollback subject
```

Unknown effect blocks blind retry.

## Verification and cleanup denominator

Completion requires all declared positive and disagreement controls, exact subject readback, failed-attempt denominator, residue/cleanup inventory, retention/deletion state, rollback identity and claims-not-proven. A green command exit without receipt/readback/cleanup is not completion.

## Local Handoff law

Compile Local Handoff only when work crosses a real unavailable host/runtime/provider/Human boundary. The queue:

- has exactly one `ACTIVE` item;
- keeps successors `BLOCKED_BY_PREDECESSOR`;
- uses concrete argv arrays, cwd, timeout, environment-name allowlist, receipt path/schema, cleanup and rollback;
- contains no secret values or generic shell;
- advances only after exact receipt + subject readback + cleanup;
- does not auto-merge, close, release, enroll, approve egress or perform irreversible actions.

Queue validation proves executable shape, not execution.

## Writable-path routing

Use the nearest issue/AGENTS lease. Root `README.md`, root `AGENTS.md`, `ARCHITECTURE.md`, `CONTEXT.md`, aggregate indexes and handoff narrative are EAS-D convergence paths. Generic contracts are EAS-C; orchestration core is EAS-K; projections are EAS-A; independent controls are EAS-E; aggregate closure is EAS-X. Profile atoms write only under their profile.

## Stop conditions

Stop on stale subject/digest, missing owner, duplicate interface owner, cycle, false Git child, overlapping lease, unavailable capability represented as PASS, private data egress, unsupported provider steering, incomplete tool transaction, evidence-lane substitution, unresolved critical finding without issue, unknown external effect, failed cleanup, semantic conflict, permission/visibility/license change, merge/release/rollback boundary or disagreement between issue/PR state and machine records.

Continue independent safe work; do not smooth blocked lanes into completion.

## Completion packet

```text
applicable requirement IDs and states
exact base/head/tree/digests and changed paths
directory/State Machine/DAG owner
issue/Stack/PR lineage and true parent set
start and completion dependencies
writer/path/resource leases
positive and mutation Gate results
required lane and receipt lane
failed/blocked/skipped denominator
cleanup/residue/retention/compensation
claims not proven and evidence ceiling
Google/GitHub projection freshness
Local Handoff items and capability blockers
rollback subject and next authority
Human-owned operations not performed
```
