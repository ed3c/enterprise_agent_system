#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "handoff/reduce_receipt.py"
SPEC = importlib.util.spec_from_file_location("eas_h4rr_reducer", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load H4RR reducer")
reducer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reducer)


class H4RRCurrentEpochTests(unittest.TestCase):
    def contract(self):
        return reducer.load_json(reducer.CONTRACT_PATH)

    def queue(self):
        return reducer.load_json(reducer.QUEUE_PATH)

    def test_contract_binds_current_queue_runner_and_zero_credit_plan(self):
        contract = self.contract()
        reducer.validate_contract(contract)
        plan = reducer.plan(contract)
        self.assertEqual(plan["queue_subject"]["commit"], reducer.QUEUE_COMMIT)
        self.assertEqual(plan["runner_subject"]["commit"], reducer.RUNNER_COMMIT)
        self.assertEqual(plan["active_item_id"], reducer.ACTIVE_ID)
        self.assertEqual(plan["real_label_real_local_credit"], 0)
        self.assertEqual(plan["synthetic_fixture_real_local_credit"], 0)
        self.assertEqual(plan["queue_execution"], "NOT_PERFORMED")
        self.assertEqual(plan["active_execution"], "NOT_PERFORMED")
        self.assertEqual(plan["real_local_receipt"], "NOT_OBSERVED")
        self.assertFalse(plan["canonical_advancement_performed"])

    def test_eas_a_canonical_or_git_parent_is_refused(self):
        contract = self.contract(); contract["eas_a"]["authority"] = "CANONICAL"
        with self.assertRaisesRegex(reducer.ReducerError, "EAS_A_AUTHORITY"):
            reducer.validate_contract(contract)
        contract = self.contract(); contract["eas_a"]["relationship"] = "GIT_PARENT"
        with self.assertRaisesRegex(reducer.ReducerError, "EAS_A_AUTHORITY"):
            reducer.validate_contract(contract)

    def test_google_or_source_correctness_promotion_is_refused(self):
        contract = self.contract(); contract["eas_a"]["google_write"] = "PASS"
        with self.assertRaisesRegex(reducer.ReducerError, "GOOGLE_PROMOTION"):
            reducer.validate_contract(contract)
        contract = self.contract(); contract["eas_a"]["source_correctness"] = "SUPPORTED"
        with self.assertRaisesRegex(reducer.ReducerError, "SOURCE_CORRECTNESS_PROMOTION"):
            reducer.validate_contract(contract)

    def test_core_reuse_cannot_gain_canonical_authority(self):
        contract = self.contract(); contract["core_reuse"]["canonical_advancement_authority"] = "CURRENT"
        with self.assertRaisesRegex(reducer.ReducerError, "CORE_REUSE_AUTHORITY"):
            reducer.validate_contract(contract)

    def test_superseded_runner_or_reducer_cannot_regain_authority(self):
        contract = self.contract(); contract["superseded_authority"][0]["authority"] = "CURRENT"
        with self.assertRaisesRegex(reducer.ReducerError, "SUPERSEDED_AUTHORITY_PROMOTED"):
            reducer.validate_contract(contract)
        contract = self.contract(); contract["superseded_authority"][1]["authority"] = "CURRENT"
        with self.assertRaisesRegex(reducer.ReducerError, "SUPERSEDED_AUTHORITY_PROMOTED"):
            reducer.validate_contract(contract)

    def test_queue_v3_is_refused(self):
        queue = self.queue(); queue["schema_version"] = "enterprise-agent-system/local-handoff-queue/v3"
        with self.assertRaisesRegex(reducer.ReducerError, "QUEUE_SCHEMA"):
            reducer.validate_queue(queue)

    def test_queue_canary_or_closure_promotion_is_refused(self):
        queue = self.queue(); queue["closure_projection"]["vertical_canary"] = "EXECUTED"
        with self.assertRaisesRegex(reducer.ReducerError, "QUEUE_CANARY_PROMOTION"):
            reducer.validate_queue(queue)
        queue = self.queue(); queue["closure_projection"]["requirements_closure_credit"] = 1
        with self.assertRaisesRegex(reducer.ReducerError, "QUEUE_CLOSURE_PROMOTION"):
            reducer.validate_queue(queue)

    def test_contract_cannot_claim_real_receipt_or_execution(self):
        contract = self.contract(); contract["real_local_receipt"] = "OBSERVED"
        with self.assertRaisesRegex(reducer.ReducerError, "FALSE_REAL_RECEIPT"):
            reducer.validate_contract(contract)
        contract = self.contract(); contract["active_execution"] = "PASS"
        with self.assertRaisesRegex(reducer.ReducerError, "FALSE_EXECUTION_PROMOTION"):
            reducer.validate_contract(contract)

    def test_real_label_still_grants_zero_local_credit(self):
        base = __import__("test_receipt_reducer")
        fixture = base.ReceiptReducerTests(methodName="test_real_label_cannot_self_grant_local_credit")
        receipt = fixture.receipt()
        decision = reducer.reduce_receipt(receipt, reducer.load_json(reducer.SCHEMA_PATH), reducer.validate_queue(self.queue()), source_kind="REAL_LOCAL_RECEIPT")
        self.assertEqual(decision["decision"], "NEXT_EPOCH_CANDIDATE_READY")
        self.assertEqual(decision["real_local_evidence_credit"], 0)
        self.assertFalse(decision["queue_mutation_performed"])
        self.assertFalse(decision["canonical_advancement_performed"])


if __name__ == "__main__":
    unittest.main()
