#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
from typing import Any, Mapping, Sequence

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_active_core as core  # noqa: E402

ROOT = core.ROOT
QUEUE_PATH = core.QUEUE_PATH
SCHEMA_PATH = core.SCHEMA_PATH
QUEUE_VERIFY_PATH = core.QUEUE_VERIFY_PATH
CONTRACT_PATH = core.CONTRACT_PATH

QUEUE_PARENT_COMMIT = "75648e0a0ca37e9ebaf182ebd757e1fa9610cbb4"
QUEUE_PARENT_TREE = "eef641a94dec755267ebe8086b68ecbe98c5b68a"
QUEUE_PARENT_VERIFY = 32348407481
QUEUE_PARENT_SHADOW = 4980566877
QUEUE_ID = "LH-EAS-INCEPTION-P7-V4-2026-08-20"
ACTIVE_ID = "LH-P7-01-ROOT-D-V3-LOCAL-READBACK"
ROOT_D_COMMIT = "6981c700f9f2f9128ebeebdf80e627178b2be336"
ROOT_D_TREE = "d044ae652b65af6a0aba49f0f79c7c04c630bebf"
WORKTREE_RELATIVE = "root-d-v3"
TEMP_REF = "refs/remotes/origin/p7-root-d-v3"
SUPERSEDED_QUEUE_V3 = "a6dbbc52fba70c9732a1bf664f52a072cd83d608"
SUPERSEDED_RUNNER_V3 = "f81c2ecabaaac44ff82832a482524124baec106a"
EAS_A_COMMIT = "250717db1cad584d50890c0d851153fa2cd755e8"
EAS_A_TREE = "fbf6a75b6e89e906f227110dc5a61e4355b8a891"

# Rebind the previously verified execution core.  These names are intentionally
# assigned before any core function is called; the core resolves them at runtime.
core.QUEUE_PARENT_COMMIT = QUEUE_PARENT_COMMIT
core.QUEUE_PARENT_TREE = QUEUE_PARENT_TREE
core.QUEUE_PARENT_VERIFY = QUEUE_PARENT_VERIFY
core.QUEUE_PARENT_SHADOW = QUEUE_PARENT_SHADOW
core.QUEUE_ID = QUEUE_ID
core.ACTIVE_ID = ACTIVE_ID
core.ROOT_D_COMMIT = ROOT_D_COMMIT
core.ROOT_D_TREE = ROOT_D_TREE
core.WORKTREE_RELATIVE = WORKTREE_RELATIVE
core.TEMP_REF = TEMP_REF
# The core's legacy variable names are implementation details.  Their values are
# rebound to the immediately superseded queue/runner subjects, both authority NONE.
core.SUPERSEDED_QUEUE_V2 = SUPERSEDED_QUEUE_V3
core.SUPERSEDED_RUNNER_V2 = SUPERSEDED_RUNNER_V3

RunnerError = core.RunnerError
load_json = core.load_json
digest_bytes = core.digest_bytes
run_process = core.run_process
git_bytes = core.git_bytes
git_subject = core.git_subject
dirty_state = core.dirty_state
validate_relative = core.validate_relative
environment_root = core.environment_root
assert_execution_roots = core.assert_execution_roots
resolve_env_path = core.resolve_env_path
render_arg = core.render_arg
required_env_names = core.required_env_names
sanitized_child_env = core.sanitized_child_env
public_command_record = core.public_command_record
command_result = core.command_result
temp_ref_present = core.temp_ref_present
worktree_registered = core.worktree_registered
residue_inventory = core.residue_inventory
preflight_residue_clean = core.preflight_residue_clean
clean_residue = core.clean_residue
assert_admitted_runner_subject = core.assert_admitted_runner_subject
validate_receipt = core.validate_receipt
atomic_write_json = core.atomic_write_json
assert_exact_parent_bytes = core.assert_exact_parent_bytes


