#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any, Iterable, Mapping, Sequence

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "handoff/local-handoff-queue.json"
SCHEMA_PATH = ROOT / "handoff/local-handoff-receipt.schema.json"
CONTRACT_PATH = ROOT / "handoff/local-receipt-reducer-contract.json"

QUEUE_ID = "LH-EAS-INCEPTION-P7-V3-2026-08-20"
QUEUE_COMMIT = "a6dbbc52fba70c9732a1bf664f52a072cd83d608"
QUEUE_TREE = "7b54d0c56d088bf7edcf7b4c8984366a89ee9e36"
RUNNER_COMMIT = "f81c2ecabaaac44ff82832a482524124baec106a"
RUNNER_TREE = "49170e045200b1cd42d8022ca6fcb81c23314932"
ACTIVE_ID = "LH-P7-01-ROOT-D-V2-LOCAL-READBACK"
NEXT_ID = "LH-P7-02-A2R-CONTEXT-TOKENIZER"
ROOT_D_COMMIT = "68828ec8de5f3ad5aa133a5c772eefb80c775568"
ROOT_D_TREE = "bf338e0cd959a2b97adee79af7459222bd5211b9"
SUCCESS_TRANSITION = "CANDIDATE_RECEIPT_READY_FOR_CANONICAL_REDUCER"
RECEIPT_VERSION = "enterprise-agent-system/local-handoff-receipt/v2"

MAIN_IDS = [
    "FETCH_ROOT_D",
    "CREATE_ROOT_D_WORKTREE",
    "ASSERT_ROOT_D_SUBJECT",
    "REPLAY_GENERIC_X",
    "REPLAY_PROFILE_X",
    "REPLAY_PROFILE_X_MUTATIONS",
    "REPLAY_PROFILE_D",
    "REPLAY_PROFILE_D_MUTATIONS",
    "ASSERT_ROOT_D_PROJECTION",
]
CLEANUP_IDS = ["REMOVE_ROOT_D_WORKTREE", "PRUNE_WORKTREES", "DELETE_TEMP_ROOT_D_REF"]
EXPECTED_RECORDS = [("main", value) for value in MAIN_IDS] + [("cleanup", value) for value in CLEANUP_IDS]

SHA40 = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
PRIVATE_PATH = re.compile(r"(?:/Users/|/home/|/mnt/data/|[A-Za-z]:\\Users\\)")
SECRETISH = re.compile(r"(?i)(?:password|secret|api[_-]?key|access[_-]?token|cookie|session)\s*[:=]\s*[^\s,}\]]{4,}")


class ReducerError(RuntimeError):
    pass


