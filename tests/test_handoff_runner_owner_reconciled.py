#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "handoff/run_active_owner_reconciled.py"
SPEC = importlib.util.spec_from_file_location("owner_reconciled_runner", MODULE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load owner-reconciled runner")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class OwnerReconciledRunnerTests(unittest.TestCase):
    def queue(self):
        return runner.load_json(runner.QUEUE_PATH)

    def contract(self):
        return runner.load_json(runner.CONTRACT_PATH)

    def test_contract_binds_exact_reconciled_queue(self):
        contract = self.contract()
        runner.validate_runner_contract(contract)
        subject = contract["queue_subject"]
        self.assertEqual(subject["pull_request"], 114)
        self.assertEqual(subject["commit"], runner.QUEUE_PARENT_COMMIT)
        self.assertEqual(subject["tree"], runner.QUEUE_PARENT_TREE)
        self.assertEqual(subject["verification_run"], runner.QUEUE_PARENT_VERIFY)
        self.assertEqual(subject["shadow_review"], runner.QUEUE_PARENT_SHADOW)
        self.assertEqual(subject["relationship"], "TRUE_GIT_PARENT")

    def test_plan_preserves_no_execution_and_owner_route(self):
        plan = runner.build_plan(self.queue(), self.contract())
        self.assertEqual(plan["schema_version"], "enterprise-agent-system/local-handoff-runner-plan/v4")
        self.assertEqual(plan["vertical_canary_owner_issue"], 14)
        self.assertEqual(plan["closed_p5_issue_22_execution_authority"], "NONE")
        self.assertEqual(plan["pre_reconciliation_queue_authority"], "NONE")
        self.assertEqual(plan["pre_reconciliation_runner_authority"], "NONE")
        self.assertEqual(plan["queue_execution"], "NOT_PERFORMED")
        self.assertEqual(plan["runner_execution"], "NOT_PERFORMED")
        self.assertEqual(plan["canonical_advancement"], "NOT_PERFORMED")
        self.assertEqual(len(plan["command_ids"]), 9)
        self.assertEqual(len(plan["cleanup_ids"]), 3)
        encoded = json.dumps(plan, sort_keys=True)
        self.assertNotIn("/Users/", encoded)
        self.assertNotIn("/home/", encoded)
        self.assertNotIn("/mnt/data/", encoded)

    def test_exact_owner_map_is_required(self):
        queue = self.queue()
        items = {row["item_id"]: row for row in queue["items"]}
        self.assertTrue(items["LH-P7-09-VERTICAL-CANARY"]["owner_issue"].endswith("/issues/14"))
        runner.validate_queue(queue)
        items["LH-P7-09-VERTICAL-CANARY"]["owner_issue"] = "https://github.com/ed3c/enterprise_agent_system/issues/22"
        with self.assertRaisesRegex(runner.RunnerError, "OWNER_ROUTE_DRIFT"):
            runner.validate_queue(queue)

    def test_pre_reconciliation_subjects_have_no_authority(self):
        contract = self.contract()
        previous = contract["pre_reconciliation_authority"]
        self.assertEqual([row["pull_request"] for row in previous], [99, 103])
        self.assertTrue(all(row["authority"] == "NONE" for row in previous))
        previous[1]["authority"] = "CURRENT"
        with self.assertRaisesRegex(runner.RunnerError, "PRE_RECONCILIATION_AUTHORITY"):
            runner.validate_runner_contract(contract)

    def test_old_queue_subject_is_refused(self):
        contract = self.contract()
        contract["queue_subject"]["commit"] = runner.PRE_RECONCILIATION_QUEUE
        with self.assertRaisesRegex(runner.RunnerError, "QUEUE_PARENT_DRIFT"):
            runner.validate_runner_contract(contract)

    def test_reused_binding_cannot_gain_execution_authority(self):
        contract = self.contract()
        contract["binding_reuse"]["execution_authority"] = "CURRENT"
        with self.assertRaisesRegex(runner.RunnerError, "BINDING_REUSE_AUTHORITY"):
            runner.validate_runner_contract(contract)

    def test_eas_a_and_google_cannot_promote(self):
        contract = self.contract()
        contract["eas_a"]["authority"] = "CANONICAL"
        with self.assertRaisesRegex(runner.RunnerError, "EAS_A_AUTHORITY"):
            runner.validate_runner_contract(contract)
        contract = self.contract()
        contract["eas_a"]["google_write"] = "PASS"
        with self.assertRaisesRegex(runner.RunnerError, "GOOGLE_PROMOTION"):
            runner.validate_runner_contract(contract)

    def test_execute_still_requires_explicit_external_runner_subject(self):
        with self.assertRaisesRegex(runner.RunnerError, "EXECUTE_REQUIRES_ADMITTED_RUNNER_SUBJECT"):
            runner.main(["--mode", "execute", "--runtime-kind", "CODEX_CLI_LOCAL"])


if __name__ == "__main__":
    unittest.main()
