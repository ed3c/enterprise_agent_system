# ADR-0001 — Repository roles and authority split

- Status: proposed by EAS-C
- Date: 2026-08-18
- Parent: `enterprise_agent_system#6`
- Implementation atom: `enterprise_agent_system#8`

## Decision

Use `enterprise_agent_system` as the cross-repository control plane for source binding, closure graphs, Tech Lead task/prompt routing, aggregate evidence views and Local Handoff epochs.

Keep executable method and product authorities in their existing repositories:

| Repository | Sole authority |
|---|---|
| `ed3c/skills-shared` | portable Tech Lead, Shadow, Git Town and Dual-Agent method laws |
| `ed3c/runtime-env` | secret-free runtime contract wire shapes, transport, identity and host bindings |
| `ed3c/bettor-arena` | durable workflow/reducer/Gate/effect ledger and vertical integration |
| `ed3c/agent-shield-monorepo` | provider, sandbox, API and browser adapters with live receipts |
| `ed3c/truth-verify-loop` | independent verification of receipts, artifacts, effects and user results |
| Human/trusted policy | semantic conflict, egress, irreversible effects, merge, promotion, release and rollback |

## Consequences

1. One interface has one owning repository.
2. This repository stores bindings and evidence references, not copied runtime wire shapes or provider implementations.
3. Google Docs, Google Sheets, vector indexes and shared memory are advisory projections. They cannot commit workflow, task, effect, Human or release state.
4. GitHub issue/PR/UI state is publication metadata, not an evidence lane.
5. Cross-repository state advances only through exact commit/tree/digest subjects and receipts from the required lane.
6. Unavailable physical work becomes a typed Local Handoff item rather than a fabricated `PASS`.

## Rejected alternatives

- A monorepo that copies every Skill, schema, workflow and provider adapter: rejected because it creates duplicate interface/state authorities.
- Google Sheets as the canonical workflow database: rejected because concurrent edits and URL visibility cannot provide exact-subject transaction authority.
- Shared vector memory as the canonical reducer: rejected because a projection cannot establish ordering, idempotency, effect commitment or Human admission.
