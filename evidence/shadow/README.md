# Shadow evidence

This directory contains read-only evaluations over exact public subjects. A Shadow verdict can block closure or admit a candidate for review. It cannot mutate Builder bytes, commit canonical task/effect/Human/release state, close issues, merge, promote, release or roll back.

## Persisted reviews

- `control-plane-preflight-review.json` binds the current EAS-C and EAS-K deterministic subjects. Its expected verdict is `ADMIT_FOR_REVIEW`: the contract, task-DAG, prompt-packet, reducer, parent-binding and lease mechanisms have exact GitHub subjects and deterministic receipts, while no runtime, provider, Human or release claim is made.
- `dual-agent-closure-review.json` evaluates the full PDF architecture denominator. Its expected verdict remains `BLOCKED_FOR_CLOSURE`: runtime contracts, disconnect/reconnect, identity, durable workflow/effects, provider isolation, independent verification, profile contracts/DAG, physical user outcome and Human/release lanes remain open.

`tests/test_shadow_snapshots.py` validates both persisted snapshots, recomputes their content digests and asserts the expected verdicts. `.github/workflows/eas-e-shadow-gates.yml` executes the inherited EAS-C/K gates plus the Shadow controls on the exact GitHub workflow subject. A green workflow proves only these deterministic evaluators; it does not close any local, provider, effect, user, Human or release lane.
