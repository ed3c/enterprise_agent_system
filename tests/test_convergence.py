from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from enterprise_agent_system.convergence import (  # noqa: E402
    ConvergenceContractError,
    validate_convergence_snapshot,
)

LEDGER = ROOT / "evidence" / "ledgers" / "cross-repo-closure.json"
ARCHITECTURE = ROOT / "plans" / "architecture-closure.yaml"
TASK_DAG = ROOT / "plans" / "task-dag.json"
STACK = ROOT / "plans" / "molecular-stack-index.json"


def snapshot() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def must_refuse(case: unittest.TestCase, value: dict, pattern: str) -> None:
    with case.assertRaisesRegex(ConvergenceContractError, pattern):
        validate_convergence_snapshot(value)


class CrossRepoConvergenceTests(unittest.TestCase):
    def test_exact_p4_ledger_validates_without_stronger_lane_promotion(self) -> None:
        value = snapshot()
        validate_convergence_snapshot(value)
        self.assertEqual(value["state"], "P5_CROSS_REPO_CONVERGENCE_CANDIDATE")
        self.assertEqual(len(value["owners"]), 7)
        self.assertEqual(value["selected_vertical_canary"]["state"], "PLAN_ONLY")
        self.assertTrue(all(item["state"] != "PASS" for item in value["stronger_lanes"]))

    def test_missing_owner_cannot_disappear_from_denominator(self) -> None:
        value = snapshot()
        value["owners"] = value["owners"][:-1]
        must_refuse(self, value, "OWNER_INTERFACE_DENOMINATOR")

    def test_duplicate_owner_interface_is_refused(self) -> None:
        value = snapshot()
        value["owners"].append(copy.deepcopy(value["owners"][0]))
        must_refuse(self, value, "DUPLICATE_OWNER_SUBJECT|DUPLICATE_OWNER_INTERFACE")

    def test_runtime_contract_cannot_be_reowned_by_consumer(self) -> None:
        value = snapshot()
        owner = next(item for item in value["owners"] if item["interface"] == "A2R_RUNTIME_CONTRACT")
        owner["repository"] = "ed3c/agent-shield-monorepo"
        owner["subject"]["repository"] = "ed3c/agent-shield-monorepo"
        must_refuse(self, value, "OWNER_REPOSITORY_MISMATCH:A2R_RUNTIME_CONTRACT")

    def test_not_implemented_projection_adapter_cannot_have_fake_subject(self) -> None:
        value = snapshot()
        dep = next(item for item in value["process_dependencies"] if item["atom"] == "EAS-A")
        dep["subject"] = {
            "repository": "ed3c/enterprise_agent_system",
            "commit": "1" * 40,
            "tree": "2" * 40,
        }
        must_refuse(self, value, "NOT_IMPLEMENTED_HAS_SUBJECT:EAS-A")

    def test_process_dependency_cannot_become_false_git_parent(self) -> None:
        value = snapshot()
        value["git_parent"]["atom"] = "EAS-K"
        must_refuse(self, value, "FALSE_GIT_PARENT")

    def test_stronger_lane_public_fixture_credit_is_refused(self) -> None:
        value = snapshot()
        lane = next(item for item in value["stronger_lanes"] if item["lane"] == "PROVIDER_CAPABILITY_ENROLLMENT")
        lane["state"] = "PUBLIC_VERIFIED"
        must_refuse(self, value, "STRONGER_LANE_FALSE_CREDIT:PROVIDER_CAPABILITY_ENROLLMENT")

    def test_stronger_lane_cannot_be_omitted(self) -> None:
        value = snapshot()
        value["stronger_lanes"] = value["stronger_lanes"][:-1]
        must_refuse(self, value, "STRONGER_LANE_DENOMINATOR")

    def test_vertical_canary_plan_cannot_claim_execution(self) -> None:
        value = snapshot()
        value["selected_vertical_canary"]["state"] = "EXECUTED"
        must_refuse(self, value, "VERTICAL_CANARY_FALSE_EXECUTION")

    def test_vertical_canary_cannot_gain_external_effect_authority(self) -> None:
        value = snapshot()
        value["selected_vertical_canary"]["external_effects"] = True
        must_refuse(self, value, "VERTICAL_CANARY_EXTERNAL_EFFECT")

    def test_vertical_canary_cannot_drop_owner_interface(self) -> None:
        value = snapshot()
        value["selected_vertical_canary"]["interfaces"].remove("A2R_RUNTIME_CONTRACT")
        must_refuse(self, value, "VERTICAL_CANARY_INTERFACE_DENOMINATOR")

    def test_two_interfaces_cannot_share_one_exact_subject(self) -> None:
        value = snapshot()
        a1 = next(item for item in value["owners"] if item["interface"] == "A1_COMPACTION_RECOVERY")
        a6 = next(item for item in value["owners"] if item["interface"] == "A6_INGRESS_EFFECTS")
        a6["subject"] = copy.deepcopy(a1["subject"])
        a6["repository"] = a1["repository"]
        must_refuse(self, value, "DUPLICATE_OWNER_SUBJECT|OWNER_REPOSITORY_MISMATCH")

    def test_terminal_convergence_state_is_not_earned_by_graph_consistency(self) -> None:
        value = snapshot()
        value["state"] = "COMPLETE"
        must_refuse(self, value, "CONVERGENCE_STATE_PROMOTION")

    def test_architecture_plan_keeps_vertical_canary_plan_only(self) -> None:
        plan = json.loads(ARCHITECTURE.read_text(encoding="utf-8"))
        self.assertEqual(plan["atom"], "EAS-X")
        self.assertEqual(plan["git_parent"]["atom"], "EAS-E")
        self.assertEqual(plan["selected_vertical_canary"]["state"], "PLAN_ONLY")
        self.assertFalse(plan["selected_vertical_canary"]["private_data"])
        self.assertFalse(plan["selected_vertical_canary"]["external_effects"])
        self.assertEqual(plan["process_dependencies"]["EAS-A"]["state"], "NOT_IMPLEMENTED")

    def test_task_dag_separates_start_completion_and_external_blockers(self) -> None:
        dag = json.loads(TASK_DAG.read_text(encoding="utf-8"))
        node_ids = {node["id"] for node in dag["nodes"]}
        self.assertEqual(len(node_ids), len(dag["nodes"]))
        for edge_class in ("start_edges", "completion_edges"):
            for source, target in dag[edge_class]:
                self.assertIn(source, node_ids)
                self.assertIn(target, node_ids)
        self.assertTrue(set(map(tuple, dag["start_edges"])).issubset(set(map(tuple, dag["completion_edges"]))))
        self.assertEqual(dag["git_ancestry"]["true_parent"], "EAS-E@177ba870c41cc5605532ea79770d54aea124fa0c")
        self.assertIn("EAS-A", dag["git_ancestry"]["process_dependencies_not_git_parents"])
        self.assertEqual(len(dag["external_blocked_edges"]), 1)

    def test_molecular_stack_keeps_missing_a_and_planned_d_visible(self) -> None:
        stack = json.loads(STACK.read_text(encoding="utf-8"))
        self.assertEqual(stack["required_atoms"], ["C", "K", "A", "E", "X", "D"])
        atoms = {item["atom"]: item for item in stack["atoms"]}
        self.assertEqual(set(atoms), {"C", "K", "A", "E", "X", "D"})
        self.assertEqual(atoms["A"]["state"], "NOT_IMPLEMENTED")
        self.assertIsNone(atoms["A"]["subject"])
        self.assertEqual(atoms["X"]["state"], "IN_PROGRESS")
        self.assertIsNone(atoms["X"]["subject"])
        self.assertEqual(atoms["X"]["subject_binding"], "PR_HEAD_READBACK_REQUIRED_AFTER_PUBLICATION")
        self.assertEqual(atoms["D"]["state"], "BLOCKED_BY_EAS_X")
        self.assertIsNone(atoms["D"]["subject"])


if __name__ == "__main__":
    unittest.main()
