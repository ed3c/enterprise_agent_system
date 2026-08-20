#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Mapping, Sequence

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import reduce_receipt_core as core  # noqa: E402

ROOT = core.ROOT
QUEUE_PATH = core.QUEUE_PATH
SCHEMA_PATH = core.SCHEMA_PATH
CONTRACT_PATH = core.CONTRACT_PATH

QUEUE_ID = "LH-EAS-INCEPTION-P7-V4-2026-08-20"
QUEUE_COMMIT = "75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4"
QUEUE_TREE = "eef641a94dec755267ebe8086b68ecbe98c5b68a"
QUEUE_VERIFY = 32348407481
QUEUE_SHADOW = 4980566877
RUNNER_COMMIT = "7be0a69b0046b66799baee2ddb5e305c90d60ec6"
RUNNER_TREE = "e8a5643b7379acca281387727c203aa9c9559acb"
RUNNER_VERIFY = 32349394151
RUNNER_SHADOW = 4980654571
ACTIVE_ID = "LH-P7-01-ROOT-D-V3-LOCAL-READBACK"
NEXT_ID = "LH-P7-02-A2R-CONTEXT-TOKENIZER"
ROOT_D_COMMIT = "6981c700f9f2f9128ebeebdf80e627178b2be336"
ROOT_D_TREE = "d044ae652b65af6a0aba49f0f79c7c04c630bebf"
SUCCESS_TRANSITION = "CANDIDATE_RECEIPT_READY_FOR_CANONICAL_REDUCER"
RECEIPT_VERSION = "enterprise-agent-system/local-handoff-receipt/v2"
EAS_A_COMMIT = "250717db1cad584d50890c0d851153fa2cd755e8"
EAS_A_TREE = "fbf6a75b6e89e906f227110dc5a61e4355b8a891"
OLD_RUNNER_COMMIT = "f81c2ecabaaac44ff82832a482524124baec106a"
OLD_REDUCER_COMMIT = "82366dabf871f466c0c1353ef49198f82de90c16"

core.QUEUE_ID = QUEUE_ID
core.QUEUE_COMMIT = QUEUE_COMMIT
core.QUEUE_TREE = QUEUE_TREE
core.RUNNER_COMMIT = RUNNER_COMMIT
core.RUNNER_TREE = RUNNER_TREE
core.ACTIVE_ID = ACTIVE_ID
core.NEXT_ID = NEXT_ID
core.ROOT_D_COMMIT = ROOT_D_COMMIT
core.ROOT_D_TREE = ROOT_D_TREE
core.SUCCESS_TRANSITION = SUCCESS_TRANSITION
core.RECEIPT_VERSION = RECEIPT_VERSION

ReducerError = core.ReducerError
load_json = core.load_json
stable_digest = core.stable_digest
strings = core.strings
require = core.require
validate_schema = core.validate_schema
validate_subject = core.validate_subject
validate_portable_surface = core.validate_portable_surface
validate_command_denominator = core.validate_command_denominator
validate_residue = core.validate_residue
validate_receipt = core.validate_receipt
blocked_missing = core.blocked_missing
reduce_receipt = core.reduce_receipt
MAIN_IDS = core.MAIN_IDS
CLEANUP_IDS = core.CLEANUP_IDS
EXPECTED_RECORDS = core.EXPECTED_RECORDS


