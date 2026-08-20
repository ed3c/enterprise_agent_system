#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import sys
from typing import Any, Mapping, Sequence

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import reduce_receipt as base  # noqa: E402

core = base.core
ROOT = base.ROOT
QUEUE_PATH = base.QUEUE_PATH
SCHEMA_PATH = base.SCHEMA_PATH
CONTRACT_PATH = ROOT / "handoff/local-receipt-reducer-contract-owner-reconciled.json"

QUEUE_ID = "LH-EAS-INCEPTION-P7-V4-2026-08-20"
QUEUE_PR = 114
QUEUE_COMMIT = "3fd99f4051dafa440d61c11eac610737281b1583"
QUEUE_TREE = "03a93749e3eb0999cca0e63041321a99286fbfb4"
QUEUE_VERIFY = 32390022568
QUEUE_SHADOW = 4984913981
RUNNER_PR = 116
RUNNER_COMMIT = "4735e30d2bc810dd3bfc25b645aaad35046bc1d5"
RUNNER_TREE = "c6f8b9e7d536686461206c192121575683aff145"
RUNNER_VERIFY = 32390817585
RUNNER_SHADOW = 4984976210
ACTIVE_ID = "LH-P7-01-ROOT-D-V3-LOCAL-READBACK"
NEXT_ID = "LH-P7-02-A2R-CONTEXT-TOKENIZER"
ROOT_D_COMMIT = base.ROOT_D_COMMIT
ROOT_D_TREE = base.ROOT_D_TREE
SUCCESS_TRANSITION = base.SUCCESS_TRANSITION
RECEIPT_VERSION = base.RECEIPT_VERSION
EAS_A_COMMIT = base.EAS_A_COMMIT
EAS_A_TREE = base.EAS_A_TREE
PRE_QUEUE = "75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4"
PRE_RUNNER = "7be0a69b0046b66799baee2ddb5e305c90d60ec6"
PRE_REDUCER = "4a44e9cf9ece133e8117ecc100e419f359d8e1a1"
OLD_BINDING_BLOB = "d804cc2ea2b7dde494adc1de1cd2a705f5bb0fc1"
CORE_BLOB = "4c5581eabb265346865963c74c573ffc057381b8"
ISSUE_PREFIX = "https://github.com/ed3c/enterprise_agent_system/issues/"
EXPECTED_OWNER_ROUTES = {
    "LH-P7-01-ROOT-D-V3-LOCAL-READBACK": 14,
    "LH-P7-02-A2R-CONTEXT-TOKENIZER": 7,
    "LH-P7-03-A1-PHYSICAL-DURABILITY": 5,
    "LH-P7-04-A2-ISOLATION-PROVIDER": 7,
    "LH-P7-05-A3-INDEPENDENT-SEMANTIC": 15,
    "LH-P7-06-A4-TERMS-TELEMETRY": 16,
    "LH-P7-07-A5-EXTERNAL-BENCHMARK": 17,
    "LH-P7-08-A6-PROVIDER-EFFECT": 18,
    "LH-P7-09-VERTICAL-CANARY": 14,
    "LH-P7-10-FINAL-TRUTH-VERIFY": 15,
    "LH-P7-11-HUMAN-ADMISSION": 14,
}

_old_validate_queue = base.validate_queue

base.CONTRACT_PATH = CONTRACT_PATH
core.CONTRACT_PATH = CONTRACT_PATH
for module in (base, core):
    module.QUEUE_ID = QUEUE_ID
    module.QUEUE_COMMIT = QUEUE_COMMIT
    module.QUEUE_TREE = QUEUE_TREE
    module.RUNNER_COMMIT = RUNNER_COMMIT
    module.RUNNER_TREE = RUNNER_TREE
    module.ACTIVE_ID = ACTIVE_ID
    module.NEXT_ID = NEXT_ID
    module.ROOT_D_COMMIT = ROOT_D_COMMIT
    module.ROOT_D_TREE = ROOT_D_TREE
    module.SUCCESS_TRANSITION = SUCCESS_TRANSITION
    module.RECEIPT_VERSION = RECEIPT_VERSION

ReducerError = base.ReducerError
load_json = base.load_json
blocked_missing = base.blocked_missing
reduce_receipt = base.reduce_receipt


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ReducerError(reason)


