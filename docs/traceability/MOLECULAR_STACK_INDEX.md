# Molecular Stack index

Derived from observed issues, branches, PR heads, owned paths and dependency contracts. It is not a merge schedule.

| Atom | Class | Observed subject | True/process parents | Owned paths | Required lane | Current state / blocker |
|---|---|---|---|---|---|---|
| `EAS-C` | root | PR #20, head `c4b20fd8594c071cab0324f0988ce954e7cdccc2`, tree `4b7100176becdc0e06b2dbaa3b06d684518100a8` | none | `contracts/control-plane/**`, `LICENSE`, ADR 0001 | CLOUD deterministic | draft; Shadow blocks consumer admission on exact-subject/start-DAG/nested-shape controls; exact-head execution absent |
| `EAS-K` | true child | PR #24, head `3a0e182f49da1fad624a14b624224dcbe866f402`, tree `2b9c374f9cbe58717c0bab313764f488634ca601` | exact EAS-C head `c4b20f...` | `src/enterprise_agent_system/**`, `tests/test_orchestration.py`, prompts 00/01, plan examples | CLOUD deterministic | draft candidate; becomes stale if C moves; exact-head CI/local receipt absent |
| `EAS-A` | sibling/process dependent | issue #10 | C vocabulary; no Git parent when path-disjoint | `integrations/**`, projection config/prompt | CLOUD adapter | branch/PR not observed |
| `INCEPTION-C0/C1` | true child | PR #21, head `60f994f5f9da55168911d19fb32489775a5f4599` | exact EAS-C head `c4b20f...` | `profiles/agent-thinking-inception/{source,requirements,contracts,examples,tests,prompts 00/01,README,AGENTS}` | CLOUD deterministic | draft; source local-only; exact-head execution absent; detailed profile contracts incomplete |
| `INCEPTION-K` | child/process consumer | issue #4 | admitted profile C1 + admitted generic K, not merely their draft branches | profile orchestration/plans/prompts | CLOUD deterministic | blocked on EAS-C Shadow findings, exact K/profile receipts, and detailed C1 contracts |
| `A1` | owner-routing sibling | issue #5 | profile K process completion | profile owners/compaction; external Bettor/runtime-env subjects | local/live | not implemented/exercised |
| `A2` | owner-routing sibling | issue #7 | profile K process completion | profile owners/runtime; external Agent Shield/runtime-env/Bettor | local/provider | not implemented/exercised |
| `A3` | owner-routing sibling | issue #15 | profile K process completion | profile owners/evidence; external Truth Verify/OpenWiki/Bettor | deterministic/independent | not implemented/exercised |
| `A4` | owner-routing sibling | issue #16 | profile K process completion | profile owners/compliance; external policy/runtime/telemetry | Human + live | not implemented/exercised |
| `A5` | owner-routing sibling | issue #17 | profile K process completion | profile owners/discovery; external candidate/admission | Human Admit | not implemented/exercised |
| `A6` | owner-routing sibling | issue #18 | profile K process completion | profile owners/ingress; external workflow/effects/adapters | live external effect | not implemented/exercised |
| `EAS-E` | true child/read-only gate | PR #25, head `327d9b9efc9b5f913fe3e135083ab9e5c67e303b`, tree `e3a0b2089cf2fac669db91479280d37292b4134b` | exact EAS-K head `3a0e18...`; evaluator path is read-only | `src/enterprise_agent_system/shadow.py`, Shadow tests/evidence/prompt | independent deterministic | draft; verdict `BLOCKED_FOR_CLOSURE`; exact-head CI/local/independent-runtime evidence absent |
| `INCEPTION-E` | profile read-only gate | issue #19 | consumes exact profile candidate records; not a Builder parent | profile shadow/tests/prompt | independent deterministic | not implemented; current ad hoc PR reviews are candidate Shadow receipts only |
| `INCEPTION-X` | convergence | issue #22 | profile K/A1–A6/E exact subjects | profile convergence plans/evidence | mixed exact lanes | issue routed; not executed |
| `EAS-X` | convergence | issue #12 | EAS C/K/A/E + profile X/owner receipts | aggregate plans/closure ledger/integration docs | mixed exact lanes | not executed |
| `INCEPTION-D` | docs convergence | issue #23 | profile X plus admitted profile atoms | profile docs/prompt/Stack packet | CLOUD docs | issue routed; not executed |
| `EAS-D-BLUEPRINT` | synchronized docs candidate | PR #26; profile synchronization merge `869665f5c5fafd556fcc1289668d94ec3f804ce9`; subsequent docs commits on same branch | exact current profile parent `60f994f5f9da55168911d19fb32489775a5f4599`; process-blocked on X | root/docs/index/handoff narrative | CLOUD docs | Git ancestry synchronized (`behind=0`); exact-head docs/link/Stack Gates and machine-readable indexes remain unexercised/not implemented |
| `P7` | Local Handoff | issue #14 | unresolved physical actions after contract/plan convergence | canonical queue only | local/provider/Human | candidate ACTIVE item updated to PR #21 head `60f994...`; queue file absent |

## Stack laws

- required generic atoms are `C/K/A/E/X/D`;
- an atom with no paths, oracle or Gate is ceremonial and blocks;
- true child consumes named unmerged parent bytes; process/evidence/Human dependency is not Git ancestry;
- path-disjoint siblings should not be serialized;
- one active writer per branch/worktree/path/resource;
- review-only atom writes nothing, is never a parent and never merges;
- moved subjects require fresh receipts for affected descendants;
- a blocker or unexercised Gate remains on the atom after publication;
- PR, branch and issue existence are delivery facts, not evidence-state promotion.