def validate_contract(contract: Mapping[str, Any]) -> None:
    require(contract.get("schema_version") == "enterprise-agent-system/local-receipt-reducer-contract/v2", "REDUCER_CONTRACT_SCHEMA")
    require(contract.get("contract_id") == "EAS-H4RR-P7-QUEUE-V4-RECEIPT-REDUCER-2026-08-20", "REDUCER_CONTRACT_ID")
    require(contract.get("state") == "REDUCER_IMPLEMENTATION_CANDIDATE", "REDUCER_CONTRACT_STATE")

    queue = contract.get("queue_subject", {})
    runner = contract.get("runner_subject", {})
    require(queue.get("pull_request") == 99, "QUEUE_PR_DRIFT")
    require((queue.get("commit"), queue.get("tree")) == (QUEUE_COMMIT, QUEUE_TREE), "QUEUE_SUBJECT_DRIFT")
    require(queue.get("verification_run") == QUEUE_VERIFY and queue.get("shadow_review") == QUEUE_SHADOW, "QUEUE_RECEIPT_DRIFT")
    require(runner.get("pull_request") == 103, "RUNNER_PR_DRIFT")
    require((runner.get("commit"), runner.get("tree")) == (RUNNER_COMMIT, RUNNER_TREE), "RUNNER_SUBJECT_DRIFT")
    require(runner.get("verification_run") == RUNNER_VERIFY and runner.get("shadow_review") == RUNNER_SHADOW, "RUNNER_RECEIPT_DRIFT")
    require(runner.get("relationship") == "TRUE_GIT_PARENT", "RUNNER_RELATIONSHIP")

    require(contract.get("active_item_id") == ACTIVE_ID and contract.get("next_item_id") == NEXT_ID, "ITEM_ROUTE_DRIFT")
    required = contract.get("required_receipt", {})
    require(required.get("schema_version") == RECEIPT_VERSION, "RECEIPT_VERSION_DRIFT")
    require(required.get("filename") == f"{ACTIVE_ID}.json", "RECEIPT_FILENAME_DRIFT")
    require(required.get("origin") == "EXTERNAL_ADMITTED_LOCAL_EXECUTION_ONLY", "RECEIPT_ORIGIN_DRIFT")

    eas = contract.get("eas_a", {})
    require((eas.get("commit"), eas.get("tree")) == (EAS_A_COMMIT, EAS_A_TREE), "EAS_A_SUBJECT")
    require(eas.get("authority") == "ADVISORY_ONLY" and eas.get("relationship") == "PROCESS_DEPENDENCY_NOT_GIT_PARENT", "EAS_A_AUTHORITY")
    require(eas.get("google_connectivity") == "NOT_PERFORMED" and eas.get("google_write") == "NOT_PERFORMED", "GOOGLE_PROMOTION")
    require(eas.get("source_correctness") == "NOT_PROVEN", "SOURCE_CORRECTNESS_PROMOTION")

    reuse = contract.get("core_reuse", {})
    require(reuse.get("source_pull_request") == 71 and reuse.get("source_commit") == OLD_REDUCER_COMMIT, "CORE_REUSE_SUBJECT")
    require(reuse.get("source_tree") == "6ca3e205afdc6b9347ccde06769344b8b37e1964", "CORE_REUSE_TREE")
    require(reuse.get("source_blob") == "4c5581eabb265346865963c74c573ffc057381b8", "CORE_REUSE_BLOB")
    require(reuse.get("reuse_authority") == "CODE_REUSE_ONLY" and reuse.get("canonical_advancement_authority") == "NONE", "CORE_REUSE_AUTHORITY")

    old = contract.get("superseded_authority")
    require(isinstance(old, list) and len(old) == 2, "SUPERSEDED_DENOMINATOR")
    by_kind = {entry.get("kind"): entry for entry in old if isinstance(entry, dict)}
    require(by_kind.get("runner", {}).get("pull_request") == 67 and by_kind.get("runner", {}).get("commit") == OLD_RUNNER_COMMIT, "OLD_RUNNER_NOT_BOUND")
    require(by_kind.get("reducer", {}).get("pull_request") == 71 and by_kind.get("reducer", {}).get("commit") == OLD_REDUCER_COMMIT, "OLD_REDUCER_NOT_BOUND")
    require(all(entry.get("authority") == "NONE" for entry in old), "SUPERSEDED_AUTHORITY_PROMOTED")

    laws = contract.get("reducer_laws", {})
    require(laws.get("missing_receipt") == "BLOCKED_BY_MISSING_REAL_LOCAL_RECEIPT", "MISSING_RECEIPT_LAW")
    require(laws.get("synthetic_fixture_receives_real_local_credit") is False, "SYNTHETIC_CREDIT_LAUNDERING")
    require(laws.get("real_label_self_grants_local_credit") is False, "REAL_LABEL_CREDIT_LAUNDERING")
    require(laws.get("real_local_credit_requires_external_authority") is True, "EXTERNAL_LOCAL_AUTHORITY_LAW")
    require(laws.get("queue_mutation") is False and laws.get("direct_queue_advancement") is False, "QUEUE_MUTATION_LAUNDERING")

    expected = contract.get("expected_pass_denominator", {})
    require(expected.get("main_commands") == 9 and expected.get("cleanup_commands") == 3 and expected.get("total_command_records") == 12, "PASS_DENOMINATOR")
    require((expected.get("root_d_commit"), expected.get("root_d_tree")) == (ROOT_D_COMMIT, ROOT_D_TREE), "ROOT_D_DENOMINATOR")
    require(expected.get("success_transition") == SUCCESS_TRANSITION, "SUCCESS_TRANSITION_DRIFT")

    public = contract.get("public_verification", {})
    require(public.get("synthetic_receipt_fixtures_allowed") is True, "SYNTHETIC_FIXTURE_POLICY")
    require(public.get("real_canonical_receipt_creation_allowed") is False, "REAL_RECEIPT_CREATION_PROMOTION")
    require(public.get("real_local_credit_grant_allowed") is False, "REAL_LOCAL_CREDIT_PROMOTION")
    require(public.get("active_execution_allowed") is False and public.get("queue_write_allowed") is False, "PUBLIC_EXECUTION_OR_QUEUE_WRITE")
    require(contract.get("queue_execution") == "NOT_PERFORMED" and contract.get("active_execution") == "NOT_PERFORMED", "FALSE_EXECUTION_PROMOTION")
    require(contract.get("real_local_receipt") == "NOT_OBSERVED", "FALSE_REAL_RECEIPT")
    require(contract.get("canonical_advancement") == "NOT_PERFORMED", "FALSE_CANONICAL_ADVANCEMENT")
    require(contract.get("evidence_ceiling") == "PUBLIC_QUEUE_V4_RECEIPT_REDUCER_SEMANTICS_ONLY", "REDUCER_EVIDENCE_CEILING")


