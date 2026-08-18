from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from enterprise_agent_system.orchestration import (  # noqa: E402
    ContractError,
    assert_disjoint_leases,
    compile_prompt_packet,
    packet_as_markdown,
    reduce_candidate,
    topological_waves,
    validate_prompt_packet,
    validate_run,
)

SUBJECT = {
    "repository": "ed3c/enterprise_agent_system",
    "commit": "c4b20fd8594c071cab0324f0988ce954e7cdccc2",
    "tree": "4b7100176becdc0e06b2dbaa3b06d684518100a8",
}


def make_run() -> dict:
    return {
        "schema_version": "enterprise-agent-system/orchestration-run/v1",
        "run_id": "RUN-EAS-K-TEST",
        "request_subject": dict(SUBJECT),
        "tasks": [
            {
                "id": "TASK-C",
                "start_dependencies": [],
                "completion_dependencies": [],
                "owns_paths": ["contracts/control-plane/**"],
                "required_lane": "CLOUD",
                "output_contract": "EAS-C contracts",
                "state": "VERIFIED",
            },
            {
                "id": "TASK-K",
                "start_dependencies": ["TASK-C"],
                "completion_dependencies": ["TASK-C"],
                "owns_paths": ["src/enterprise_agent_system/**"],
                "required_lane": "CLOUD",
                "output_contract": "Tech Lead core receipt",
                "state": "ACTIVE",
            },
            {
                "id": "TASK-A",
                "start_dependencies": ["TASK-C"],
                "completion_dependencies": ["TASK-C"],
                "owns_paths": ["integrations/**"],
                "required_lane": "CLOUD",
                "output_contract": "projection adapter receipt",
                "state": "PLANNED",
            },
            {
                "id": "TASK-E",
                "start_dependencies": ["TASK-K"],
                "completion_dependencies": ["TASK-K"],
                "owns_paths": ["evidence/shadow/**"],
                "required_lane": "CLOUD",
                "output_contract": "Shadow receipt",
                "state": "PLANNED",
            },
            {
                "id": "TASK-X",
                "start_dependencies": ["TASK-A", "TASK-E"],
                "completion_dependencies": ["TASK-A", "TASK-E"],
                "owns_paths": ["plans/**"],
                "required_lane": "CLOUD",
                "output_contract": "cross-repository closure graph",
                "state": "PLANNED",
            },
        ],
        "leases": [
            {"task_id": "TASK-C", "writer_id": "worker-c", "paths": ["contracts/control-plane/**"], "resources": []},
            {"task_id": "TASK-K", "writer_id": "worker-k", "paths": ["src/enterprise_agent_system/**"], "resources": []},
            {"task_id": "TASK-A", "writer_id": "worker-a", "paths": ["integrations/**"], "resources": ["google-drive-read"]},
            {"task_id": "TASK-E", "writer_id": "shadow-e", "paths": ["evidence/shadow/**"], "resources": []},
            {"task_id": "TASK-X", "writer_id": "worker-x", "paths": ["plans/**"], "resources": []},
        ],
        "canonical_reducer": {
            "owner": "enterprise-agent-system/control-plane/reducer",
            "may_commit": ["TASK_STATE"],
        },
        "shadow": {
            "read_only": True,
            "separate_evaluation_path": True,
            "may_commit": [],
        },
        "authority": {
            "automation_forbidden": [
                "merge",
                "issue_close",
                "permission_change",
                "visibility_change",
                "semantic_conflict_resolution",
                "data_egress",
                "irreversible_effect",
                "promotion",
                "release",
                "rollback",
            ],
            "human_owned": [
                "merge",
                "data_egress",
                "irreversible_effect",
                "release",
                "rollback",
            ],
        },
        "state": "TASK_DAG_COMPILED",
    }


