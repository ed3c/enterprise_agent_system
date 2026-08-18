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
    "commit": "ac0a7645392f689ae488328a53e7b6f3bb6ad02d",
    "tree": "51c94cb43ed1e4a3a3ac05e42838532c3ec2e598",
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
            {
                "task_id": "TASK-C",
                "writer_id": "worker-c",
                "paths": ["contracts/control-plane/**"],
                "resources": [],
            },
            {
                "task_id": "TASK-K",
                "writer_id": "worker-k",
                "paths": ["src/enterprise_agent_system/**"],
                "resources": [],
            },
            {
                "task_id": "TASK-A",
                "writer_id": "worker-a",
                "paths": ["integrations/**"],
                "resources": ["google-drive-read"],
            },
            {
                "task_id": "TASK-E",
                "writer_id": "shadow-e",
                "paths": ["evidence/shadow/**"],
                "resources": [],
            },
            {
                "task_id": "TASK-X",
                "writer_id": "worker-x",
                "paths": ["plans/**"],
                "resources": [],
            },
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
            "automation_forbidden": sorted(
                {
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
                }
            ),
            "human_owned": sorted(
                {
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
                }
            ),
        },
        "state": "TASK_DAG_COMPILED",
    }


def make_packet() -> dict:
    return compile_prompt_packet(
        make_run(),
        "TASK-K",
        objective="Implement the deterministic Tech Lead core without widening authority.",
        non_goals=[
            "widen authority",
            "invent live evidence",
            "edit documentation convergence paths",
        ],
        invariants=[
            "contracts precede fan-out",
            "one writer owns each mutation subject",
            "Worker output is candidate evidence",
        ],
        unknowns=[
            "local worktree and provider behavior remain unverified",
            "Human admission and release remain unperformed",
        ],
        read_only_paths=[
            "contracts/control-plane/**",
            "docs/decisions/0001-repository-roles.md",
        ],
        input_contract={
            "parent_contract": "enterprise-agent-system/orchestration-run/v1",
            "parent_commit": SUBJECT["commit"],
            "parent_tree": SUBJECT["tree"],
        },
        acceptance_criteria=[
            "all deterministic gates pass on the exact subject",
            "the persisted packet digest validates after readback",
        ],
        positive_controls=[
            "valid DAG compiles into deterministic waves",
            "one exact-lane candidate can be admitted for convergence",
        ],
        negative_controls=[
            "start-only cycle is refused",
            "overlapping path or resource lease is refused",
            "stale subject and Human promotion are refused",
        ],
        runtime_requirements=[
            "execute only in the CLOUD deterministic lane",
            "persist no credential or session value",
        ],
        capability_requirements=[
            "exact subject readback",
            "Python deterministic gate execution",
        ],
        cleanup_requirements=[
            "report dirty state",
            "report residue inventory",
        ],
        required_gates=[
            "python-compile",
            "unit-tests",
            "mutation-controls",
            "parent-binding",
        ],
        evidence_ceiling=(
            "deterministic candidate; local worktree, provider, Git Town, "
            "Human and release remain NOT_EXERCISED"
        ),
        retry_budget=1,
        timeout_seconds=600,
        next_authority="INDEPENDENT_SHADOW",
    )


