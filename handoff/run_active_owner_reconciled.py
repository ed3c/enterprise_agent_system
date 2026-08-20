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

import run_active as base  # noqa: E402

core = base.core
ROOT = base.ROOT
QUEUE_PATH = base.QUEUE_PATH
SCHEMA_PATH = base.SCHEMA_PATH
QUEUE_VERIFY_PATH = base.QUEUE_VERIFY_PATH
CONTRACT_PATH = ROOT / "handoff/local-handoff-runner-contract-owner-reconciled.json"

QUEUE_PARENT_PR = 114
QUEUE_PARENT_COMMIT = "3fd99f4051dafa440d61c11eac610737281b1583"
QUEUE_PARENT_TREE = "03a93749e3eb0999cca0e63041321a99286fbfb4"
QUEUE_PARENT_VERIFY = 32390022568
QUEUE_PARENT_SHADOW = 4984913981
QUEUE_ID = "LH-EAS-INCEPTION-P7-V4-2026-08-20"
ACTIVE_ID = "LH-P7-01-ROOT-D-V3-LOCAL-READBACK"
ROOT_D_COMMIT = base.ROOT_D_COMMIT
ROOT_D_TREE = base.ROOT_D_TREE
EAS_A_COMMIT = base.EAS_A_COMMIT
EAS_A_TREE = base.EAS_A_TREE
PRE_RECONCILIATION_QUEUE = "75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4"
PRE_RECONCILIATION_RUNNER = "7be0a69b0046b66799baee2ddb5e305c90d60ec6"
OLD_BINDING_BLOB = "29cd7cb8861e93f8b31b6cd9110f9d14971338ba"
CORE_BLOB = "8c4ae46515bca4ab2f5e89e1d2677c84d65bbd8f"

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
ISSUE_PREFIX = "https://github.com/ed3c/enterprise_agent_system/issues/"

# Preserve the already-verified mechanics; rebind only current authority/identity.
_old_validate_queue = base.validate_queue

base.CONTRACT_PATH = CONTRACT_PATH
core.CONTRACT_PATH = CONTRACT_PATH
for module in (base, core):
    module.QUEUE_PARENT_COMMIT = QUEUE_PARENT_COMMIT
    module.QUEUE_PARENT_TREE = QUEUE_PARENT_TREE
    module.QUEUE_PARENT_VERIFY = QUEUE_PARENT_VERIFY
    module.QUEUE_PARENT_SHADOW = QUEUE_PARENT_SHADOW
    module.QUEUE_ID = QUEUE_ID
    module.ACTIVE_ID = ACTIVE_ID
    module.ROOT_D_COMMIT = ROOT_D_COMMIT
    module.ROOT_D_TREE = ROOT_D_TREE

# The old public queue/runner are no longer admissible execution identities after this rebind.
core.SUPERSEDED_QUEUE_V2 = PRE_RECONCILIATION_QUEUE
core.SUPERSEDED_RUNNER_V2 = PRE_RECONCILIATION_RUNNER

RunnerError = base.RunnerError
load_json = base.load_json
digest_bytes = base.digest_bytes
required_env_names = base.required_env_names


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise RunnerError(reason)


