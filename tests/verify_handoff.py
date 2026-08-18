#!/usr/bin/env python3
"""Deterministic shape and authority gate for Local Handoff queue candidates."""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import sys
from typing import Any, Callable

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "handoff" / "local-handoff-queue.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
ISSUE_URL = re.compile(r"^https://github\.com/ed3c/enterprise_agent_system/issues/[0-9]+$")
SECRET_OR_PRIVATE = re.compile(
    r"(?i)(PRIVATE KEY|(?:password|secret|token|cookie|session)\s*[:=]\s*\S{6,}|/Users/|/home/|/mnt/data/|gemini\.google\.com/app/)"
)
UNSAFE_SHELL = re.compile(r"(?:&&|\|\||`|\$\(|\n|\r|\|\s|\s\||(?:^|\s)[<>](?:\s|$))")
TOP_KEYS = {
    "schema_version",
    "queue_id",
    "state",
    "active_item_id",
    "environment_name_allowlist",
    "secret_values_allowed",
    "items",
    "advance_rule",
    "human_owned",
    "evidence_ceiling",
}
ACTIVE_KEYS = {
    "item_id",
    "state",
    "owner_issue",
    "blocked_issues",
    "objective",
    "required_runtime_any_of",
    "required_capabilities",
    "subjects",
    "commands",
    "required_receipt",
    "cleanup",
    "success_transition",
    "failure_transition",
    "claims_not_proven",
}
BLOCKED_KEYS = {"item_id", "state", "owner_issue", "blocked_by", "objective", "next_transition"}
COMMAND_KEYS = {"command_id", "cwd", "argv", "timeout_seconds"}
CWD_KEYS = {"env", "relative"}
RECEIPT_KEYS = {"path", "required_fields"}
REQUIRED_RECEIPT_FIELDS = {
    "queue_id",
    "item_id",
    "started_at",
    "finished_at",
    "commands",
    "exit_codes",
    "stdout_digests",
    "stderr_digests",
    "observed_commit",
    "observed_tree",
    "source_digest",
    "dirty_state_before",
    "dirty_state_after",
    "residue_inventory",
    "cleanup_result",
    "failures",
    "retries",
    "claims_not_proven",
}
ALLOWED_EXECUTABLES = {"git", "python3"}


class Refusal(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "QUEUE_ROOT_NOT_OBJECT")
    return value


def strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from strings(item)


def exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label}_NOT_OBJECT")
    missing = expected - set(value)
    unknown = set(value) - expected
    require(not missing and not unknown, f"{label}_FIELDS:missing={sorted(missing)}:unknown={sorted(unknown)}")
    return value


def unique_strings(value: Any, label: str, *, nonempty: bool = True) -> list[str]:
    require(isinstance(value, list), f"{label}_NOT_ARRAY")
    if nonempty:
        require(bool(value), f"{label}_EMPTY")
    require(all(isinstance(item, str) and bool(item) for item in value), f"{label}_ITEM")
    require(len(value) == len(set(value)), f"{label}_DUPLICATE")
    return value


def safe_relative(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(value), f"{label}_EMPTY")
    path = pathlib.PurePosixPath(value)
    require(not path.is_absolute(), f"{label}_ABSOLUTE")
    require(".." not in path.parts, f"{label}_TRAVERSAL")
    return value


def validate_env_path(value: Any, allowlist: set[str], label: str) -> None:
    item = exact_keys(value, {"env", "relative"}, label)
    require(item["env"] in allowlist, f"UNKNOWN_ENV:{item['env']}")
    safe_relative(item["relative"], f"{label}_RELATIVE")


def validate_argv_token(value: Any, allowlist: set[str], command_id: str, index: int) -> str | None:
    require(isinstance(value, dict), f"ARGV_TOKEN_NOT_OBJECT:{command_id}:{index}")
    require(set(value) in ({"literal"}, {"env_path"}), f"ARGV_TOKEN_FIELDS:{command_id}:{index}")
    if "env_path" in value:
        validate_env_path(value["env_path"], allowlist, f"ARGV_ENV_PATH:{command_id}:{index}")
        return None
    literal = value["literal"]
    require(isinstance(literal, str) and bool(literal), f"ARGV_LITERAL_EMPTY:{command_id}:{index}")
    require("\x00" not in literal, f"ARGV_NUL:{command_id}:{index}")
    return literal


