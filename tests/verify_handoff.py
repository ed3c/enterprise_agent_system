#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
from typing import Any, Callable

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "handoff/local-handoff-queue.json"
SCHEMA_PATH = ROOT / "handoff/local-handoff-receipt.schema.json"
HISTORY_PATH = ROOT / "handoff/history/LH-EAS-INCEPTION-2026-08-18-superseded.json"
README_PATH = ROOT / "handoff/README.md"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
UNSAFE_SHELL = re.compile(r"(?:&&|\|\||`|\$\(|\n|\r)")
SECRET_ASSIGNMENT = re.compile(r"(?i)(password|secret|token|cookie|session)\s*[:=]\s*\S{4,}")
PRIVATE_PATH = re.compile(r"(?:/Users/|/home/|/mnt/data/)")

ROOT_D = ("89e12f5863c9bfd02bddb28de121d9c19cc25d16", "16e51462b2a0a693c1af92ad344fa3db6bbd4879")
OLD_QUEUE = ("9223107163b27984ed490246b4c0899caeb1bdae", "d462e2a1a69d225bf8161ce01918e5e8bb8d102f")
GENERIC_X = ("3f8af3d75b28ca1904fe07b8ea9ee0d291f5989c", "e1be41234ff336297ce591b564291c9a0cd819ed")
PROFILE_D = ("690154a5f7154d551bef6942fe5d1f34091c2197", "1a2e02d4c92b882f51f8c8d28f70771648a6a528")
CANARY = "sha256:2146c02c23bbf87b6797900141c491a53f6936714b0b620a23016a2b20eaab79"
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
RECEIPT_FIELDS = [
    "queue_id", "item_id", "started_at", "finished_at", "subject_before", "subject_after",
    "commands", "exit_codes", "stdout_digests", "stderr_digests", "observed_commit", "observed_tree",
    "evidence_lane", "result", "dirty_state_before", "dirty_state_after", "residue_inventory",
    "cleanup_result", "failures", "retries", "claims_not_proven", "next_transition",
]


class QueueError(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise QueueError(reason)


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"NOT_OBJECT:{path}")
    return value


def sha(value: Any, reason: str) -> None:
    require(isinstance(value, str) and SHA40.fullmatch(value) is not None, reason)


def env_refs(value: Any):
    if isinstance(value, dict):
        if set(value) == {"env", "relative"}:
            yield value["env"]
        if isinstance(value.get("env_path"), dict):
            yield value["env_path"].get("env")
        for child in value.values():
            yield from env_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from env_refs(child)


