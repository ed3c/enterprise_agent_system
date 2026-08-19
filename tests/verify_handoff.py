#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
from typing import Any, Callable

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "handoff" / "local-handoff-queue.json"
SCHEMA_PATH = ROOT / "handoff" / "local-handoff-receipt.schema.json"
HISTORY_PATH = ROOT / "handoff" / "history" / "LH-EAS-INCEPTION-2026-08-18-superseded.json"
README_PATH = ROOT / "handoff" / "README.md"

SHA40 = re.compile(r"^[0-9a-f]{40}$")
UNSAFE_SHELL = re.compile(r"(?:&&|\|\||`|\$\(|\n|\r)")
SECRET_ASSIGNMENT = re.compile(r"(?i)(password|secret|token|cookie|session)\s*[:=]\s*\S{4,}")
PRIVATE_PATH = re.compile(r"(?:/Users/|/home/|/mnt/data/)")
EXPECTED_IDS = [
    "LH-P7-01-FINAL-P6-LOCAL-READBACK",
    "LH-P7-02-A2R-CONTEXT-TOKENIZER",
    "LH-P7-03-A1-PHYSICAL-DURABILITY",
    "LH-P7-04-A2-ISOLATION-PROVIDER",
    "LH-P7-05-A3-INDEPENDENT-SEMANTIC",
    "LH-P7-06-A4-TERMS-TELEMETRY",
    "LH-P7-07-A5-EXTERNAL-BENCHMARK",
    "LH-P7-08-A6-PROVIDER-EFFECT",
    "LH-P7-09-VERTICAL-CANARY",
    "LH-P7-10-FINAL-TRUTH-VERIFY",
    "LH-P7-11-HUMAN-ADMISSION",
]
ROOT_D = ("89e12f5863c9bfd02bddb28de121d9c19cc25d16", "16e51462b2a0a693c1af92ad344fa3db6bbd4879")
OLD_QUEUE = ("9223107163b27984ed490246b4c0899caeb1bdae", "d462e2a1a69d225bf8161ce01918e5e8bb8d102f")
CANARY = "sha256:2146c02c23bbf87b6797900141c491a53f6936714b0b620a23016a2b20eaab79"


class QueueError(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise QueueError(reason)


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"NOT_OBJECT:{path}")
    return value


def check_sha(value: Any, reason: str) -> None:
    require(isinstance(value, str) and SHA40.fullmatch(value) is not None, reason)


def iter_env_refs(value: Any):
    if isinstance(value, dict):
        if set(value) == {"env", "relative"}:
            yield value["env"]
        if "env_path" in value and isinstance(value["env_path"], dict):
            yield value["env_path"].get("env")
        for child in value.values():
            yield from iter_env_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_env_refs(child)