def validate_command(value: Any, allowlist: set[str], label: str) -> str:
    command = exact_keys(value, COMMAND_KEYS, label)
    command_id = command["command_id"]
    require(re.fullmatch(r"[A-Z][A-Z0-9_]*", str(command_id)) is not None, f"COMMAND_ID:{command_id}")
    cwd = exact_keys(command["cwd"], CWD_KEYS, f"CWD:{command_id}")
    require(cwd["env"] in allowlist, f"UNKNOWN_ENV:{cwd['env']}")
    safe_relative(cwd["relative"], f"CWD_RELATIVE:{command_id}")
    argv = command["argv"]
    require(isinstance(argv, list) and bool(argv), f"ARGV_EMPTY:{command_id}")
    literals = [validate_argv_token(token, allowlist, command_id, index) for index, token in enumerate(argv)]
    executable = literals[0]
    require(executable in ALLOWED_EXECUTABLES, f"EXECUTABLE_NOT_ALLOWED:{command_id}:{executable}")
    require(isinstance(command["timeout_seconds"], int) and 1 <= command["timeout_seconds"] <= 600, f"TIMEOUT:{command_id}")

    if command_id == "VERIFY_SOURCE_DIGEST":
        require(literals[:2] == ["python3", "-c"] and len(argv) == 3, "DIGEST_COMMAND_SHAPE")
        code = literals[2] or ""
        require("INCEPTION_SOURCE_PDF" in code, "DIGEST_COMMAND_ENV_ABSENT")
        require("a6f1245ff865cae24838ed8ec4828330be684f3c03b29b9064ade8bfac94d8da" in code, "DIGEST_COMMAND_EXPECTED_DIGEST_ABSENT")
        require("read_bytes()" in code and "write" not in code.lower(), "DIGEST_COMMAND_NOT_READ_ONLY")
    else:
        for index, literal in enumerate(literals):
            if literal is not None:
                require(UNSAFE_SHELL.search(literal) is None, f"SHELL_METACHAR:{command_id}:{index}")
        require("-c" not in [literal for literal in literals if literal is not None], f"GENERIC_INTERPRETER_C:{command_id}")
    return command_id


def validate_subjects(value: Any, allowlist: set[str]) -> None:
    require(isinstance(value, list) and len(value) == 2, "SUBJECT_DENOMINATOR")
    git_subjects = [item for item in value if isinstance(item, dict) and "commit" in item]
    source_subjects = [item for item in value if isinstance(item, dict) and "expected_digest" in item]
    require(len(git_subjects) == 1 and len(source_subjects) == 1, "SUBJECT_KINDS")

    git_subject = exact_keys(git_subjects[0], {"subject_id", "repository", "pull_request", "commit"}, "GIT_SUBJECT")
    require(git_subject["subject_id"] == "INCEPTION-C0-C1", "GIT_SUBJECT_ID")
    require(git_subject["repository"] == "ed3c/enterprise_agent_system", "GIT_SUBJECT_REPOSITORY")
    require(git_subject["pull_request"] == 21, "GIT_SUBJECT_PR")
    require(SHA40.fullmatch(str(git_subject["commit"])) is not None, "MUTABLE_GIT_SUBJECT")

    source = exact_keys(source_subjects[0], {"subject_id", "data_class", "egress_allowed", "expected_digest", "path_env"}, "LOCAL_SOURCE_SUBJECT")
    require(source["subject_id"] == "SRC-PDF-INCEPTION-001", "LOCAL_SOURCE_ID")
    require(source["data_class"] == "LOCAL_ONLY" and source["egress_allowed"] is False, "LOCAL_SOURCE_EGRESS_WIDENED")
    require(SHA256.fullmatch(str(source["expected_digest"])) is not None, "LOCAL_SOURCE_DIGEST")
    require(source["path_env"] in allowlist, f"UNKNOWN_ENV:{source['path_env']}")