class OrchestrationContractTests(unittest.TestCase):
    def test_valid_run_has_separate_deterministic_waves(self) -> None:
        run = make_run()
        validate_run(run)
        expected = [["TASK-C"], ["TASK-A", "TASK-K"], ["TASK-E"], ["TASK-X"]]
        self.assertEqual(
            topological_waves(run, dependency_field="start_dependencies"),
            expected,
        )
        self.assertEqual(
            topological_waves(run, dependency_field="completion_dependencies"),
            expected,
        )

    def test_start_only_cycle_fails_closed(self) -> None:
        run = make_run()
        run["tasks"][0]["start_dependencies"] = ["TASK-K"]
        run["tasks"][1]["start_dependencies"] = ["TASK-C"]
        run["tasks"][0]["completion_dependencies"] = []
        run["tasks"][1]["completion_dependencies"] = []
        with self.assertRaisesRegex(
            ContractError, "CYCLIC_DAG:start_dependencies"
        ):
            validate_run(run)

    def test_completion_edge_cannot_appear_without_start_edge(self) -> None:
        run = make_run()
        run["tasks"][1]["start_dependencies"] = []
        with self.assertRaisesRegex(
            ContractError, "COMPLETION_WITHOUT_START:TASK-K"
        ):
            validate_run(run)

    def test_completion_cycle_fails_closed(self) -> None:
        run = make_run()
        run["tasks"][0]["start_dependencies"] = ["TASK-X"]
        run["tasks"][0]["completion_dependencies"] = ["TASK-X"]
        with self.assertRaisesRegex(
            ContractError, "CYCLIC_DAG:completion_dependencies"
        ):
            topological_waves(
                run, dependency_field="completion_dependencies"
            )

    def test_task_and_lease_paths_must_match(self) -> None:
        run = make_run()
        run["leases"][1]["paths"] = ["src/other/**"]
        with self.assertRaisesRegex(
            ContractError, "TASK_LEASE_PATH_MISMATCH:TASK-K"
        ):
            validate_run(run)

    def test_concurrent_path_and_resource_leases_are_disjoint(self) -> None:
        run = make_run()
        run["tasks"][2]["state"] = "ACTIVE"
        run["tasks"][2]["owns_paths"] = ["src/enterprise_agent_system/adapters/**"]
        run["leases"][2]["paths"] = ["src/enterprise_agent_system/adapters/**"]
        with self.assertRaisesRegex(ContractError, "PATH_LEASE_COLLISION"):
            validate_run(run)

        run = make_run()
        run["tasks"][2]["state"] = "ACTIVE"
        run["leases"][1]["resources"] = ["shared-index"]
        run["leases"][2]["resources"] = ["shared-index"]
        with self.assertRaisesRegex(ContractError, "RESOURCE_LEASE_COLLISION"):
            assert_disjoint_leases(run, ["TASK-K", "TASK-A"])

    def test_unknown_nested_fields_fail_closed(self) -> None:
        run = make_run()
        run["tasks"][0]["extra"] = "not allowed"
        with self.assertRaisesRegex(ContractError, "TASK_0_FIELDS"):
            validate_run(run)

        run = make_run()
        run["leases"][0]["extra"] = "not allowed"
        with self.assertRaisesRegex(ContractError, "LEASE_0_FIELDS"):
            validate_run(run)

    def test_human_authority_denominator_is_complete(self) -> None:
        run = make_run()
        run["authority"]["human_owned"].remove("release")
        with self.assertRaisesRegex(
            ContractError, "HUMAN_AUTHORITY_MISSING:release"
        ):
            validate_run(run)

    def test_prompt_packet_is_full_zero_context_and_content_addressed(self) -> None:
        first = make_packet()
        second = make_packet()
        self.assertEqual(first, second)
        self.assertEqual(first["schema_version"], "enterprise-agent-system/prompt-packet/v2")
        self.assertEqual(first["subject"], SUBJECT)
        self.assertEqual(first["rollback_subject"], SUBJECT)
        self.assertEqual(first["dependencies"]["completion"], ["TASK-C"])
        self.assertEqual(first["runtime"]["required_lane"], "CLOUD")
        self.assertTrue(first["controls"]["positive"])
        self.assertTrue(first["controls"]["negative"])
        self.assertTrue(first["cleanup"]["residue_inventory_required"])
        self.assertTrue(first["required_receipt"]["exact_subject_required"])
        self.assertRegex(first["packet_digest"], r"^sha256:[0-9a-f]{64}$")
        validate_prompt_packet(first)
        markdown = packet_as_markdown(first)
        self.assertIn("Do not rely on prior chat memory", markdown)
        self.assertIn(first["packet_digest"], markdown)

    def test_prompt_packet_unknown_field_fails_closed(self) -> None:
        packet = make_packet()
        packet["canonical_state"] = "COMPLETE"
        packet.pop("packet_digest")
        packet["packet_digest"] = (
            "sha256:"
            + __import__("hashlib").sha256(
                json.dumps(
                    packet,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest()
        )
        with self.assertRaisesRegex(ContractError, "PROMPT_PACKET_FIELDS"):
            validate_prompt_packet(packet)

    def test_prompt_digest_or_authority_mutation_fails_closed(self) -> None:
        packet = make_packet()
        packet["objective"] = "silently changed"
        with self.assertRaisesRegex(ContractError, "PACKET_DIGEST_MISMATCH"):
            validate_prompt_packet(packet)

        packet = make_packet()
        packet["forbidden_actions"].remove("release")
        with self.assertRaisesRegex(
            ContractError, "PROMPT_AUTHORITY_WIDENED:release"
        ):
            validate_prompt_packet(packet)

    def test_prompt_controls_cleanup_and_rollback_cannot_be_hollow(self) -> None:
        packet = make_packet()
        packet["controls"]["negative"] = []
        with self.assertRaisesRegex(ContractError, "PROMPT_NEGATIVE_CONTROLS_EMPTY"):
            validate_prompt_packet(packet)

        packet = make_packet()
        packet["cleanup"]["residue_inventory_required"] = False
        with self.assertRaisesRegex(
            ContractError, "RESIDUE_INVENTORY_NOT_REQUIRED"
        ):
            validate_prompt_packet(packet)

        packet = make_packet()
        packet["rollback_subject"]["commit"] = "0" * 40
        with self.assertRaisesRegex(ContractError, "ROLLBACK_SUBJECT_DRIFT"):
            validate_prompt_packet(packet)

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
        self.assertEqual(
            verdict.state, "CANDIDATE_ADMITTED_FOR_CONVERGENCE"
        )
        self.assertEqual(
            verdict.admitted_candidate_id, "candidate-k-001"
        )

    def test_reducer_preserves_all_refusal_denominators(self) -> None:
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

        wrong_repository = copy.deepcopy(base)
        wrong_repository.update(candidate_id="wrong-repository")
        wrong_repository["subject"]["repository"] = "ed3c/other"

        wrong_lane = copy.deepcopy(base)
        wrong_lane.update(candidate_id="wrong-lane", lane="LOCAL")

        missing_gate = copy.deepcopy(base)
        missing_gate.update(candidate_id="missing-gate", gates=[])

        promotion = copy.deepcopy(base)
        promotion.update(
            candidate_id="promotion",
            claims_human_or_release_state=True,
        )

        verdict = reduce_candidate(
            run,
            task_id="TASK-K",
            candidates=[
                stale,
                wrong_repository,
                wrong_lane,
                missing_gate,
                promotion,
            ],
            required_gates=["unit-tests"],
            required_lane="CLOUD",
        )
        self.assertEqual(verdict.state, "BLOCKED")
        reasons = "\n".join(verdict.reasons)
        self.assertIn("STALE_SUBJECT", reasons)
        self.assertIn("LANE_SUBSTITUTION", reasons)
        self.assertIn("GATES_NOT_PASS", reasons)
        self.assertIn("AUTHORITY_PROMOTION", reasons)

    def test_duplicate_or_malformed_candidate_gate_is_refused(self) -> None:
        candidate = {
            "candidate_id": "candidate-k",
            "task_id": "TASK-K",
            "subject": dict(SUBJECT),
            "lane": "CLOUD",
            "gates": [
                {"id": "unit-tests", "state": "PASS"},
                {"id": "unit-tests", "state": "PASS"},
            ],
            "claims_human_or_release_state": False,
        }
        verdict = reduce_candidate(
            make_run(),
            task_id="TASK-K",
            candidates=[candidate],
            required_gates=["unit-tests"],
            required_lane="CLOUD",
        )
        self.assertEqual(verdict.state, "BLOCKED")
        self.assertIn(
            "candidate-k:MALFORMED_OR_DUPLICATE_GATE",
            verdict.reasons,
        )

    def test_critical_shadow_finding_blocks_and_requires_owner(self) -> None:
        verdict = reduce_candidate(
            make_run(),
            task_id="TASK-K",
            candidates=[],
            required_gates=["unit-tests"],
            required_lane="CLOUD",
            shadow_findings=[
                {
                    "id": "SHADOW-001",
                    "severity": "CRITICAL",
                    "state": "OPEN",
                    "owner_issue": "",
                }
            ],
        )
        self.assertEqual(verdict.state, "BLOCKED_BY_SHADOW")
        self.assertEqual(
            verdict.reasons,
            ("MISSING_OWNER:SHADOW-001",),
        )

    def test_multiple_admissible_candidates_fail_closed(self) -> None:
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
            make_run(),
            task_id="TASK-K",
            candidates=[candidate, other],
            required_gates=["unit-tests"],
            required_lane="CLOUD",
        )
        self.assertEqual(verdict.state, "BLOCKED")
        self.assertIn("MULTIPLE_ADMISSIBLE_CANDIDATES", verdict.reasons)

    def test_candidate_from_another_task_is_not_admitted(self) -> None:
        candidate = {
            "candidate_id": "candidate-wrong-task",
            "task_id": "TASK-A",
            "subject": dict(SUBJECT),
            "lane": "CLOUD",
            "gates": [{"id": "unit-tests", "state": "PASS"}],
            "claims_human_or_release_state": False,
        }
        verdict = reduce_candidate(
            make_run(),
            task_id="TASK-K",
            candidates=[candidate],
            required_gates=["unit-tests"],
            required_lane="CLOUD",
        )
        self.assertEqual(verdict.state, "BLOCKED")
        self.assertIn(
            "candidate-wrong-task:CANDIDATE_TASK_MISMATCH",
            verdict.reasons,
        )

    def test_packet_json_round_trip_is_runtime_object_free(self) -> None:
        packet = make_packet()
        self.assertEqual(packet, json.loads(json.dumps(packet)))


if __name__ == "__main__":
    unittest.main()