def validate_contract(contract: Mapping[str, Any]) -> None:
    require(contract.get("schema_version") == "enterprise-agent-system/local-receipt-reducer-contract/v3", "REDUCER_CONTRACT_SCHEMA")
    require(contract.get("contract_id") == "EAS-H5RR-P7-OWNER-ROUTE-RECONCILED-REDUCER-2026-08-20", "REDUCER_CONTRACT_ID")
    require(contract.get("state") == "REDUCER_REBIND_CANDIDATE", "REDUCER_CONTRACT_STATE")

    queue = contract.get("queue_subject", {})
    runner = contract.get("runner_subject", {})
    require(queue.get("pull_request") == QUEUE_PR, "QUEUE_PR_DRIFT")
    require((queue.get("commit"), queue.get("tree")) == (QUEUE_COMMIT, QUEUE_TREE), "QUEUE_SUBJECT_DRIFT")
    require(queue.get("verification_run") == QUEUE_VERIFY and queue.get("shadow_review") == QUEUE_SHADOW, "QUEUE_RECEIPT_DRIFT")
    require(runner.get("pull_request") == RUNNER_PR, "RUNNER_PR_DRIFT")
    require((runner.get("commit"), runner.get("tree")) == (RUNNER_COMMIT, RUNNER_TREE), "RUNNER_SUBJECT_DRIFT")
    require(runner.get("verification_run") == RUNNER_VERIFY and runner.get("shadow_review") == RUNNER_SHADOW, "RUNNER_RECEIPT_DRIFT")
    require(runner.get("relationship") == "TRUE_GIT_PARENT", "RUNNER_RELATIONSHIP")

    reuse = contract.get("binding_reuse", {})
    require(reuse.get("source_pull_request") == 107 and reuse.get("source_commit") == PRE_REDUCER, "BINDING_REUSE_SUBJECT")
    require(reuse.get("source_blob") == OLD_BINDING_BLOB, "BINDING_REUSE_BLOB")
    require(reuse.get("reuse_authority") == "CODE_REUSE_ONLY" and reuse.get("canonical_advancement_authority") == "NONE", "BINDING_REUSE_AUTHORITY")

    reducer_core = contract.get("reducer_core_reuse", {})
    require(reducer_core.get("source_pull_request") == 71 and reducer_core.get("source_blob") == CORE_BLOB, "CORE_REUSE_SUBJECT")
    require(reducer_core.get("reuse_authority") == "CODE_REUSE_ONLY" and reducer_core.get("canonical_advancement_authority") == "NONE", "CORE_REUSE_AUTHORITY")

    previous = contract.get("pre_reconciliation_authority")
    require(isinstance(previous, list) and len(previous) == 3, "PRE_RECONCILIATION_DENOMINATOR")
    by_kind = {row.get("kind"): row for row in previous if isinstance(row, dict)}
    require(by_kind.get("queue", {}).get("pull_request") == 99 and by_kind.get("queue", {}).get("commit") == PRE_QUEUE, "PRE_QUEUE")
    require(by_kind.get("runner", {}).get("pull_request") == 103 and by_kind.get("runner", {}).get("commit") == PRE_RUNNER, "PRE_RUNNER")
    require(by_kind.get("reducer", {}).get("pull_request") == 107 and by_kind.get("reducer", {}).get("commit") == PRE_REDUCER, "PRE_REDUCER")
    require(all(row.get("authority") == "NONE" for row in previous), "PRE_RECONCILIATION_AUTHORITY")

    require(contract.get("owner_routes") == EXPECTED_OWNER_ROUTES, "OWNER_ROUTE_CONTRACT_DRIFT")
    require(contract.get("active_item_id") == ACTIVE_ID and contract.get("next_item_id") == NEXT_ID, "ITEM_ROUTE_DRIFT")
    required = contract.get("required_receipt", {})
    require(required.get("schema_version") == RECEIPT_VERSION, "RECEIPT_VERSION_DRIFT")
    require(required.get("filename") == f"{ACTIVE_ID}.json", "RECEIPT_FILENAME_DRIFT")
    require(required.get("origin") == "EXTERNAL_ADMITTED_LOCAL_EXECUTION_ONLY", "RECEIPT_ORIGIN_DRIFT")

    laws = contract.get("reducer_laws", {})
    require(laws.get("missing_receipt") == "BLOCKED_BY_MISSING_REAL_LOCAL_RECEIPT", "MISSING_RECEIPT_LAW")
    require(laws.get("synthetic_fixture_receives_real_local_credit") is False, "SYNTHETIC_CREDIT")
    require(laws.get("real_label_self_grants_local_credit") is False, "REAL_LABEL_CREDIT")
    require(laws.get("real_local_credit_requires_external_authority") is True, "EXTERNAL_AUTHORITY_LAW")
    require(laws.get("queue_mutation") is False and laws.get("direct_queue_advancement") is False, "QUEUE_MUTATION")

    expected = contract.get("expected_pass_denominator", {})
    require(expected.get("main_commands") == 9 and expected.get("cleanup_commands") == 3 and expected.get("total_command_records") == 12, "PASS_DENOMINATOR")
    require((expected.get("root_d_commit"), expected.get("root_d_tree")) == (ROOT_D_COMMIT, ROOT_D_TREE), "ROOT_D_DENOMINATOR")
    require(expected.get("success_transition") == SUCCESS_TRANSITION, "SUCCESS_TRANSITION")

    eas = contract.get("eas_a", {})
    require((eas.get("commit"), eas.get("tree")) == (EAS_A_COMMIT, EAS_A_TREE), "EAS_A_SUBJECT")
    require(eas.get("authority") == "ADVISORY_ONLY" and eas.get("relationship") == "PROCESS_DEPENDENCY_NOT_GIT_PARENT", "EAS_A_AUTHORITY")
    require(eas.get("google_connectivity") == "NOT_PERFORMED" and eas.get("google_write") == "NOT_PERFORMED", "GOOGLE_PROMOTION")
    require(eas.get("source_correctness") == "NOT_PROVEN", "SOURCE_CORRECTNESS")

    public = contract.get("public_verification", {})
    require(public.get("real_canonical_receipt_creation_allowed") is False, "REAL_RECEIPT_CREATION")
    require(public.get("real_local_credit_grant_allowed") is False, "REAL_LOCAL_CREDIT")
    require(public.get("active_execution_allowed") is False and public.get("queue_write_allowed") is False, "PUBLIC_EXECUTION")
    require(contract.get("queue_execution") == "NOT_PERFORMED" and contract.get("active_execution") == "NOT_PERFORMED", "FALSE_EXECUTION")
    require(contract.get("real_local_receipt") == "NOT_OBSERVED", "FALSE_REAL_RECEIPT")
    require(contract.get("canonical_advancement") == "NOT_PERFORMED", "FALSE_ADVANCEMENT")
    require(contract.get("evidence_ceiling") == "PUBLIC_OWNER_RECONCILED_RECEIPT_REDUCER_SEMANTICS_ONLY", "REDUCER_CEILING")