class OrchestrationContractTests(unittest.TestCase):
    def test_valid_run_and_deterministic_parallel_waves(self) -> None:
        run = make_run()
        validate_run(run)
        self.assertEqual(
            topological_waves(run),
            [["TASK-C"], ["TASK-A", "TASK-K"], ["TASK-E"], ["TASK-X"]],
        )

    def test_prompt_packet_is_zero_context_and_content_addressed(self) -> None:
        run = make_run()
        kwargs = {
            "objective": "Implement the deterministic Tech Lead core without widening authority.",
            "invariants": [
                "contracts precede fan-out",
                "one writer owns each mutation subject",
                "Worker output is candidate evidence",
            ],
            "read_only_paths": ["contracts/control-plane/**"],
            "required_gates": ["unit-tests", "mutation-controls"],
            "evidence_ceiling": "deterministic exact-subject candidate only",
            "retry_budget": 1,
        }
        first = compile_prompt_packet(run, "TASK-K", **kwargs)
        second = compile_prompt_packet(run, "TASK-K", **kwargs)
        self.assertEqual(first, second)
        self.assertRegex(first["packet_digest"], r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(first["subject"], SUBJECT)
        self.assertEqual(first["leases"]["write_paths"], ["src/enterprise_agent_system/**"])
        self.assertEqual(first["dependencies"]["completion"], ["TASK-C"])
        self.assertIn("merge", first["forbidden_actions"])
        self.assertEqual(first["handoff"]["on_unavailable_capability"], "LOCAL_HANDOFF_REQUIRED")
        validate_prompt_packet(first)
        markdown = packet_as_markdown(first)
        self.assertIn("Do not rely on prior chat memory", markdown)
        self.assertIn(first["packet_digest"], markdown)

    def test_completion_edge_cannot_appear_without_start_edge(self) -> None:
        run = make_run()
        run["tasks"][1]["start_dependencies"] = []
        with self.assertRaisesRegex(ContractError, "COMPLETION_WITHOUT_START:TASK-K"):
            validate_run(run)

    def test_cycle_fails_closed(self) -> None:
        run = make_run()
        run["tasks"][0]["start_dependencies"] = ["TASK-X"]
        run["tasks"][0]["completion_dependencies"] = ["TASK-X"]
        with self.assertRaisesRegex(ContractError, "CYCLIC_DAG"):
            validate_run(run)

    def test_concurrent_path_and_resource_leases_must_be_disjoint(self) -> None:
        run = make_run()
        run["tasks"][2]["state"] = "ACTIVE"
        run["leases"][2]["paths"] = ["src/enterprise_agent_system/adapters/**"]
        with self.assertRaisesRegex(ContractError, "PATH_LEASE_COLLISION"):
            validate_run(run)

        run = make_run()
        run["tasks"][2]["state"] = "ACTIVE"
        run["leases"][1]["resources"] = ["shared-index"]
        run["leases"][2]["resources"] = ["shared-index"]
        with self.assertRaisesRegex(ContractError, "RESOURCE_LEASE_COLLISION"):
            assert_disjoint_leases(run, ["TASK-K", "TASK-A"])

    def test_reducer_admits_exactly_one_exact_lane_candidate(self) -> None:
        run = make_run()
        candidate = {
            "candidate_id": "candidate-k-001",
            "task_id": "TASK-K",
            "subject": dict(SUBJECT),
            "lane": "CLOUD",
            "gates": [
                {"id": "unit-tests", "state": "PASS"},
                {"id": "mutation-controls", "state": "PASS"},
            ],
            "claims_human_or_release_state": False,
        }
        verdict = reduce_candidate(
            run,
            task_id="TASK-K",
            candidates=[candidate],
            required_gates=["unit-tests", "mutation-controls"],
            required_lane="CLOUD",
        )
        self.assertEqual(verdict.state, "CANDIDATE_ADMITTED_FOR_CONVERGENCE")
        self.assertEqual(verdict.admitted_candidate_id, "candidate-k-001")

    def test_reducer_preserves_stale_lane_gate_and_authority_refusals(self) -> None:
        run = make_run()
        base = {
            "task_id": "TASK-K",
            "subject": dict(SUBJECT),
            "lane": "CLOUD",
            "gates": [{"id": "unit-tests", "state": "PASS"}],
            "claims_human_or_release_state": False,
        }
        stale = copy.deepcopy(base)
        stale.update(candidate_id="stale")
        stale["subject"]["commit"] = "0" * 40
        wrong_lane = copy.deepcopy(base)
        wrong_lane.update(candidate_id="wrong-lane", lane="LOCAL")
        missing_gate = copy.deepcopy(base)
        missing_gate.update(candidate_id="missing-gate", gates=[])
        promotion = copy.deepcopy(base)
        promotion.update(candidate_id="promotion", claims_human_or_release_state=True)

        verdict = reduce_candidate(
            run,
            task_id="TASK-K",
            candidates=[stale, wrong_lane, missing_gate, promotion],
            required_gates=["unit-tests"],
            required_lane="CLOUD",
        )
        self.assertEqual(verdict.state, "BLOCKED")
        reason_text = "\n".join(verdict.reasons)
        self.assertIn("STALE_SUBJECT", reason_text)
        self.assertIn("LANE_SUBSTITUTION", reason_text)
        self.assertIn("GATES_NOT_PASS", reason_text)
        self.assertIn("AUTHORITY_PROMOTION", reason_text)

    def test_critical_shadow_finding_blocks_and_requires_owner(self) -> None:
        run = make_run()
        verdict = reduce_candidate(
            run,
            task_id="TASK-K",
            candidates=[],
            required_gates=["unit-tests"],
            required_lane="CLOUD",
            shadow_findings=[
                {
                    "id": "SHADOW-001",
                    "severity": "CRITICAL",
                    "state": "OPEN",
                    "owner_issue": "https://github.com/ed3c/enterprise_agent_system/issues/11",
                }
            ],
        )
        self.assertEqual(verdict.state, "BLOCKED_BY_SHADOW")
        self.assertEqual(
            verdict.reasons,
            ("https://github.com/ed3c/enterprise_agent_system/issues/11",),
        )

    def test_multiple_admissible_candidates_fail_closed(self) -> None:
        run = make_run()
        candidate = {
            "candidate_id": "candidate-a",
            "task_id": "TASK-K",
            "subject": dict(SUBJECT),
            "lane": "CLOUD",
            "gates": [{"id": "unit-tests", "state": "PASS"}],
            "claims_human_or_release_state": False,
        }
        other = copy.deepcopy(candidate)
        other["candidate_id"] = "candidate-b"
        verdict = reduce_candidate(
            run,
            task_id="TASK-K",
            candidates=[candidate, other],
            required_gates=["unit-tests"],
            required_lane="CLOUD",
        )
        self.assertEqual(verdict.state, "BLOCKED")
        self.assertIn("MULTIPLE_ADMISSIBLE_CANDIDATES", verdict.reasons)


    def test_prompt_digest_or_authority_mutation_fails_closed(self) -> None:
        packet = compile_prompt_packet(
            make_run(),
            "TASK-K",
            objective="Compile one task packet.",
            invariants=["exact subject"],
            required_gates=["unit-tests"],
            evidence_ceiling="deterministic",
        )
        packet["objective"] = "silently changed"
        with self.assertRaisesRegex(ContractError, "PACKET_DIGEST_MISMATCH"):
            validate_prompt_packet(packet)

        packet = compile_prompt_packet(
            make_run(),
            "TASK-K",
            objective="Compile one task packet.",
            invariants=["exact subject"],
            required_gates=["unit-tests"],
            evidence_ceiling="deterministic",
        )
        packet["forbidden_actions"].remove("release")
        with self.assertRaisesRegex(ContractError, "PROMPT_AUTHORITY_WIDENED:release"):
            validate_prompt_packet(packet)

    def test_candidate_from_another_task_is_not_admitted(self) -> None:
        run = make_run()
        candidate = {
            "candidate_id": "candidate-wrong-task",
            "task_id": "TASK-A",
            "subject": dict(SUBJECT),
            "lane": "CLOUD",
            "gates": [{"id": "unit-tests", "state": "PASS"}],
            "claims_human_or_release_state": False,
        }
        verdict = reduce_candidate(
            run,
            task_id="TASK-K",
            candidates=[candidate],
            required_gates=["unit-tests"],
            required_lane="CLOUD",
        )
        self.assertEqual(verdict.state, "BLOCKED")
        self.assertIn("candidate-wrong-task:CANDIDATE_TASK_MISMATCH", verdict.reasons)

    def test_packet_json_round_trip_does_not_depend_on_runtime_objects(self) -> None:
        packet = compile_prompt_packet(
            make_run(),
            "TASK-K",
            objective="Compile one task packet.",
            invariants=["exact subject"],
            required_gates=["unit-tests"],
            evidence_ceiling="deterministic",
        )
        self.assertEqual(packet, json.loads(json.dumps(packet)))


if __name__ == "__main__":
    unittest.main()