def validate_active_item(value: Any, allowlist: set[str]) -> None:
    item = exact_keys(value, ACTIVE_KEYS, "ACTIVE_ITEM")
    require(item["state"] == "ACTIVE", "ACTIVE_ITEM_STATE")
    require(ISSUE_URL.fullmatch(str(item["owner_issue"])) is not None, "ACTIVE_OWNER_ISSUE")
    blocked_issues = unique_strings(item["blocked_issues"], "BLOCKED_ISSUES")
    require(all(ISSUE_URL.fullmatch(issue) is not None for issue in blocked_issues), "BLOCKED_ISSUE_URL")
    require(isinstance(item["objective"], str) and bool(item["objective"]), "ACTIVE_OBJECTIVE")
    unique_strings(item["required_runtime_any_of"], "REQUIRED_RUNTIME")
    unique_strings(item["required_capabilities"], "REQUIRED_CAPABILITIES")
    validate_subjects(item["subjects"], allowlist)

    command_ids = [validate_command(command, allowlist, "COMMAND") for command in item["commands"]]
    require(len(command_ids) == len(set(command_ids)) and len(command_ids) >= 6, "COMMAND_DENOMINATOR_OR_DUPLICATE")
    required_commands = {"FETCH_PROFILE_PR", "CREATE_DETACHED_WORKTREE", "VERIFY_SOURCE_DIGEST", "VERIFY_PROFILE", "REPLAY_PROFILE_MUTATIONS", "COMPILE_PROFILE_GATE"}
    require(set(command_ids) == required_commands, "COMMAND_SET")

    receipt = exact_keys(item["required_receipt"], RECEIPT_KEYS, "REQUIRED_RECEIPT")
    validate_env_path(receipt["path"], allowlist, "RECEIPT_PATH")
    fields = set(unique_strings(receipt["required_fields"], "RECEIPT_FIELDS"))
    require(fields == REQUIRED_RECEIPT_FIELDS, "RECEIPT_FIELDS_MISMATCH")

    cleanup_ids = [validate_command(command, allowlist, "CLEANUP_COMMAND") for command in item["cleanup"]]
    require(set(cleanup_ids) == {"REMOVE_PROFILE_WORKTREE", "PRUNE_WORKTREES"}, "CLEANUP_COMMAND_SET")
    require(isinstance(item["success_transition"], str) and bool(item["success_transition"]), "SUCCESS_TRANSITION")
    require(isinstance(item["failure_transition"], str) and bool(item["failure_transition"]), "FAILURE_TRANSITION")
    unique_strings(item["claims_not_proven"], "ACTIVE_CLAIMS_NOT_PROVEN")


def validate_blocked_item(value: Any) -> None:
    item = exact_keys(value, BLOCKED_KEYS, "BLOCKED_ITEM")
    require(item["state"] == "BLOCKED", "BLOCKED_ITEM_STATE")
    require(ISSUE_URL.fullmatch(str(item["owner_issue"])) is not None, "BLOCKED_OWNER_ISSUE")
    unique_strings(item["blocked_by"], "BLOCKED_BY")
    require(isinstance(item["objective"], str) and bool(item["objective"]), "BLOCKED_OBJECTIVE")
    require(isinstance(item["next_transition"], str) and bool(item["next_transition"]), "BLOCKED_NEXT_TRANSITION")