def load_json(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReducerError(f"NOT_OBJECT:{path.name}")
    return value


def stable_digest(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ReducerError(reason)


def validate_contract(contract: Mapping[str, Any]) -> None:
    require(contract.get("schema_version") == "enterprise-agent-system/local-receipt-reducer-contract/v1", "REDUCER_CONTRACT_SCHEMA")
    require(contract.get("state") == "REDUCER_IMPLEMENTATION_CANDIDATE", "REDUCER_CONTRACT_STATE")
    queue = contract.get("queue_subject", {})
    runner = contract.get("runner_subject", {})
    require((queue.get("commit"), queue.get("tree")) == (QUEUE_COMMIT, QUEUE_TREE), "QUEUE_SUBJECT_DRIFT")
    require((runner.get("commit"), runner.get("tree")) == (RUNNER_COMMIT, RUNNER_TREE), "RUNNER_SUBJECT_DRIFT")
    require(runner.get("verification_run") == 32293402604, "RUNNER_VERIFY_DRIFT")
    require(runner.get("shadow_review") == 4976016596, "RUNNER_SHADOW_DRIFT")
    require(contract.get("active_item_id") == ACTIVE_ID and contract.get("next_item_id") == NEXT_ID, "ITEM_ROUTE_DRIFT")
    required = contract.get("required_receipt", {})
    require(required.get("schema_version") == RECEIPT_VERSION, "RECEIPT_VERSION_DRIFT")
    require(required.get("filename") == f"{ACTIVE_ID}.json", "RECEIPT_FILENAME_DRIFT")
    laws = contract.get("reducer_laws", {})
    require(laws.get("missing_receipt") == "BLOCKED_BY_MISSING_REAL_LOCAL_RECEIPT", "MISSING_RECEIPT_LAW")
    require(laws.get("synthetic_fixture_receives_real_local_credit") is False, "SYNTHETIC_CREDIT_LAUNDERING")
    require(laws.get("queue_mutation") is False and laws.get("direct_queue_advancement") is False, "QUEUE_MUTATION_LAUNDERING")


def validate_queue(queue: Mapping[str, Any]) -> dict[str, Any]:
    require(queue.get("schema_version") == "enterprise-agent-system/local-handoff-queue/v3", "QUEUE_SCHEMA")
    require(queue.get("queue_id") == QUEUE_ID, "QUEUE_ID")
    require(queue.get("queue_execution") == "NOT_PERFORMED", "FALSE_QUEUE_EXECUTION")
    require(queue.get("active_item_id") == ACTIVE_ID, "ACTIVE_ID")
    items = queue.get("items")
    require(isinstance(items, list), "QUEUE_ITEMS")
    active = [item for item in items if isinstance(item, dict) and item.get("state") == "ACTIVE"]
    require(len(active) == 1 and active[0].get("item_id") == ACTIVE_ID, "ACTIVE_CARDINALITY")
    require(len(items) >= 2 and items[1].get("item_id") == NEXT_ID and items[1].get("state") == "BLOCKED_BY_PREDECESSOR", "NEXT_ITEM_ROUTE")
    return active[0]


def validate_schema(schema: Mapping[str, Any]) -> tuple[set[str], set[str]]:
    properties = schema.get("properties")
    required = schema.get("required")
    require(isinstance(properties, dict) and isinstance(required, list), "RECEIPT_SCHEMA_SHAPE")
    require(schema.get("additionalProperties") is False, "RECEIPT_SCHEMA_OPEN")
    return set(properties), set(required)


def validate_subject(value: Any, reason: str) -> dict[str, str]:
    require(isinstance(value, dict) and set(value) == {"repository", "commit", "tree"}, reason + ":SHAPE")
    require(value.get("repository") == "ed3c/enterprise_agent_system", reason + ":REPOSITORY")
    require(isinstance(value.get("commit"), str) and SHA40.fullmatch(value["commit"]) is not None, reason + ":COMMIT")
    require(isinstance(value.get("tree"), str) and SHA40.fullmatch(value["tree"]) is not None, reason + ":TREE")
    return value  # type: ignore[return-value]


def validate_portable_surface(receipt: Mapping[str, Any]) -> None:
    for text in strings(receipt):
        require(PRIVATE_PATH.search(text) is None, "PORTABLE_PRIVATE_PATH_LEAK")
        require(SECRETISH.search(text) is None, "PORTABLE_SECRET_LIKE_VALUE")


def validate_command_denominator(receipt: Mapping[str, Any], *, require_complete: bool) -> None:
    commands = receipt.get("commands")
    exits = receipt.get("exit_codes")
    outs = receipt.get("stdout_digests")
    errs = receipt.get("stderr_digests")
    require(all(isinstance(value, list) for value in (commands, exits, outs, errs)), "COMMAND_ARRAYS")
    assert isinstance(commands, list) and isinstance(exits, list) and isinstance(outs, list) and isinstance(errs, list)
    require(len(commands) == len(exits) == len(outs) == len(errs), "COMMAND_CARDINALITY")
    require(all(isinstance(code, int) for code in exits), "EXIT_CODE_TYPE")
    require(all(isinstance(value, str) and DIGEST.fullmatch(value) is not None for value in [*outs, *errs]), "DIGEST_FORMAT")
    records: list[tuple[Any, Any]] = []
    for row in commands:
        require(isinstance(row, dict), "COMMAND_RECORD_SHAPE")
        records.append((row.get("phase"), row.get("command_id")))
    if require_complete:
        require(records == EXPECTED_RECORDS, "PASS_COMMAND_DENOMINATOR")
        require(all(code == 0 for code in exits), "PASS_NONZERO_EXIT")


def validate_residue(receipt: Mapping[str, Any], *, require_clean: bool) -> None:
    residue = receipt.get("residue_inventory")
    require(isinstance(residue, dict), "RESIDUE_SHAPE")
    if require_clean:
        require(residue.get("root_d_worktree_exists") is False, "WORKTREE_DIRECTORY_RESIDUE")
        require(residue.get("root_d_worktree_registered") is False, "WORKTREE_REGISTRATION_RESIDUE")
        require(residue.get("temporary_root_d_ref_present") is False, "TEMP_REF_RESIDUE")
        require(receipt.get("dirty_state_before") == "CLEAN" and receipt.get("dirty_state_after") == "CLEAN", "DIRTY_STATE")
        require(residue.get("checkout_dirty_state") == "CLEAN", "RESIDUE_DIRTY_STATE")


def validate_receipt(receipt: Mapping[str, Any], schema: Mapping[str, Any], item: Mapping[str, Any]) -> None:
    properties, required = validate_schema(schema)
    require(set(receipt) <= properties, "RECEIPT_UNKNOWN_FIELD")
    require(required <= set(receipt), "RECEIPT_MISSING_FIELD")
    require(receipt.get("schema_version") == RECEIPT_VERSION, "RECEIPT_SCHEMA_VERSION")
    require(receipt.get("queue_id") == QUEUE_ID and receipt.get("item_id") == ACTIVE_ID, "RECEIPT_QUEUE_ITEM")
    require(receipt.get("evidence_lane") == item.get("required_evidence_lane") == "LOCAL_DETERMINISTIC", "RECEIPT_EVIDENCE_LANE")
    before = validate_subject(receipt.get("subject_before"), "SUBJECT_BEFORE")
    after = validate_subject(receipt.get("subject_after"), "SUBJECT_AFTER")
    require((before["commit"], before["tree"]) == (RUNNER_COMMIT, RUNNER_TREE), "WRONG_RUNNER_SUBJECT_BEFORE")
    require((after["commit"], after["tree"]) == (RUNNER_COMMIT, RUNNER_TREE), "WRONG_RUNNER_SUBJECT_AFTER")
    require(isinstance(receipt.get("failures"), list) and isinstance(receipt.get("retries"), list), "ATTEMPT_DENOMINATOR")
    require(isinstance(receipt.get("claims_not_proven"), list) and bool(receipt.get("claims_not_proven")), "CLAIMS_NOT_PROVEN")
    validate_portable_surface(receipt)

    effect = receipt.get("effect_state", "NOT_APPLICABLE")
    readback = receipt.get("readback_state", "NOT_APPLICABLE")
    compensation = receipt.get("compensation_state", "NOT_APPLICABLE")
    require(effect in {"NOT_APPLICABLE", "NOT_PERFORMED"}, "LOCAL_RECEIPT_EFFECT_PROMOTION")
    require(readback in {"NOT_APPLICABLE", "NOT_PERFORMED"}, "LOCAL_RECEIPT_READBACK_PROMOTION")
    require(compensation in {"NOT_APPLICABLE", "NOT_PERFORMED"}, "LOCAL_RECEIPT_COMPENSATION_PROMOTION")

    result = receipt.get("result")
    require(result in {"PASS", "FAIL", "BLOCKED", "NOT_EXERCISED", "UNKNOWN_EFFECT", "HUMAN_ADMIT_REQUIRED"}, "RECEIPT_RESULT")
    require(receipt.get("cleanup_result") in {"PASS", "FAIL", "NOT_REQUIRED", "NOT_EXERCISED"}, "CLEANUP_RESULT")
    validate_command_denominator(receipt, require_complete=result == "PASS")
    validate_residue(receipt, require_clean=result == "PASS")

    if result == "PASS":
        require((receipt.get("observed_commit"), receipt.get("observed_tree")) == (ROOT_D_COMMIT, ROOT_D_TREE), "PASS_WITHOUT_EXACT_ROOT_D")
        require(receipt.get("cleanup_result") == "PASS", "PASS_WITHOUT_CLEANUP")
        require(receipt.get("failures") == [], "PASS_WITH_FAILURES")
        require(receipt.get("next_transition") == SUCCESS_TRANSITION, "PASS_NEXT_TRANSITION")
    else:
        require(isinstance(receipt.get("next_transition"), str) and bool(receipt.get("next_transition")), "NONPASS_NEXT_TRANSITION")


def blocked_missing() -> dict[str, Any]:
    return {
        "schema_version": "enterprise-agent-system/local-receipt-reducer-decision/v1",
        "decision": "BLOCKED_BY_MISSING_REAL_LOCAL_RECEIPT",
        "receipt_state": "NOT_EXERCISED",
        "active_item_id": ACTIVE_ID,
        "next_item_id": NEXT_ID,
        "real_local_evidence_credit": 0,
        "queue_mutation_performed": False,
        "canonical_advancement_performed": False,
        "claims_not_proven": [
            "No real local receipt was supplied.",
            "Public tests and synthetic fixtures do not satisfy the local execution lane."
        ],
    }


def reduce_receipt(receipt: Mapping[str, Any] | None, schema: Mapping[str, Any], item: Mapping[str, Any], *, source_kind: str) -> dict[str, Any]:
    if receipt is None:
        return blocked_missing()
    validate_receipt(receipt, schema, item)
    receipt_digest = stable_digest(receipt)
    if receipt.get("result") != "PASS":
        return {
            "schema_version": "enterprise-agent-system/local-receipt-reducer-decision/v1",
            "decision": "BLOCKED_BY_LOCAL_RECEIPT_RESULT",
            "receipt_state": receipt.get("result"),
            "receipt_digest": receipt_digest,
            "active_item_id": ACTIVE_ID,
            "next_item_id": NEXT_ID,
            "source_kind": source_kind,
            "receipt_semantics_admitted": False,
            "real_local_evidence_credit": 0,
            "queue_mutation_performed": False,
            "canonical_advancement_performed": False,
            "stronger_lane_credit": [],
        }
    return {
        "schema_version": "enterprise-agent-system/local-receipt-reducer-decision/v1",
        "decision": "NEXT_EPOCH_CANDIDATE_READY",
        "receipt_state": "PASS",
        "receipt_digest": receipt_digest,
        "active_item_id": ACTIVE_ID,
        "next_item_id": NEXT_ID,
        "source_kind": source_kind,
        "receipt_semantics_admitted": True,
        "real_local_evidence_credit": 0,
        "queue_mutation_performed": False,
        "canonical_advancement_performed": False,
        "stronger_lane_credit": [],
        "claims_not_proven": [
            "Receipt semantics are admitted, but real local evidence credit remains external to this public reducer decision.",
            "This decision is a next-epoch candidate only; the queue has not been mutated.",
            "LOCAL_DETERMINISTIC evidence grants no provider, physical, private, external-effect, user, Human, merge, release or rollback credit.",
        ],
    }


def plan(contract: Mapping[str, Any]) -> dict[str, Any]:
    validate_contract(contract)
    return {
        "schema_version": "enterprise-agent-system/local-receipt-reducer-plan/v1",
        "queue_subject": contract["queue_subject"],
        "runner_subject": contract["runner_subject"],
        "active_item_id": ACTIVE_ID,
        "next_item_id": NEXT_ID,
        "receipt_environment_name": "EAS_RECEIPT_DIR",
        "receipt_filename": f"{ACTIVE_ID}.json",
        "missing_receipt_decision": "BLOCKED_BY_MISSING_REAL_LOCAL_RECEIPT",
        "synthetic_fixture_real_local_credit": 0,
        "real_local_credit_requires_external_authority": True,
        "queue_mutation_performed": False,
        "canonical_advancement_performed": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail-closed queue-v3 local receipt reducer")
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
