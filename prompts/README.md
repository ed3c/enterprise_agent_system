# Phase prompt catalogue

Each file is a zero-context system prompt template for a fresh ChatGPT/Codex/Claude session. The controller must replace all `<PLACEHOLDER>` values with exact immutable subjects before dispatch. Prompt text is not execution; a session result is a candidate until independent readback and Gates.

| Phase | Prompt | Output |
|---|---|---|
| P0 | `00-source-authority-auditor.system.md` | source/requirement/contradiction graph |
| P1 | `01-contract-lock-worker.system.md` | strict contracts, examples and mutation controls |
| P2 | `02-tech-lead-controller.system.md` | DAGs, prompts, leases, expected receipts |
| P3 | `03-owner-wave-worker.system.md` | one A-lane owner packet/implementation candidate |
| P4 | `04-shadow-architect.system.md` | read-only applicability/evidence/global-objective verdict |
| P5 | `05-convergence-owner.system.md` | exact-subject closure graph and canary selection |
| P6 | `06-docs-stack-convergence.system.md` | root/profile routes, diagrams and Stack index |
| P7 | `07-local-handoff-compiler.system.md` | concrete queue item and receipt/cleanup contract |

## Required packet fields

```text
packet ID and content digest
exact repository/commit/tree and source/profile digests
role, issue, atom, objective and global denominator
non-goals, invariants and unresolved unknowns
writable/read-only/forbidden paths and resources
start and completion dependencies
input/output schemas
positive and mutation/disagreement controls
runtime/capability/evidence requirements
retry/budget/timeout/retention/cleanup/rollback limits
receipt, claims not proven, stop conditions and next authority
```