def validate_runner_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != "enterprise-agent-system/local-handoff-runner-contract/v3":
        raise RunnerError("RUNNER_CONTRACT_SCHEMA")
    if contract.get("contract_id") != "EAS-H4R-P7-QUEUE-V4-RUNNER-2026-08-20":
        raise RunnerError("RUNNER_CONTRACT_ID")
    subject = contract.get("queue_subject")
    if not isinstance(subject, dict):
        raise RunnerError("QUEUE_SUBJECT_MISSING")
    if subject.get("pull_request") != 99:
        raise RunnerError("QUEUE_PARENT_PR_DRIFT")
    if (subject.get("commit"), subject.get("tree")) != (QUEUE_PARENT_COMMIT, QUEUE_PARENT_TREE):
        raise RunnerError("QUEUE_PARENT_DRIFT")
    if subject.get("verification_run") != QUEUE_PARENT_VERIFY or subject.get("shadow_review") != QUEUE_PARENT_SHADOW:
        raise RunnerError("QUEUE_PARENT_RECEIPT_DRIFT")
    if subject.get("relationship") != "TRUE_GIT_PARENT":
        raise RunnerError("QUEUE_PARENT_RELATIONSHIP")
    if contract.get("active_item_id") != ACTIVE_ID:
        raise RunnerError("ACTIVE_ID_DRIFT")
    if contract.get("default_mode") != "plan" or contract.get("modes") != ["plan", "execute"]:
        raise RunnerError("DEFAULT_MODE_NOT_PLAN")
    if contract.get("runner_execution") != "NOT_PERFORMED" or contract.get("queue_execution") != "NOT_PERFORMED":
        raise RunnerError("FALSE_EXECUTION_PROMOTION")
    if contract.get("canonical_advancement") != "NOT_PERFORMED":
        raise RunnerError("FALSE_ADVANCEMENT_PROMOTION")
    if contract.get("evidence_ceiling") != "PUBLIC_QUEUE_V4_RUNNER_IMPLEMENTATION_ONLY":
        raise RunnerError("RUNNER_EVIDENCE_CEILING")

    eas = contract.get("eas_a")
    if not isinstance(eas, dict):
        raise RunnerError("EAS_A_MISSING")
    if (eas.get("commit"), eas.get("tree")) != (EAS_A_COMMIT, EAS_A_TREE):
        raise RunnerError("EAS_A_SUBJECT")
    if eas.get("authority") != "ADVISORY_ONLY" or eas.get("relationship") != "PROCESS_DEPENDENCY_NOT_GIT_PARENT":
        raise RunnerError("EAS_A_AUTHORITY")
    if eas.get("google_connectivity") != "NOT_PERFORMED" or eas.get("google_write") != "NOT_PERFORMED":
        raise RunnerError("GOOGLE_PROMOTION")
    if eas.get("source_correctness") != "NOT_PROVEN":
        raise RunnerError("SOURCE_CORRECTNESS_PROMOTION")

    reuse = contract.get("core_reuse")
    if not isinstance(reuse, dict):
        raise RunnerError("CORE_REUSE_MISSING")
    if reuse.get("source_pull_request") != 67 or reuse.get("source_commit") != SUPERSEDED_RUNNER_V3:
        raise RunnerError("CORE_REUSE_SUBJECT")
    if reuse.get("source_blob") != "8c4ae46515bca4ab2f5e89e1d2677c84d65bbd8f":
        raise RunnerError("CORE_REUSE_BLOB")
    if reuse.get("reuse_authority") != "CODE_REUSE_ONLY" or reuse.get("execution_authority") != "NONE":
        raise RunnerError("CORE_REUSE_AUTHORITY")

    old = contract.get("superseded_authority")
    if not isinstance(old, list) or len(old) != 2:
        raise RunnerError("SUPERSEDED_DENOMINATOR")
    by_kind = {entry.get("kind"): entry for entry in old if isinstance(entry, dict)}
    if by_kind.get("queue", {}).get("pull_request") != 59 or by_kind.get("queue", {}).get("commit") != SUPERSEDED_QUEUE_V3:
        raise RunnerError("OLD_QUEUE_V3_NOT_BOUND")
    if by_kind.get("runner", {}).get("pull_request") != 67 or by_kind.get("runner", {}).get("commit") != SUPERSEDED_RUNNER_V3:
        raise RunnerError("OLD_RUNNER_V3_NOT_BOUND")
    if any(entry.get("authority") != "NONE" for entry in old):
        raise RunnerError("SUPERSEDED_AUTHORITY_PROMOTED")

    public = contract.get("public_verification")
    if not isinstance(public, dict) or public.get("real_queue_execute_allowed") is not False or public.get("plan_allowed") is not True:
        raise RunnerError("PUBLIC_VERIFICATION_EXECUTION_BOUNDARY")