def validate_runner_contract(contract: Mapping[str, Any]) -> None:
    require(contract.get("schema_version") == "enterprise-agent-system/local-handoff-runner-contract/v4", "RUNNER_CONTRACT_SCHEMA")
    require(contract.get("contract_id") == "EAS-H5R-P7-OWNER-ROUTE-RECONCILED-RUNNER-2026-08-20", "RUNNER_CONTRACT_ID")
    require(contract.get("state") == "RUNNER_REBIND_CANDIDATE", "RUNNER_CONTRACT_STATE")

    subject = contract.get("queue_subject", {})
    require(subject.get("pull_request") == QUEUE_PARENT_PR, "QUEUE_PARENT_PR_DRIFT")
    require((subject.get("commit"), subject.get("tree")) == (QUEUE_PARENT_COMMIT, QUEUE_PARENT_TREE), "QUEUE_PARENT_DRIFT")
    require(subject.get("verification_run") == QUEUE_PARENT_VERIFY, "QUEUE_PARENT_VERIFY_DRIFT")
    require(subject.get("shadow_review") == QUEUE_PARENT_SHADOW, "QUEUE_PARENT_SHADOW_DRIFT")
    require(subject.get("relationship") == "TRUE_GIT_PARENT", "QUEUE_PARENT_RELATIONSHIP")

    reuse = contract.get("binding_reuse", {})
    require(reuse.get("source_pull_request") == 103, "BINDING_REUSE_PR")
    require(reuse.get("source_commit") == PRE_RECONCILIATION_RUNNER, "BINDING_REUSE_COMMIT")
    require(reuse.get("source_blob") == OLD_BINDING_BLOB, "BINDING_REUSE_BLOB")
    require(reuse.get("reuse_authority") == "CODE_REUSE_ONLY" and reuse.get("execution_authority") == "NONE", "BINDING_REUSE_AUTHORITY")

    execution_core = contract.get("execution_core_reuse", {})
    require(execution_core.get("source_pull_request") == 67, "CORE_REUSE_PR")
    require(execution_core.get("source_blob") == CORE_BLOB, "CORE_REUSE_BLOB")
    require(execution_core.get("reuse_authority") == "CODE_REUSE_ONLY" and execution_core.get("execution_authority") == "NONE", "CORE_REUSE_AUTHORITY")

    previous = contract.get("pre_reconciliation_authority")
    require(isinstance(previous, list) and len(previous) == 2, "PRE_RECONCILIATION_DENOMINATOR")
    by_kind = {row.get("kind"): row for row in previous if isinstance(row, dict)}
    require(by_kind.get("queue", {}).get("pull_request") == 99 and by_kind.get("queue", {}).get("commit") == PRE_RECONCILIATION_QUEUE, "PRE_RECONCILIATION_QUEUE")
    require(by_kind.get("runner", {}).get("pull_request") == 103 and by_kind.get("runner", {}).get("commit") == PRE_RECONCILIATION_RUNNER, "PRE_RECONCILIATION_RUNNER")
    require(all(row.get("authority") == "NONE" for row in previous), "PRE_RECONCILIATION_AUTHORITY")

    require(contract.get("active_item_id") == ACTIVE_ID, "ACTIVE_ID_DRIFT")
    require(contract.get("default_mode") == "plan" and contract.get("modes") == ["plan", "execute"], "DEFAULT_MODE_NOT_PLAN")
    require(contract.get("owner_routes") == EXPECTED_OWNER_ROUTES, "OWNER_ROUTE_CONTRACT_DRIFT")

    eas = contract.get("eas_a", {})
    require((eas.get("commit"), eas.get("tree")) == (EAS_A_COMMIT, EAS_A_TREE), "EAS_A_SUBJECT")
    require(eas.get("authority") == "ADVISORY_ONLY" and eas.get("relationship") == "PROCESS_DEPENDENCY_NOT_GIT_PARENT", "EAS_A_AUTHORITY")
    require(eas.get("google_connectivity") == "NOT_PERFORMED" and eas.get("google_write") == "NOT_PERFORMED", "GOOGLE_PROMOTION")
    require(eas.get("source_correctness") == "NOT_PROVEN", "SOURCE_CORRECTNESS_PROMOTION")

    public = contract.get("public_verification", {})
    require(public.get("real_queue_execute_allowed") is False and public.get("plan_allowed") is True, "PUBLIC_VERIFICATION_BOUNDARY")
    require(contract.get("runner_execution") == "NOT_PERFORMED" and contract.get("queue_execution") == "NOT_PERFORMED", "FALSE_EXECUTION_PROMOTION")
    require(contract.get("canonical_advancement") == "NOT_PERFORMED", "FALSE_ADVANCEMENT_PROMOTION")
    require(contract.get("evidence_ceiling") == "PUBLIC_RECONCILED_QUEUE_RUNNER_BINDING_ONLY", "RUNNER_EVIDENCE_CEILING")


def validate_queue(queue: Mapping[str, Any]) -> dict[str, Any]:
    item = _old_validate_queue(queue)
    actual = {row.get("item_id"): row.get("owner_issue") for row in queue.get("items", []) if isinstance(row, dict)}
    expected = {item_id: f"{ISSUE_PREFIX}{issue}" for item_id, issue in EXPECTED_OWNER_ROUTES.items()}
    require(actual == expected, "OWNER_ROUTE_DRIFT")
    require(f"{ISSUE_PREFIX}22" not in actual.values(), "CLOSED_P5_EXECUTION_AUTHORITY")
    return item


def build_plan(queue: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, Any]:
    validate_runner_contract(contract)
    item = validate_queue(queue)
    return {
        "schema_version": "enterprise-agent-system/local-handoff-runner-plan/v4",
        "mode": "plan",
        "queue_parent": contract["queue_subject"],
        "queue_id": queue.get("queue_id"),
        "active_item_id": item.get("item_id"),
        "required_runtime_any_of": item.get("required_runtime_any_of"),
        "required_environment_names": required_env_names(item),
        "command_ids": [row.get("command_id") for row in item.get("commands", [])],
        "cleanup_ids": [row.get("command_id") for row in item.get("cleanup", [])],
        "receipt": item.get("required_receipt"),
        "execute_requires_external_runner_admission": True,
        "pre_reconciliation_queue_authority": "NONE",
        "pre_reconciliation_runner_authority": "NONE",
        "vertical_canary_owner_issue": 14,
        "closed_p5_issue_22_execution_authority": "NONE",
        "eas_a_authority": "ADVISORY_ONLY",
        "queue_execution": "NOT_PERFORMED",
        "runner_execution": "NOT_PERFORMED",
        "canonical_advancement": "NOT_PERFORMED"
    }


base.validate_runner_contract = validate_runner_contract
base.validate_queue = validate_queue
base.build_plan = build_plan
core.validate_runner_contract = validate_runner_contract
core.validate_queue = validate_queue
core.build_plan = build_plan


def main(argv: Sequence[str] | None = None) -> int:
    return base.main(argv)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RunnerError as exc:
        print(f"BLOCKED:{exc}", file=sys.stderr)
        raise SystemExit(3)
