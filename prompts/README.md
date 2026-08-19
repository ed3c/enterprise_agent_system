# Root prompt catalogue

Complete fresh-session prompts are published under `docs/prompts/`:

```text
P0-source-authority-auditor.system.md
P1-contract-lock-worker.system.md
P2-tech-lead-controller.system.md
P3-owner-wave-worker.system.md
P4-shadow-architect.system.md
P5-convergence-owner.system.md
P6-docs-stack-convergence.system.md
P7-local-handoff-compiler.system.md
```

## Selection law

Choose the prompt matching the owning phase/issue. Do not give one session multiple conflicting roles. Owner-specific P3 sessions additionally consume the exact Profile-K rendered task packet from `profiles/agent-thinking-inception/orchestration/profile-worker-packet-specs.json`.

Current profile packet bundle:

`sha256:dc4473b3195a738e55eb49c43661b6e1f4ea7f95c66749454776f2003b18ebc3`

## Fresh-session law

Every prompt is self-contained and must be paired with exact current repository/commit/tree inputs. No prompt may rely on hidden prior chat memory. If an input moved after the prompt was published, rebind it before execution rather than silently using the mutable branch head.

## Required packet fields

```text
exact inputs and source/profile digests
objective/non-goals/invariants/unknowns
one role + one owner issue
writer/read-only/forbidden paths/resources
start and completion dependencies
input/output contracts
positive and mutation controls
runtime/capability requirements
evidence lane/ceiling
retry/timeout/cleanup/rollback
required receipt
claims_not_proven
stop conditions
next authority
```

## Authority

Prompt text is executable instruction, not evidence. A prompt, generated task packet, model answer, or model agreement cannot create implementation truth, provider capability, Human admission, merge, release or rollback state.

Google Docs may mirror prompt text for review and Google Sheets may index prompt/issue/phase links, but both are `ADVISORY_ONLY`. Canonical prompt bytes/digests and publication history remain in GitHub.