def validate(value: dict[str, Any]) -> None:
    exact_keys(value, TOP_KEYS, "QUEUE")
    require(value["schema_version"] == "enterprise-agent-system/local-handoff-queue/v1", "QUEUE_SCHEMA")
    require(value["queue_id"] == "LH-EAS-INCEPTION-2026-08-18", "QUEUE_ID")
    require(value["state"] == "QUEUE_CANDIDATE", "QUEUE_STATE")
    allowlist = set(unique_strings(value["environment_name_allowlist"], "ENV_ALLOWLIST"))
    require(allowlist == {"EAS_CHECKOUT", "EAS_WORKTREES", "EAS_RECEIPT_DIR", "INCEPTION_SOURCE_PDF"}, "ENV_ALLOWLIST_SET")
    require(value["secret_values_allowed"] is False, "SECRET_VALUES_ALLOWED")
    require(not any(SECRET_OR_PRIVATE.search(text) for text in strings(value)), "SECRET_PRIVATE_OR_HOST_PATH")

    items = value["items"]
    require(isinstance(items, list) and len(items) == 3, "ITEM_DENOMINATOR")
    item_ids = [item.get("item_id") for item in items if isinstance(item, dict)]
    require(len(item_ids) == len(items) == len(set(item_ids)), "ITEM_ID_DUPLICATE_OR_INVALID")
    active = [item for item in items if item.get("state") == "ACTIVE"]
    require(len(active) == 1, "EXACTLY_ONE_ACTIVE")
    require(value["active_item_id"] == active[0]["item_id"], "ACTIVE_ITEM_ID_MISMATCH")
    validate_active_item(active[0], allowlist)
    for item in items:
        if item is not active[0]:
            validate_blocked_item(item)

    require(isinstance(value["advance_rule"], str) and "canonical reducer" in value["advance_rule"].lower(), "ADVANCE_RULE")
    human_owned = set(unique_strings(value["human_owned"], "HUMAN_OWNED"))
    for operation in {"merge", "release", "rollback", "private-source egress approval"}:
        require(operation in human_owned, f"HUMAN_BOUNDARY_MISSING:{operation}")
    require(value["evidence_ceiling"] == "LOCAL_HANDOFF_QUEUE_CANDIDATE_ONLY", "EVIDENCE_CEILING_WIDENED")


def selftest(value: dict[str, Any]) -> None:
    active = lambda candidate: next(item for item in candidate["items"] if item["state"] == "ACTIVE")
    blocked = lambda candidate: next(item for item in candidate["items"] if item["state"] == "BLOCKED")
    command = lambda candidate, command_id: next(item for item in active(candidate)["commands"] if item["command_id"] == command_id)
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("EXACTLY_ONE_ACTIVE", lambda candidate: blocked(candidate).update(state="ACTIVE")),
        ("ACTIVE_ITEM_ID_MISMATCH", lambda candidate: candidate.update(active_item_id="LH-OTHER")),
        ("SECRET_PRIVATE_OR_HOST_PATH", lambda candidate: active(candidate).update(objective="token=abcdef123456")),
        ("UNKNOWN_ENV", lambda candidate: command(candidate, "FETCH_PROFILE_PR")["cwd"].update(env="UNKNOWN_ENV")),
        ("EXECUTABLE_NOT_ALLOWED", lambda candidate: command(candidate, "FETCH_PROFILE_PR")["argv"][0].update(literal="bash")),
        ("MUTABLE_GIT_SUBJECT", lambda candidate: next(item for item in active(candidate)["subjects"] if "commit" in item).update(commit="main")),
        ("LOCAL_SOURCE_EGRESS_WIDENED", lambda candidate: next(item for item in active(candidate)["subjects"] if "expected_digest" in item).update(data_class="PUBLIC", egress_allowed=True)),
        ("CLEANUP_COMMAND_SET", lambda candidate: active(candidate).update(cleanup=[])),
        ("BLOCKED_ITEM_FIELDS", lambda candidate: blocked(candidate).update(commands=[])),
        ("EVIDENCE_CEILING_WIDENED", lambda candidate: candidate.update(evidence_ceiling="EXECUTED")),
        ("CWD_RELATIVE:FETCH_PROFILE_PR_TRAVERSAL", lambda candidate: command(candidate, "FETCH_PROFILE_PR")["cwd"].update(relative="../escape")),
        ("COMMAND_DENOMINATOR_OR_DUPLICATE", lambda candidate: active(candidate)["commands"].append(copy.deepcopy(active(candidate)["commands"][0]))),
        ("RECEIPT_FIELDS_MISMATCH", lambda candidate: active(candidate)["required_receipt"]["required_fields"].pop()),
    ]
    for expected, mutate in mutations:
        candidate = copy.deepcopy(value)
        mutate(candidate)
        try:
            validate(candidate)
        except Refusal as exc:
            require(expected in str(exc), f"WRONG_REFUSAL:{expected}:{exc}")
        else:
            raise Refusal(f"MUTATION_DID_NOT_FAIL:{expected}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    try:
        value = load(QUEUE_PATH)
        validate(value)
        if args.selftest:
            selftest(value)
    except (OSError, json.JSONDecodeError, Refusal, TypeError, KeyError, StopIteration) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2
    print("PASS queue_items=3 active=1 commands=6 cleanup=2 mutations=13")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