def validate(queue: dict[str, Any], schema: dict[str, Any], history: dict[str, Any], readme: str) -> None:
    require(queue.get("schema_version") == "enterprise-agent-system/local-handoff-queue/v2", "QUEUE_SCHEMA")
    require(queue.get("queue_id") == "LH-EAS-INCEPTION-P7-2026-08-20", "QUEUE_ID")
    require(queue.get("state") == "READY_FOR_LOCAL_EXECUTION_PREPARATION", "QUEUE_STATE")
    require(queue.get("queue_execution") == "NOT_PERFORMED", "FALSE_QUEUE_EXECUTION")
    require(queue.get("evidence_ceiling") == "P7_EXECUTABLE_QUEUE_PREPARATION_ONLY", "QUEUE_CEILING")
    require(queue.get("secret_values_allowed") is False, "SECRET_VALUES_ALLOWED")
    require(queue.get("credential_values_allowed") is False, "CREDENTIAL_VALUES_ALLOWED")
    require(queue.get("failed_blocked_retried_attempts_must_remain_visible") is True, "ATTEMPT_DENOMINATOR")

    compiled = queue.get("compiled_from", {})
    require(compiled.get("commit") == ROOT_D[0] and compiled.get("tree") == ROOT_D[1], "ROOT_D_DRIFT")
    require(compiled.get("verification_run") == 32272986158, "ROOT_D_VERIFY_RECEIPT")
    require(compiled.get("shadow_review") == 4974136248, "ROOT_D_SHADOW_RECEIPT")
    require(compiled.get("p6_state") == "COMPLETE_AT_DOCS_CEILING", "P6_STATE")

    supersedes = queue.get("supersedes", {})
    require(supersedes.get("commit") == OLD_QUEUE[0] and supersedes.get("tree") == OLD_QUEUE[1], "OLD_QUEUE_SUBJECT")
    require(supersedes.get("previous_active_item") == "LH-INCEPTION-SOURCE-01", "OLD_ACTIVE")
    require(supersedes.get("disposition") == "SUPERSEDED_STALE_SUBJECT", "OLD_QUEUE_NOT_SUPERSEDED")
    require("60f994f" in supersedes.get("reason", ""), "STALE_REASON_MISSING")

    projection = queue.get("closure_projection", {})
    require(projection == {
        "requirements_total": 15,
        "requirements_required_lane_satisfied": 1,
        "requirements_closure_credit": 0,
        "contradictions_total": 14,
        "contradictions_preserved": 14,
        "profile_shadow": "BLOCKED_FOR_CLOSURE",
        "vertical_canary": "PLAN_ONLY",
        "vertical_execution_receipt": None,
        "EAS_A": "NOT_IMPLEMENTED",
        "profile_release": "NOT_ADMITTED",
    }, "CLOSURE_PROMOTION")

    allow = queue.get("environment_name_allowlist")
    require(isinstance(allow, list) and len(allow) >= 7 and len(set(allow)) == len(allow), "ENV_ALLOWLIST")
    require(all(isinstance(x, str) and re.fullmatch(r"[A-Z][A-Z0-9_]+", x) for x in allow), "ENV_NAME")
    allow_set = set(allow)

    items = queue.get("items")
    require(isinstance(items, list) and [x.get("item_id") for x in items] == EXPECTED_IDS, "ITEM_DENOMINATOR")
    active = [x for x in items if x.get("state") == "ACTIVE"]
    require(len(active) == 1 and active[0].get("item_id") == queue.get("active_item_id"), "ACTIVE_CARDINALITY")
    require(queue.get("active_item_id") == EXPECTED_IDS[0], "ACTIVE_ID")
    require(items[-1].get("state") == "HUMAN_ADMIT_REQUIRED", "HUMAN_TERMINAL_STATE")
    require(items[-1].get("required_evidence_lane") == "HUMAN_ADMIT", "HUMAN_LANE")
    require("commands" not in items[-1], "HUMAN_AUTO_COMMANDS")

    for index, item in enumerate(items):
        require(item.get("owner_issue", "").startswith("https://github.com/ed3c/enterprise_agent_system/issues/"), f"OWNER_ISSUE:{index}")
        require(item.get("claims_not_proven"), f"CLAIMS_NOT_PROVEN:{index}")
        if index > 0:
            require(item.get("blocked_by") == [items[index - 1]["item_id"]], f"CHAIN:{item.get('item_id')}")
            if index < len(items) - 1:
                require(item.get("state") == "BLOCKED_BY_PREDECESSOR", f"BLOCKED_STATE:{item.get('item_id')}")
                resolver = item.get("resolver")
                require(isinstance(resolver, dict) and resolver.get("requires"), f"RESOLVER:{item.get('item_id')}")
        subject = item.get("subject")
        if subject is not None:
            check_sha(subject.get("commit"), f"SUBJECT_COMMIT:{item.get('item_id')}")
            check_sha(subject.get("tree"), f"SUBJECT_TREE:{item.get('item_id')}")

    first = items[0]
    require(first.get("required_evidence_lane") == "LOCAL_DETERMINISTIC", "ACTIVE_LANE")
    subjects = first.get("subjects")
    require(isinstance(subjects, list) and len(subjects) == 3, "ACTIVE_SUBJECTS")
    root = next((x for x in subjects if x.get("subject_id") == "ROOT-D"), None)
    require(root and root.get("commit") == ROOT_D[0] and root.get("tree") == ROOT_D[1], "ACTIVE_ROOT_D")
    commands = first.get("commands")
    require(isinstance(commands, list) and len(commands) == 8, "ACTIVE_COMMANDS")
    require(isinstance(first.get("cleanup"), list) and len(first["cleanup"]) == 2, "ACTIVE_CLEANUP")
    receipt = first.get("required_receipt", {})
    require(receipt.get("schema") == "handoff/local-handoff-receipt.schema.json", "RECEIPT_SCHEMA_ROUTE")
    require(len(receipt.get("required_fields", [])) >= 20, "RECEIPT_FIELDS")
    require(first.get("rollback_subject", {}).get("commit") == ROOT_D[0], "ROLLBACK_SUBJECT")

    for command in commands + first["cleanup"]:
        require(isinstance(command.get("timeout_seconds"), int) and 0 < command["timeout_seconds"] <= 1800, f"TIMEOUT:{command.get('command_id')}")
        argv = command.get("argv")
        require(isinstance(argv, list) and argv, f"ARGV:{command.get('command_id')}")
        for arg in argv:
            require(isinstance(arg, dict) and len(arg) == 1, f"ARGV_SHAPE:{command.get('command_id')}")
            if "literal" in arg:
                text = arg["literal"]
                require(isinstance(text, str), f"ARGV_LITERAL:{command.get('command_id')}")
                require(UNSAFE_SHELL.search(text) is None, f"UNSAFE_SHELL:{command.get('command_id')}")
                require(SECRET_ASSIGNMENT.search(text) is None, f"SECRET_LITERAL:{command.get('command_id')}")
                require(PRIVATE_PATH.search(text) is None, f"PRIVATE_PATH_LITERAL:{command.get('command_id')}")
        for env in iter_env_refs(command):
            require(env in allow_set, f"ENV_NOT_ALLOWED:{env}")

    canary = next(x for x in items if x["item_id"] == "LH-P7-09-VERTICAL-CANARY").get("canary", {})
    require(canary == {"contract_digest": CANARY, "current_state": "PLAN_ONLY", "execution_receipt": None}, "CANARY_PROMOTION")

    require(schema.get("title") == "EAS Local Handoff Receipt v2", "RECEIPT_SCHEMA_TITLE")
    required = schema.get("required")
    require(isinstance(required, list) and set(first["required_receipt"]["required_fields"]).issubset(set(required)), "RECEIPT_SCHEMA_FIELDS")
    require(schema.get("properties", {}).get("result", {}).get("enum") == ["PASS", "FAIL", "BLOCKED", "NOT_EXERCISED", "UNKNOWN_EFFECT", "HUMAN_ADMIT_REQUIRED"], "RECEIPT_RESULT_ENUM")

    require(history.get("commit") == OLD_QUEUE[0] and history.get("tree") == OLD_QUEUE[1], "HISTORY_SUBJECT")
    require(history.get("disposition") == "SUPERSEDED_STALE_SUBJECT", "HISTORY_DISPOSITION")
    require(history.get("execution_receipt") is None and history.get("queue_execution") == "NOT_PERFORMED", "HISTORY_EXECUTION_PROMOTION")

    for token in (
        "P7 queue v2", "SUPERSEDED_STALE_SUBJECT", "exactly one `ACTIVE`",
        "89e12f5863c9bfd02bddb28de121d9c19cc25d16",
        "32272986158", "4974136248", "PLAN_ONLY", "NOT_PERFORMED",
    ):
        require(token in readme, f"README_ROUTE:{token}")

    require("canonical reducer" in queue.get("advance_rule", "").lower(), "REDUCER_ADVANCE_RULE")
    require("Queue-shape or command exit alone cannot advance state." in queue.get("advance_rule", ""), "NO_EXIT_CODE_ADVANCE")


