#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "handoff/reduce_receipt.py"
SPEC = importlib.util.spec_from_file_location("eas_h3rr_reducer", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load receipt reducer")
reducer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reducer)


class ReceiptReducerTests(unittest.TestCase):
    def contract(self):
        return reducer.load_json(reducer.CONTRACT_PATH)

    def queue(self):
        return reducer.load_json(reducer.QUEUE_PATH)

    def schema(self):
        return reducer.load_json(reducer.SCHEMA_PATH)

    def item(self):
        return reducer.validate_queue(self.queue())

    def receipt(self):
        commands = [
            {"phase": phase, "command_id": command_id}
            for phase, command_id in reducer.EXPECTED_RECORDS
        ]
        digest = "sha256:" + "0" * 64
        subject = {
            "repository": "ed3c/enterprise_agent_system",
            "commit": reducer.RUNNER_COMMIT,
            "tree": reducer.RUNNER_TREE,
        }
        return {
            "schema_version": reducer.RECEIPT_VERSION,
            "queue_id": reducer.QUEUE_ID,
            "item_id": reducer.ACTIVE_ID,
            "started_at": "2026-08-20T00:00:00Z",
            "finished_at": "2026-08-20T00:00:10Z",
            "subject_before": copy.deepcopy(subject),
            "subject_after": copy.deepcopy(subject),
            "commands": commands,
            "exit_codes": [0] * len(commands),
            "stdout_digests": [digest] * len(commands),
            "stderr_digests": [digest] * len(commands),
            "observed_commit": reducer.ROOT_D_COMMIT,
            "observed_tree": reducer.ROOT_D_TREE,
            "evidence_lane": "LOCAL_DETERMINISTIC",
            "result": "PASS",
            "dirty_state_before": "CLEAN",
            "dirty_state_after": "CLEAN",
            "residue_inventory": {
                "root_d_worktree_exists": False,
                "root_d_worktree_registered": False,
                "temporary_root_d_ref_present": False,
                "checkout_dirty_state": "CLEAN",
            },
            "cleanup_result": "PASS",
            "failures": [],
            "retries": [],
            "claims_not_proven": [
                "This receipt cannot itself advance the queue.",
                "No provider or Human credit is granted.",
            ],
            "next_transition": reducer.SUCCESS_TRANSITION,
        }

    def assert_refused(self, mutate, reason):
        receipt = self.receipt()
        mutate(receipt)
        with self.assertRaisesRegex(reducer.ReducerError, reason):
            reducer.reduce_receipt(receipt, self.schema(), self.item(), source_kind="SYNTHETIC_FIXTURE")

    def test_contract_and_plan_bind_exact_subjects(self):
        contract = self.contract()
        reducer.validate_contract(contract)
        plan = reducer.plan(contract)
        self.assertEqual(plan["runner_subject"]["commit"], reducer.RUNNER_COMMIT)
        self.assertEqual(plan["queue_subject"]["commit"], reducer.QUEUE_COMMIT)
        self.assertEqual(plan["active_item_id"], reducer.ACTIVE_ID)
        self.assertEqual(plan["next_item_id"], reducer.NEXT_ID)
        self.assertEqual(plan["synthetic_fixture_real_local_credit"], 0)
        self.assertTrue(plan["real_local_credit_requires_external_authority"])
        self.assertFalse(plan["queue_mutation_performed"])

    def test_missing_receipt_is_blocked_not_pass(self):
        decision = reducer.reduce_receipt(None, self.schema(), self.item(), source_kind="SYNTHETIC_FIXTURE")
        self.assertEqual(decision["decision"], "BLOCKED_BY_MISSING_REAL_LOCAL_RECEIPT")
        self.assertEqual(decision["receipt_state"], "NOT_EXERCISED")
        self.assertEqual(decision["real_local_evidence_credit"], 0)
        self.assertFalse(decision["canonical_advancement_performed"])

    def test_valid_synthetic_pass_is_only_semantic_candidate(self):
        decision = reducer.reduce_receipt(self.receipt(), self.schema(), self.item(), source_kind="SYNTHETIC_FIXTURE")
        self.assertEqual(decision["decision"], "NEXT_EPOCH_CANDIDATE_READY")
        self.assertTrue(decision["receipt_semantics_admitted"])
        self.assertEqual(decision["real_local_evidence_credit"], 0)
        self.assertFalse(decision["queue_mutation_performed"])
        self.assertFalse(decision["canonical_advancement_performed"])
        self.assertEqual(decision["stronger_lane_credit"], [])

    def test_real_label_cannot_self_grant_local_credit(self):
        decision = reducer.reduce_receipt(self.receipt(), self.schema(), self.item(), source_kind="REAL_LOCAL_RECEIPT")
        self.assertEqual(decision["decision"], "NEXT_EPOCH_CANDIDATE_READY")
        self.assertEqual(decision["real_local_evidence_credit"], 0)
        self.assertTrue(decision["receipt_semantics_admitted"])

    def test_nonpass_receipt_stays_blocked(self):
        receipt = self.receipt()
        receipt["result"] = "FAIL"
        receipt["cleanup_result"] = "FAIL"
        receipt["failures"] = [{"kind": "fixture"}]
        receipt["next_transition"] = "BLOCKED_WITH_EXACT_LOCAL_RECEIPT"
        decision = reducer.reduce_receipt(receipt, self.schema(), self.item(), source_kind="SYNTHETIC_FIXTURE")
        self.assertEqual(decision["decision"], "BLOCKED_BY_LOCAL_RECEIPT_RESULT")
        self.assertEqual(decision["real_local_evidence_credit"], 0)
        self.assertFalse(decision["receipt_semantics_admitted"])

    def test_wrong_queue_is_refused(self):
        self.assert_refused(lambda r: r.__setitem__("queue_id", "old"), "RECEIPT_QUEUE_ITEM")

    def test_wrong_item_is_refused(self):
        self.assert_refused(lambda r: r.__setitem__("item_id", "other"), "RECEIPT_QUEUE_ITEM")

    def test_wrong_lane_is_refused(self):
        self.assert_refused(lambda r: r.__setitem__("evidence_lane", "LIVE_PROVIDER"), "RECEIPT_EVIDENCE_LANE")

    def test_wrong_runner_before_is_refused(self):
        self.assert_refused(lambda r: r["subject_before"].__setitem__("commit", "1" * 40), "WRONG_RUNNER_SUBJECT_BEFORE")

    def test_wrong_runner_after_is_refused(self):
        self.assert_refused(lambda r: r["subject_after"].__setitem__("tree", "2" * 40), "WRONG_RUNNER_SUBJECT_AFTER")

    def test_wrong_root_d_observation_is_refused(self):
        self.assert_refused(lambda r: r.__setitem__("observed_commit", "3" * 40), "PASS_WITHOUT_EXACT_ROOT_D")

    def test_missing_command_is_refused(self):
        def mutate(r):
            r["commands"].pop()
            r["exit_codes"].pop()
            r["stdout_digests"].pop()
            r["stderr_digests"].pop()
        self.assert_refused(mutate, "PASS_COMMAND_DENOMINATOR")

    def test_wrong_command_order_is_refused(self):
        self.assert_refused(lambda r: r["commands"].reverse(), "PASS_COMMAND_DENOMINATOR")

    def test_nonzero_exit_is_refused_for_pass(self):
        self.assert_refused(lambda r: r["exit_codes"].__setitem__(0, 7), "PASS_NONZERO_EXIT")

    def test_cleanup_fail_is_refused_for_pass(self):
        self.assert_refused(lambda r: r.__setitem__("cleanup_result", "FAIL"), "PASS_WITHOUT_CLEANUP")

    def test_dirty_state_is_refused_for_pass(self):
        self.assert_refused(lambda r: r.__setitem__("dirty_state_after", "DIRTY:sha256:" + "1" * 64), "DIRTY_STATE")

    def test_residue_is_refused_for_pass(self):
        self.assert_refused(lambda r: r["residue_inventory"].__setitem__("temporary_root_d_ref_present", True), "TEMP_REF_RESIDUE")

    def test_failures_are_refused_for_pass(self):
        self.assert_refused(lambda r: r.__setitem__("failures", [{"kind": "hidden"}]), "PASS_WITH_FAILURES")

    def test_wrong_success_transition_is_refused(self):
        self.assert_refused(lambda r: r.__setitem__("next_transition", "AUTO_ADVANCE"), "PASS_NEXT_TRANSITION")

    def test_private_path_leak_is_refused(self):
        self.assert_refused(lambda r: r["commands"][0].__setitem__("debug", "/home/alice/private"), "PORTABLE_PRIVATE_PATH_LEAK")

    def test_secret_like_value_is_refused(self):
        self.assert_refused(lambda r: r["commands"][0].__setitem__("debug", "api_key=supersecret"), "PORTABLE_SECRET_LIKE_VALUE")

    def test_effect_promotion_is_refused(self):
        self.assert_refused(lambda r: r.__setitem__("effect_state", "COMMITTED"), "LOCAL_RECEIPT_EFFECT_PROMOTION")

    def test_unknown_field_is_refused(self):
        self.assert_refused(lambda r: r.__setitem__("canonical_pass", True), "RECEIPT_UNKNOWN_FIELD")

    def test_bad_digest_is_refused(self):
        self.assert_refused(lambda r: r["stdout_digests"].__setitem__(0, "not-a-digest"), "DIGEST_FORMAT")

    def test_queue_v2_is_refused(self):
        queue = self.queue()
        queue["schema_version"] = "enterprise-agent-system/local-handoff-queue/v2"
        with self.assertRaisesRegex(reducer.ReducerError, "QUEUE_SCHEMA"):
            reducer.validate_queue(queue)

    def test_contract_cannot_enable_queue_mutation(self):
        contract = self.contract()
        contract["reducer_laws"]["queue_mutation"] = True
        with self.assertRaisesRegex(reducer.ReducerError, "QUEUE_MUTATION_LAUNDERING"):
            reducer.validate_contract(contract)

    def test_cli_missing_receipt_path_returns_blocked(self):
        with tempfile.TemporaryDirectory() as root_dir:
            missing = pathlib.Path(root_dir) / "missing.json"
            self.assertEqual(reducer.main(["--mode", "inspect", "--receipt", str(missing)]), 4)


if __name__ == "__main__":
    unittest.main()
