#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE = ROOT / "handoff/reduce_receipt_owner_reconciled.py"
SPEC = importlib.util.spec_from_file_location("owner_reconciled_reducer", MODULE)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load owner-reconciled reducer")
reducer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reducer)


class OwnerReconciledReducerTests(unittest.TestCase):
    def contract(self):
        return reducer.load_json(reducer.CONTRACT_PATH)

    def queue(self):
        return reducer.load_json(reducer.QUEUE_PATH)

    def test_contract_binds_exact_queue_and_h5r(self):
        contract = self.contract()
        reducer.validate_contract(contract)
        self.assertEqual(contract["queue_subject"]["pull_request"], 114)
        self.assertEqual(contract["queue_subject"]["commit"], reducer.QUEUE_COMMIT)
        self.assertEqual(contract["queue_subject"]["tree"], reducer.QUEUE_TREE)
        self.assertEqual(contract["runner_subject"]["pull_request"], 116)
        self.assertEqual(contract["runner_subject"]["commit"], reducer.RUNNER_COMMIT)
        self.assertEqual(contract["runner_subject"]["tree"], reducer.RUNNER_TREE)
        self.assertEqual(contract["runner_subject"]["relationship"], "TRUE_GIT_PARENT")

    def test_plan_preserves_missing_receipt_and_zero_credit(self):
        p = reducer.plan(self.contract())
        self.assertEqual(p["schema_version"], "enterprise-agent-system/local-receipt-reducer-plan/v3")
        self.assertEqual(p["missing_receipt_decision"], "BLOCKED_BY_MISSING_REAL_LOCAL_RECEIPT")
        self.assertEqual(p["synthetic_fixture_real_local_credit"], 0)
        self.assertEqual(p["real_label_real_local_credit"], 0)
        self.assertEqual(p["vertical_canary_owner_issue"], 14)
        self.assertEqual(p["closed_p5_issue_22_execution_authority"], "NONE")
        self.assertFalse(p["queue_mutation_performed"])
        self.assertFalse(p["canonical_advancement_performed"])
        self.assertEqual(p["real_local_receipt"], "NOT_OBSERVED")

    def test_exact_owner_routes_are_required(self):
        queue = self.queue()
        reducer.validate_queue(queue)
        target = next(row for row in queue["items"] if row["item_id"] == "LH-P7-09-VERTICAL-CANARY")
        self.assertTrue(target["owner_issue"].endswith("/issues/14"))
        target["owner_issue"] = "https://github.com/ed3c/enterprise_agent_system/issues/22"
        with self.assertRaisesRegex(reducer.ReducerError, "OWNER_ROUTE_DRIFT"):
            reducer.validate_queue(queue)

    def test_pre_reconciliation_subjects_have_no_authority(self):
        contract = self.contract()
        previous = contract["pre_reconciliation_authority"]
        self.assertEqual([row["pull_request"] for row in previous], [99, 103, 107])
        self.assertTrue(all(row["authority"] == "NONE" for row in previous))
        previous[2]["authority"] = "CURRENT"
        with self.assertRaisesRegex(reducer.ReducerError, "PRE_RECONCILIATION_AUTHORITY"):
            reducer.validate_contract(contract)

    def test_old_runner_and_reducer_subjects_are_refused(self):
        contract = self.contract()
        contract["runner_subject"]["commit"] = reducer.PRE_RUNNER
        with self.assertRaisesRegex(reducer.ReducerError, "RUNNER_SUBJECT_DRIFT"):
            reducer.validate_contract(contract)
        contract = self.contract()
        contract["binding_reuse"]["canonical_advancement_authority"] = "CURRENT"
        with self.assertRaisesRegex(reducer.ReducerError, "BINDING_REUSE_AUTHORITY"):
            reducer.validate_contract(contract)

    def test_missing_receipt_stays_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            missing = pathlib.Path(temp) / "missing.json"
            rc = reducer.main(["--mode", "inspect", "--receipt", str(missing)])
            self.assertEqual(rc, 4)

    def test_eas_a_and_public_verification_cannot_promote(self):
        contract = self.contract()
        contract["eas_a"]["authority"] = "CANONICAL"
        with self.assertRaisesRegex(reducer.ReducerError, "EAS_A_AUTHORITY"):
            reducer.validate_contract(contract)
        contract = self.contract()
        contract["public_verification"]["real_local_credit_grant_allowed"] = True
        with self.assertRaisesRegex(reducer.ReducerError, "REAL_LOCAL_CREDIT"):
            reducer.validate_contract(contract)

    def test_plan_contains_no_local_path_values(self):
        encoded = json.dumps(reducer.plan(self.contract()), sort_keys=True)
        self.assertNotIn("/Users/", encoded)
        self.assertNotIn("/home/", encoded)
        self.assertNotIn("/mnt/data/", encoded)


if __name__ == "__main__":
    unittest.main()