def validate_queue(queue: Mapping[str, Any]) -> dict[str, Any]:
    if queue.get("schema_version") != "enterprise-agent-system/local-handoff-queue/v4":
        raise RunnerError("QUEUE_SCHEMA")
    if queue.get("queue_id") != QUEUE_ID or queue.get("queue_execution") != "NOT_PERFORMED":
        raise RunnerError("QUEUE_ID_OR_EXECUTION_DRIFT")
    if queue.get("active_item_id") != ACTIVE_ID:
        raise RunnerError("QUEUE_ACTIVE_DRIFT")
    eas = queue.get("eas_a")
    if not isinstance(eas, dict) or (eas.get("commit"), eas.get("tree")) != (EAS_A_COMMIT, EAS_A_TREE):
        raise RunnerError("QUEUE_EAS_A_SUBJECT")
    if eas.get("authority") != "ADVISORY_ONLY" or eas.get("relationship") != "PROCESS_DEPENDENCY_NOT_GIT_PARENT":
        raise RunnerError("QUEUE_EAS_A_AUTHORITY")
    if eas.get("google_connectivity") != "NOT_PERFORMED" or eas.get("google_write") != "NOT_PERFORMED" or eas.get("source_correctness") != "NOT_PROVEN":
        raise RunnerError("QUEUE_EAS_A_EVIDENCE_PROMOTION")

    items = queue.get("items")
    if not isinstance(items, list) or len(items) != 11:
        raise RunnerError("QUEUE_ITEMS")
    active = [row for row in items if isinstance(row, dict) and row.get("state") == "ACTIVE"]
    if len(active) != 1 or active[0].get("item_id") != ACTIVE_ID:
        raise RunnerError("ACTIVE_CARDINALITY")
    item = active[0]
    if item.get("required_evidence_lane") != "LOCAL_DETERMINISTIC":
        raise RunnerError("ACTIVE_LANE_DRIFT")
    command_ids = [row.get("command_id") for row in item.get("commands", [])]
    if command_ids != [
        "FETCH_ROOT_D", "CREATE_ROOT_D_WORKTREE", "ASSERT_ROOT_D_SUBJECT",
        "REPLAY_GENERIC_X", "REPLAY_PROFILE_X", "REPLAY_PROFILE_X_MUTATIONS",
        "REPLAY_PROFILE_D", "REPLAY_PROFILE_D_MUTATIONS", "ASSERT_ROOT_D_PROJECTION",
    ]:
        raise RunnerError("ACTIVE_COMMAND_DENOMINATOR")
    cleanup_ids = [row.get("command_id") for row in item.get("cleanup", [])]
    if cleanup_ids != ["REMOVE_ROOT_D_WORKTREE", "PRUNE_WORKTREES", "DELETE_TEMP_ROOT_D_REF"]:
        raise RunnerError("CLEANUP_DENOMINATOR")
    subjects = {row.get("subject_id"): row for row in item.get("subjects", []) if isinstance(row, dict)}
    root_subject = subjects.get("ROOT-D", {})
    if (root_subject.get("commit"), root_subject.get("tree")) != (ROOT_D_COMMIT, ROOT_D_TREE):
        raise RunnerError("ROOT_D_SUBJECT_DRIFT")
    eas_subject = subjects.get("EAS-A", {})
    if (eas_subject.get("commit"), eas_subject.get("tree")) != (EAS_A_COMMIT, EAS_A_TREE):
        raise RunnerError("ACTIVE_EAS_A_SUBJECT_DRIFT")
    if eas_subject.get("authority") != "ADVISORY_ONLY" or eas_subject.get("relationship") != "PROCESS_DEPENDENCY_NOT_GIT_PARENT":
        raise RunnerError("ACTIVE_EAS_A_AUTHORITY")
    receipt = item.get("required_receipt", {})
    if receipt.get("path", {}).get("relative") != "LH-P7-01-ROOT-D-V3-LOCAL-READBACK.json":
        raise RunnerError("RECEIPT_ROUTE_DRIFT")
    projection = queue.get("closure_projection", {})
    if projection.get("vertical_canary") != "PLAN_ONLY" or projection.get("vertical_execution_receipt") is not None:
        raise RunnerError("CANARY_PROMOTION")
    if projection.get("requirements_closure_credit") != 0 or projection.get("full_architecture") != "BLOCKED_FOR_CLOSURE":
        raise RunnerError("CLOSURE_PROMOTION")
    return item