def validate(queue: dict[str, Any], schema: dict[str, Any], history: dict[str, Any], readme: str) -> None:
    require(queue.get("schema_version") == "enterprise-agent-system/local-handoff-queue/v2", "QUEUE_SCHEMA")
    require(queue.get("queue_id") == "LH-EAS-INCEPTION-P7-2026-08-20", "QUEUE_ID")
    require(queue.get("state") == "READY_FOR_LOCAL_EXECUTION_PREPARATION", "QUEUE_STATE")
    require(queue.get("queue_execution") == "NOT_PERFORMED", "FALSE_QUEUE_EXECUTION")
    require(queue.get("evidence_ceiling") == "P7_EXECUTABLE_QUEUE_PREPARATION_ONLY", "QUEUE_CEILING")
    require(queue.get("secret_values_allowed") is False and queue.get("credential_values_allowed") is False, "SECRET_OR_CREDENTIAL_VALUES")
    require(queue.get("failed_blocked_retried_attempts_must_remain_visible") is True, "ATTEMPT_DENOMINATOR")

    compiled = queue.get("compiled_from", {})
    require((compiled.get("commit"), compiled.get("tree")) == ROOT_D, "ROOT_D_DRIFT")
    require(compiled.get("verification_run") == 32272986158 and compiled.get("shadow_review") == 4974136248, "P6_RECEIPTS")
    require(compiled.get("p6_state") == "COMPLETE_AT_DOCS_CEILING", "P6_STATE")

    old = queue.get("supersedes", {})
    require((old.get("commit"), old.get("tree")) == OLD_QUEUE, "OLD_QUEUE_SUBJECT")
    require(old.get("previous_active_item") == "LH-INCEPTION-SOURCE-01", "OLD_ACTIVE")
    require(old.get("disposition") == "SUPERSEDED_STALE_SUBJECT" and "60f994f" in old.get("reason", ""), "OLD_QUEUE_NOT_SUPERSEDED")

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
    require(isinstance(allow, list) and len(allow) == 7 and len(set(allow)) == 7, "ENV_ALLOWLIST")
    allow_set = set(allow)

    items = queue.get("items")
    require(isinstance(items, list) and [x.get("item_id") for x in items] == EXPECTED_IDS, "ITEM_DENOMINATOR")
    active = [x for x in items if x.get("state") == "ACTIVE"]
    require(len(active) == 1 and active[0].get("item_id") == queue.get("active_item_id") == EXPECTED_IDS[0], "ACTIVE_CARDINALITY")
    require(items[-1].get("state") == "HUMAN_ADMIT_REQUIRED" and items[-1].get("required_evidence_lane") == "HUMAN_ADMIT", "HUMAN_TERMINAL")
    require("commands" not in items[-1], "HUMAN_AUTO_COMMANDS")

    for index, item in enumerate(items):
        require(item.get("owner_issue", "").startswith("https://github.com/ed3c/enterprise_agent_system/issues/"), f"OWNER:{index}")
        require(item.get("claims_not_proven"), f"CLAIMS:{index}")
        if index:
            require(item.get("blocked_by") == [items[index - 1]["item_id"]], f"CHAIN:{index}")
            if index < len(items) - 1:
                require(item.get("state") == "BLOCKED_BY_PREDECESSOR", f"BLOCKED:{index}")
                require(item.get("resolver", {}).get("requires"), f"RESOLVER:{index}")
        if item.get("subject"):
            sha(item["subject"].get("commit"), f"SUBJECT_COMMIT:{index}")
            sha(item["subject"].get("tree"), f"SUBJECT_TREE:{index}")

    first = items[0]
    require(first.get("required_evidence_lane") == "LOCAL_DETERMINISTIC", "ACTIVE_LANE")
    bound = {x.get("subject_id"): (x.get("commit"), x.get("tree")) for x in first.get("subjects", [])}
    require(bound == {"ROOT-D": ROOT_D, "GENERIC-X": GENERIC_X, "PROFILE-D": PROFILE_D}, "ACTIVE_SUBJECTS")
    commands = first.get("commands")
    require(isinstance(commands, list) and len(commands) == 8, "ACTIVE_COMMANDS")
    require(isinstance(first.get("cleanup"), list) and len(first["cleanup"]) == 2, "ACTIVE_CLEANUP")
    receipt = first.get("required_receipt", {})
    require(receipt.get("schema") == "handoff/local-handoff-receipt.schema.json", "RECEIPT_SCHEMA_ROUTE")
    require(receipt.get("required_fields") == RECEIPT_FIELDS, "RECEIPT_FIELDS")
    require((first.get("rollback_subject", {}).get("commit"), first.get("rollback_subject", {}).get("tree")) == ROOT_D, "ROLLBACK_SUBJECT")

    for command in commands + first["cleanup"]:
        require(isinstance(command.get("timeout_seconds"), int) and 0 < command["timeout_seconds"] <= 1800, f"TIMEOUT:{command.get('command_id')}")
        argv = command.get("argv")
        require(isinstance(argv, list) and argv, f"ARGV:{command.get('command_id')}")
        for arg in argv:
            require(isinstance(arg, dict) and len(arg) == 1, f"ARGV_SHAPE:{command.get('command_id')}")
            if "literal" in arg:
                text = arg["literal"]
                require(isinstance(text, str), "ARGV_LITERAL")
                require(UNSAFE_SHELL.search(text) is None, f"UNSAFE_SHELL:{command.get('command_id')}")
                require(SECRET_ASSIGNMENT.search(text) is None, f"SECRET_LITERAL:{command.get('command_id')}")
                require(PRIVATE_PATH.search(text) is None, f"PRIVATE_PATH:{command.get('command_id')}")
        for env in env_refs(command):
            require(env in allow_set, f"ENV_NOT_ALLOWED:{env}")

    canary = items[8].get("canary", {})
    require(canary == {"contract_digest": CANARY, "current_state": "PLAN_ONLY", "execution_receipt": None}, "CANARY_PROMOTION")

    require(schema.get("title") == "EAS Local Handoff Receipt v2", "SCHEMA_TITLE")
    require(set(RECEIPT_FIELDS).issubset(set(schema.get("required", []))), "SCHEMA_REQUIRED")
    require(schema.get("properties", {}).get("result", {}).get("enum") == ["PASS", "FAIL", "BLOCKED", "NOT_EXERCISED", "UNKNOWN_EFFECT", "HUMAN_ADMIT_REQUIRED"], "RESULT_ENUM")

    require((history.get("commit"), history.get("tree")) == OLD_QUEUE, "HISTORY_SUBJECT")
    require(history.get("disposition") == "SUPERSEDED_STALE_SUBJECT", "HISTORY_DISPOSITION")
    require(history.get("execution_receipt") is None and history.get("queue_execution") == "NOT_PERFORMED", "HISTORY_EXECUTION")

    for token in ("P7 queue v2", "SUPERSEDED_STALE_SUBJECT", "exactly one `ACTIVE`", ROOT_D[0], "32272986158", "4974136248", "PLAN_ONLY", "NOT_PERFORMED"):
        require(token in readme, f"README:{token}")
    require("canonical reducer" in queue.get("advance_rule", "").lower() and "command exit alone cannot advance" in queue.get("advance_rule", ""), "ADVANCE_RULE")


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