def validate_queue(queue: Mapping[str, Any]) -> dict[str, Any]:
    item = _old_validate_queue(queue)
    actual = {row.get("item_id"): row.get("owner_issue") for row in queue.get("items", []) if isinstance(row, dict)}
    expected = {item_id: f"{ISSUE_PREFIX}{issue}" for item_id, issue in EXPECTED_OWNER_ROUTES.items()}
    require(actual == expected, "OWNER_ROUTE_DRIFT")
    require(f"{ISSUE_PREFIX}22" not in actual.values(), "CLOSED_P5_EXECUTION_AUTHORITY")
    return item


def plan(contract: Mapping[str, Any]) -> dict[str, Any]:
    validate_contract(contract)
    return {
        "schema_version": "enterprise-agent-system/local-receipt-reducer-plan/v3",
        "queue_subject": contract["queue_subject"],
        "runner_subject": contract["runner_subject"],
        "active_item_id": ACTIVE_ID,
        "next_item_id": NEXT_ID,
        "receipt_environment_name": "EAS_RECEIPT_DIR",
        "receipt_filename": f"{ACTIVE_ID}.json",
        "missing_receipt_decision": "BLOCKED_BY_MISSING_REAL_LOCAL_RECEIPT",
        "synthetic_fixture_real_local_credit": 0,
        "real_label_real_local_credit": 0,
        "real_local_credit_requires_external_authority": True,
        "vertical_canary_owner_issue": 14,
        "closed_p5_issue_22_execution_authority": "NONE",
        "pre_reconciliation_queue_authority": "NONE",
        "pre_reconciliation_runner_authority": "NONE",
        "pre_reconciliation_reducer_authority": "NONE",
        "queue_mutation_performed": False,
        "canonical_advancement_performed": False,
        "queue_execution": "NOT_PERFORMED",
        "active_execution": "NOT_PERFORMED",
        "real_local_receipt": "NOT_OBSERVED"
    }


base.validate_contract = validate_contract
base.validate_queue = validate_queue
base.plan = plan
core.validate_contract = validate_contract
core.validate_queue = validate_queue
core.plan = plan


def main(argv: Sequence[str] | None = None) -> int:
    return base.main(argv)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReducerError as exc:
        print(f"BLOCKED:{exc}", file=sys.stderr)
        raise SystemExit(3)
