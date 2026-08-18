# Molecular Stack index

Derived from observed issues, branches, PR heads, owned paths and dependency contracts. It is not a merge schedule.

| Atom | Class | Observed subject | True/process parents | Owned paths | Required lane | Current state / blocker |
|---|---|---|---|---|---|---|
| `EAS-C` | root | PR #20, head `c4b20fd8594c071cab0324f0988ce954e7cdccc2` | none | `contracts/control-plane/**`, `LICENSE`, ADR 0001 | CLOUD deterministic | draft; exact-head CI/review not admitted |
| `EAS-K` | child | branch `agent/eas-k-tech-lead-core`; issue #9 | true child of EAS-C only if it consumes exact C bytes | `control-plane/router|reducer|leases|state-machines/**`, prompts 00/01 | CLOUD deterministic | branch observed; PR/head/tree/receipt pending |
| `EAS-A` | sibling/process dependent | issue #10 | C vocabulary; no Git parent when path-disjoint | `integrations/**`, projection config/prompt | CLOUD adapter | branch/PR not observed |
| `INCEPTION-C0/C1` | child | PR #21, head `c4af8fc3859a8f8674b55d3b45dfc4ee00037add` | true child of EAS-C | `profiles/agent-thinking-inception/{source,requirements,contracts,examples,tests,prompts 00/01,README,AGENTS}` | CLOUD deterministic | draft; detailed profile contracts incomplete |
| `INCEPTION-K` | child/process consumer | issue #4 | exact profile C1 + exact generic K | profile orchestration/plans/prompts | CLOUD deterministic | blocked on generic K subject and profile review |
| `A1` | owner-routing sibling | issue #5 | profile K process completion | profile owners/compaction; external Bettor/runtime-env subjects | local/live | not implemented/exercised |
| `A2` | owner-routing sibling | issue #7 | profile K process completion | profile owners/runtime; external Agent Shield/runtime-env/Bettor | local/provider | not implemented/exercised |
| `A3` | owner-routing sibling | issue #15 | profile K process completion | profile owners/evidence; external Truth Verify/OpenWiki/Bettor | deterministic/independent | not implemented/exercised |
| `A4` | owner-routing sibling | issue #16 | profile K process completion | profile owners/compliance; external policy/runtime/telemetry | Human + live | not implemented/exercised |
| `A5` | owner-routing sibling | issue #17 | profile K process completion | profile owners/discovery; external candidate/admission | Human Admit | not implemented/exercised |
| `A6` | owner-routing sibling | issue #18 | profile K process completion | profile owners/ingress; external workflow/effects/adapters | live external effect | not implemented/exercised |
| `EAS-E` | child/read-only gate | issue #11 | consumes K candidate contract, not Builder path | `control-plane/gates/**`, `evidence/shadow/**` | independent deterministic | not implemented |
| `INCEPTION-E` | profile read-only gate | issue #19 | consumes profile candidate records | profile shadow/tests/prompt | independent deterministic | not implemented |
| `INCEPTION-X` | convergence | issue #22 | profile K/A1–A6/E exact subjects | profile convergence plans/evidence | mixed exact lanes | issue routed; not executed |
| `EAS-X` | convergence | issue #12 | EAS C/K/A/E + profile X/owner receipts | aggregate plans/closure ledger/integration docs | mixed exact lanes | not executed |
| `INCEPTION-D` | docs convergence | issue #23 | profile X plus admitted profile atoms | profile docs/prompt/Stack packet | CLOUD docs | issue routed; not executed |
| `EAS-D` | final docs convergence | issue #13; branch `agent/eas-d-docs-blueprint` | EAS-X plus admitted C/K/A/E/profile D | root/docs/index/handoff narrative | CLOUD docs | this mutable draft; blocked on X |
| `P7` | Local Handoff | issue #14 | unresolved physical actions after D/X | canonical queue only | local/provider/Human | candidate comment only; queue file absent |

## Stack laws

- required generic atoms are `C/K/A/E/X/D`;
- an atom with no paths, oracle or Gate is ceremonial and blocks;
- true child consumes unmerged parent bytes; process/evidence/Human dependency is not Git ancestry;
- path-disjoint siblings should not be serialized;
- one active writer per branch/worktree/path/resource;
- review-only atom writes nothing, is never a parent and never merges;
- moved subjects require fresh receipts;
- a blocker or unexercised Gate remains on the atom even after publication.