def build_plan(queue: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, Any]:
    validate_runner_contract(contract)
    item = validate_queue(queue)
    return {
        "schema_version": "enterprise-agent-system/local-handoff-runner-plan/v3",
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
        "superseded_queue_v3_authority": "NONE",
        "superseded_runner_v3_authority": "NONE",
        "eas_a_authority": "ADVISORY_ONLY",
        "queue_execution": "NOT_PERFORMED",
        "runner_execution": "NOT_PERFORMED",
        "canonical_advancement": "NOT_PERFORMED",
    }


# Core functions look up these globals dynamically; replace only the binding and
# validation layer while preserving the previously verified execution mechanics.
core.validate_runner_contract = validate_runner_contract
core.validate_queue = validate_queue
core.build_plan = build_plan
active_item = core.active_item
execute_active = core.execute_active


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail-closed EAS queue-v4 Local Handoff runner")
    parser.add_argument("--mode", choices=["plan", "execute"], default="plan")
    parser.add_argument("--runtime-kind")
    parser.add_argument("--admitted-runner-commit")
    parser.add_argument("--admitted-runner-tree")
    args = parser.parse_args(argv)

    queue = load_json(QUEUE_PATH)
    contract = load_json(CONTRACT_PATH)
    schema = load_json(SCHEMA_PATH)
    validate_runner_contract(contract)
    validate_queue(queue)

    if args.mode == "plan":
        if (ROOT / ".git").exists():
            assert_exact_parent_bytes(ROOT)
        print(json.dumps(build_plan(queue, contract), indent=2, sort_keys=True))
        return 0

    if not args.runtime_kind:
        raise RunnerError("EXECUTE_REQUIRES_RUNTIME_KIND")
    if not args.admitted_runner_commit or not args.admitted_runner_tree:
        raise RunnerError("EXECUTE_REQUIRES_ADMITTED_RUNNER_SUBJECT")
    receipt, path = execute_active(
        queue,
        contract,
        schema,
        runtime_kind=args.runtime_kind,
        admitted_runner_commit=args.admitted_runner_commit,
        admitted_runner_tree=args.admitted_runner_tree,
        environ=os.environ,
    )
    print(json.dumps({
        "result": receipt["result"],
        "cleanup_result": receipt["cleanup_result"],
        "next_transition": receipt["next_transition"],
        "receipt_environment_name": "EAS_RECEIPT_DIR",
        "receipt_filename": path.name,
    }, indent=2, sort_keys=True))
    return 0 if receipt["result"] == "PASS" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RunnerError as exc:
        print(f"BLOCKED:{exc}", file=sys.stderr)
        raise SystemExit(3)