def validate_queue(queue: Mapping[str, Any]) -> dict[str, Any]:
    require(queue.get("schema_version") == "enterprise-agent-system/local-handoff-queue/v4", "QUEUE_SCHEMA")
    require(queue.get("queue_id") == QUEUE_ID, "QUEUE_ID")
    require(queue.get("queue_execution") == "NOT_PERFORMED", "FALSE_QUEUE_EXECUTION")
    require(queue.get("active_item_id") == ACTIVE_ID, "ACTIVE_ID")
    eas = queue.get("eas_a", {})
    require((eas.get("commit"), eas.get("tree")) == (EAS_A_COMMIT, EAS_A_TREE), "QUEUE_EAS_A_SUBJECT")
    require(eas.get("authority") == "ADVISORY_ONLY" and eas.get("relationship") == "PROCESS_DEPENDENCY_NOT_GIT_PARENT", "QUEUE_EAS_A_AUTHORITY")
    require(eas.get("google_connectivity") == "NOT_PERFORMED" and eas.get("google_write") == "NOT_PERFORMED", "QUEUE_GOOGLE_PROMOTION")
    require(eas.get("source_correctness") == "NOT_PROVEN", "QUEUE_SOURCE_CORRECTNESS")
    projection = queue.get("closure_projection", {})
    require(projection.get("requirements_closure_credit") == 0, "QUEUE_CLOSURE_PROMOTION")
    require(projection.get("vertical_canary") == "PLAN_ONLY" and projection.get("vertical_execution_receipt") is None, "QUEUE_CANARY_PROMOTION")
    require(projection.get("full_architecture") == "BLOCKED_FOR_CLOSURE", "QUEUE_FULL_CLOSURE_PROMOTION")
    items = queue.get("items")
    require(isinstance(items, list) and len(items) == 11, "QUEUE_ITEMS")
    active = [item for item in items if isinstance(item, dict) and item.get("state") == "ACTIVE"]
    require(len(active) == 1 and active[0].get("item_id") == ACTIVE_ID, "ACTIVE_CARDINALITY")
    require(len(items) >= 2 and items[1].get("item_id") == NEXT_ID and items[1].get("state") == "BLOCKED_BY_PREDECESSOR", "NEXT_ITEM_ROUTE")
    return active[0]


def plan(contract: Mapping[str, Any]) -> dict[str, Any]:
    validate_contract(contract)
    return {
        "schema_version": "enterprise-agent-system/local-receipt-reducer-plan/v2",
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
        "queue_mutation_performed": False,
        "canonical_advancement_performed": False,
        "queue_execution": "NOT_PERFORMED",
        "active_execution": "NOT_PERFORMED",
        "real_local_receipt": "NOT_OBSERVED",
    }


core.validate_contract = validate_contract
core.validate_queue = validate_queue
core.plan = plan


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail-closed queue-v4 local receipt reducer")
    parser.add_argument("--mode", choices=["plan", "inspect"], default="plan")
    parser.add_argument("--receipt")
    parser.add_argument("--source-kind", choices=["REAL_LOCAL_RECEIPT", "SYNTHETIC_FIXTURE"], default="REAL_LOCAL_RECEIPT")
    args = parser.parse_args(argv)

    contract = load_json(CONTRACT_PATH)
    queue = load_json(QUEUE_PATH)
    schema = load_json(SCHEMA_PATH)
    validate_contract(contract)
    item = validate_queue(queue)

    if args.mode == "plan":
        print(json.dumps(plan(contract), indent=2, sort_keys=True))
        return 0

    if not args.receipt:
        decision = blocked_missing()
        print(json.dumps(decision, indent=2, sort_keys=True))
        return 4
    receipt_path = pathlib.Path(args.receipt).expanduser()
    if not receipt_path.exists() or not receipt_path.is_file():
        decision = blocked_missing()
        print(json.dumps(decision, indent=2, sort_keys=True))
        return 4
    receipt = load_json(receipt_path)
    decision = reduce_receipt(receipt, schema, item, source_kind=args.source_kind)
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0 if decision["decision"] == "NEXT_EPOCH_CANDIDATE_READY" else 5


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReducerError as exc:
        print(f"BLOCKED:{exc}", file=sys.stderr)
        raise SystemExit(3)