def verify() -> None:
    validate(load(QUEUE_PATH), load(SCHEMA_PATH), load(HISTORY_PATH), README_PATH.read_text(encoding="utf-8"))
    print("PASS P7 queue-v2 items=11 active=1 blocked=9 human=1 execution=NOT_PERFORMED")


def must_refuse(label: str, mutate: Callable[[list[Any]], None]) -> None:
    args: list[Any] = [load(QUEUE_PATH), load(SCHEMA_PATH), load(HISTORY_PATH), README_PATH.read_text(encoding="utf-8")]
    mutate(args)
    try:
        validate(*args)
    except QueueError:
        return
    raise AssertionError(f"mutation accepted: {label}")


def selftest() -> None:
    tests: list[tuple[str, Callable[[list[Any]], None]]] = [
        ("two active", lambda a: a[0]["items"][1].update({"state": "ACTIVE"})),
        ("stale root-d", lambda a: a[0]["compiled_from"].update({"commit": "0" * 40})),
        ("old queue reactivated", lambda a: a[0]["supersedes"].update({"disposition": "ACTIVE"})),
        ("drop item", lambda a: a[0]["items"].pop(5)),
        ("break chain", lambda a: a[0]["items"][4].update({"blocked_by": ["wrong"]})),
        ("allow secrets", lambda a: a[0].update({"secret_values_allowed": True})),
        ("allow credentials", lambda a: a[0].update({"credential_values_allowed": True})),
        ("unsafe shell", lambda a: a[0]["items"][0]["commands"][0]["argv"].append({"literal": "echo x && rm -rf /"})),
        ("unlisted env", lambda a: a[0]["items"][0]["commands"][0].update({"cwd": {"env": "SECRET_HOME", "relative": "."}})),
        ("remove cleanup", lambda a: a[0]["items"][0].update({"cleanup": []})),
        ("remove receipt field", lambda a: a[0]["items"][0]["required_receipt"]["required_fields"].pop()),
        ("canary executed", lambda a: a[0]["items"][8]["canary"].update({"current_state": "EXECUTED", "execution_receipt": "x"})),
        ("queue executed", lambda a: a[0].update({"queue_execution": "PASS"})),
        ("shadow promoted", lambda a: a[0]["closure_projection"].update({"profile_shadow": "CLOSED"})),
        ("EAS-A invented", lambda a: a[0]["closure_projection"].update({"EAS_A": "IMPLEMENTED"})),
        ("closure credit", lambda a: a[0]["closure_projection"].update({"requirements_closure_credit": 15})),
        ("human auto-pass", lambda a: a[0]["items"][-1].update({"state": "PASS"})),
        ("history executed", lambda a: a[2].update({"queue_execution": "PASS", "execution_receipt": "fake"})),
    ]
    for label, mutate in tests:
        must_refuse(label, mutate)
    print(f"PASS P7 planted refusals={len(tests)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    selftest() if args.selftest else verify()
