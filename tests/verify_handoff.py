#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "handoff/local-handoff-queue.json"
SCHEMA_PATH = ROOT / "handoff/local-handoff-receipt.schema.json"
HISTORY_PATH = ROOT / "handoff/history/LH-EAS-INCEPTION-2026-08-18-superseded.json"
README_PATH = ROOT / "handoff/README.md"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
UNSAFE_SHELL = re.compile(r"(?:&&|\|\||`|\$\(|\n|\r)")
SECRET_ASSIGNMENT = re.compile(r"(?i)(password|secret|token|cookie|session)\s*[:=]\s*\S{4,}")
PRIVATE_PATH = re.compile(r"(?:/Users/|/home/|/mnt/data/)")

ROOT_D = ("6981c700f9f2f9128ebeebdf80e627178b2be336", "d044ae652b65af6a0aba49f0f79c7c04c630bebf")
GENERIC_X = ("b295eabec7b4c9d4e1f65f7fb0238034f454ae7f", "25bd4c7e934690b3ac15692ba04af4418a46b1f2")
PROFILE_X = ("df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0", "9290a2822ba30309a9d44933ce0ea4d640501a39")
PROFILE_D = ("f04f9fc78270c8f97ce978e2ccc161ab4d724ca4", "9740f25f9b1fa8f6533c49642381955b953dd12a")
EAS_A = ("250717db1cad584d50890c0d851153fa2cd755e8", "fbf6a75b6e89e906f227110dc5a61e4355b8a891")
OLD_QUEUE = ("9223107163b27984ed490246b4c0899caeb1bdae", "d462e2a1a69d225bf8161ce01918e5e8bb8d102f")
CANARY = "sha256:869842575cae80c62227699f576728f3331fa25a573a3cc27c052f23f32944c2"
EXPECTED_IDS = [
    "LH-P7-01-ROOT-D-V3-LOCAL-READBACK",
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


def load(path: Path) -> dict[str, Any]:
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
    require(queue.get("schema_version") == "enterprise-agent-system/local-handoff-queue/v4", "QUEUE_SCHEMA")
    require(queue.get("queue_id") == "LH-EAS-INCEPTION-P7-V4-2026-08-20", "QUEUE_ID")
    require(queue.get("state") == "READY_FOR_LOCAL_EXECUTION_PREPARATION", "QUEUE_STATE")
    require(queue.get("queue_execution") == "NOT_PERFORMED", "FALSE_QUEUE_EXECUTION")
    require(queue.get("evidence_ceiling") == "P7_EXECUTABLE_QUEUE_PREPARATION_ONLY", "QUEUE_CEILING")
    require(queue.get("secret_values_allowed") is False and queue.get("credential_values_allowed") is False, "SECRET_OR_CREDENTIAL_VALUES")
    require(queue.get("failed_blocked_retried_attempts_must_remain_visible") is True, "ATTEMPT_DENOMINATOR")

    compiled = queue.get("compiled_from", {})
    require((compiled.get("commit"), compiled.get("tree")) == ROOT_D, "ROOT_D_DRIFT")
    require(compiled.get("pull_request") == 94, "ROOT_D_PR")
    require(compiled.get("verification_run") == 32342272177, "ROOT_D_VERIFY")
    require(compiled.get("shadow_review") == 4979950874, "ROOT_D_SHADOW")
    require(compiled.get("p6_state") == "ADMIT_FOR_P7_REBIND_AFTER_EAS_A", "P6_STATE")

    eas = queue.get("eas_a", {})
    require((eas.get("commit"), eas.get("tree")) == EAS_A, "EAS_A_SUBJECT")
    require(eas.get("authority") == "ADVISORY_ONLY", "EAS_A_AUTHORITY")
    require(eas.get("relationship") == "PROCESS_DEPENDENCY_NOT_GIT_PARENT", "EAS_A_RELATIONSHIP")
    require(eas.get("google_connectivity") == "NOT_PERFORMED", "GOOGLE_CONNECTIVITY")
    require(eas.get("google_write") == "NOT_PERFORMED", "GOOGLE_WRITE")
    require(eas.get("source_correctness") == "NOT_PROVEN", "SOURCE_CORRECTNESS")

    superseded = queue.get("superseded_candidates", [])
    require([x.get("pull_request") for x in superseded] == [27, 50, 59], "SUPERSEDED_QUEUE_DENOMINATOR")
    require(all(x.get("authority") == "NONE" for x in superseded), "SUPERSEDED_QUEUE_AUTHORITY")
    downstream = queue.get("superseded_downstream", [])
    require([x.get("pull_request") for x in downstream] == [67, 71], "SUPERSEDED_DOWNSTREAM_DENOMINATOR")
    require(all(x.get("authority") == "NONE" for x in downstream), "SUPERSEDED_DOWNSTREAM_AUTHORITY")

    projection = queue.get("closure_projection", {})
    require(projection == {
        "requirements_total": 15,
        "requirements_required_lane_satisfied": 1,
        "requirements_closure_credit": 0,
        "contradictions_total": 14,
        "contradictions_preserved": 14,
        "stronger_no_credit_lanes": 13,
        "full_architecture": "BLOCKED_FOR_CLOSURE",
        "vertical_canary": "PLAN_ONLY",
        "vertical_canary_digest": CANARY,
        "vertical_execution_receipt": None,
        "profile_release": "NOT_ADMITTED",
        "human_admission": "NOT_PERFORMED",
    }, "CLOSURE_PROJECTION")

    prompt = queue.get("p7_prompt", {})
    require(prompt.get("path") == "docs/prompts/P7-local-handoff-compiler.system.md", "P7_PROMPT_PATH")
    require(prompt.get("blob") == "364b07078f9d29b67e03270eb04454ddcf997184", "P7_PROMPT_BLOB")
    require(prompt.get("source_commit") == ROOT_D[0], "P7_PROMPT_SOURCE")

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
    subjects = {x.get("subject_id"): x for x in first.get("subjects", [])}
    require((subjects["ROOT-D"].get("commit"), subjects["ROOT-D"].get("tree")) == ROOT_D, "ACTIVE_ROOT_D")
    require((subjects["GENERIC-X"].get("commit"), subjects["GENERIC-X"].get("tree")) == GENERIC_X, "ACTIVE_GENERIC_X")
    require((subjects["PROFILE-X"].get("commit"), subjects["PROFILE-X"].get("tree")) == PROFILE_X, "ACTIVE_PROFILE_X")
    require((subjects["PROFILE-D"].get("commit"), subjects["PROFILE-D"].get("tree")) == PROFILE_D, "ACTIVE_PROFILE_D")
    require((subjects["EAS-A"].get("commit"), subjects["EAS-A"].get("tree")) == EAS_A, "ACTIVE_EAS_A")
    require(subjects["EAS-A"].get("authority") == "ADVISORY_ONLY" and subjects["EAS-A"].get("relationship") == "PROCESS_DEPENDENCY_NOT_GIT_PARENT", "ACTIVE_EAS_A_AUTHORITY")

    commands = first.get("commands")
    require(isinstance(commands, list) and len(commands) == 9, "ACTIVE_COMMANDS")
    require([x.get("command_id") for x in commands] == [
        "FETCH_ROOT_D", "CREATE_ROOT_D_WORKTREE", "ASSERT_ROOT_D_SUBJECT", "REPLAY_GENERIC_X",
        "REPLAY_PROFILE_X", "REPLAY_PROFILE_X_MUTATIONS", "REPLAY_PROFILE_D",
        "REPLAY_PROFILE_D_MUTATIONS", "ASSERT_ROOT_D_PROJECTION",
    ], "ACTIVE_COMMAND_ORDER")
    cleanup = first.get("cleanup")
    require(isinstance(cleanup, list) and [x.get("command_id") for x in cleanup] == [
        "REMOVE_ROOT_D_WORKTREE", "PRUNE_WORKTREES", "DELETE_TEMP_ROOT_D_REF"
    ], "CLEANUP_ORDER")
    require("p7-root-d-v3" in str(cleanup[-1].get("argv")), "TEMP_REF_CLEANUP")
    receipt = first.get("required_receipt", {})
    require(receipt.get("schema") == "handoff/local-handoff-receipt.schema.json", "RECEIPT_SCHEMA_ROUTE")
    require(receipt.get("required_fields") == RECEIPT_FIELDS, "RECEIPT_FIELDS")
    require((first.get("rollback_subject", {}).get("commit"), first.get("rollback_subject", {}).get("tree")) == ROOT_D, "ROLLBACK_SUBJECT")

    for command in commands + cleanup:
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

    for token in (
        "P7 queue v4", "exactly-one-ACTIVE", ROOT_D[0], "32342272177", "4979950874",
        "ADVISORY_ONLY", "PLAN_ONLY", "NOT_PERFORMED", "authority NONE",
    ):
        require(token in readme, f"README:{token}")
    require("canonical reducer" in queue.get("advance_rule", "").lower() and "command exit alone cannot advance" in queue.get("advance_rule", ""), "ADVANCE_RULE")


def verify() -> None:
    validate(load(QUEUE_PATH), load(SCHEMA_PATH), load(HISTORY_PATH), README_PATH.read_text(encoding="utf-8"))
    print("PASS P7 queue-v4 items=11 active=1 blocked=9 human=1 commands=9 cleanup=3 execution=NOT_PERFORMED")


def must_refuse(label: str, mutate: Callable[[list[Any]], None]) -> None:
    args: list[Any] = [load(QUEUE_PATH), load(SCHEMA_PATH), load(HISTORY_PATH), README_PATH.read_text(encoding="utf-8")]
    mutate(args)
    try:
        validate(*args)
    except QueueError:
        return
    raise AssertionError(f"mutation accepted: {label}")


def selftest() -> None:
    cases: list[tuple[str, Callable[[list[Any]], None]]] = [
        ("two active", lambda a: a[0]["items"][1].update({"state": "ACTIVE"})),
        ("stale root-d", lambda a: a[0]["compiled_from"].update({"commit": "0" * 40})),
        ("root verify drift", lambda a: a[0]["compiled_from"].update({"verification_run": 1})),
        ("root shadow drift", lambda a: a[0]["compiled_from"].update({"shadow_review": 1})),
        ("eas-a canonical", lambda a: a[0]["eas_a"].update({"authority": "CANONICAL"})),
        ("eas-a git parent", lambda a: a[0]["eas_a"].update({"relationship": "GIT_PARENT"})),
        ("google connectivity", lambda a: a[0]["eas_a"].update({"google_connectivity": "PASS"})),
        ("google write", lambda a: a[0]["eas_a"].update({"google_write": "PASS"})),
        ("source correctness", lambda a: a[0]["eas_a"].update({"source_correctness": "SUPPORTED"})),
        ("old queue authority", lambda a: a[0]["superseded_candidates"][2].update({"authority": "CURRENT"})),
        ("old runner authority", lambda a: a[0]["superseded_downstream"][0].update({"authority": "CURRENT"})),
        ("drop item", lambda a: a[0]["items"].pop(5)),
        ("break chain", lambda a: a[0]["items"][4].update({"blocked_by": ["wrong"]})),
        ("allow secrets", lambda a: a[0].update({"secret_values_allowed": True})),
        ("allow credentials", lambda a: a[0].update({"credential_values_allowed": True})),
        ("unsafe shell", lambda a: a[0]["items"][0]["commands"][0]["argv"].append({"literal": "echo x && rm -rf /"})),
        ("unlisted env", lambda a: a[0]["items"][0]["commands"][0].update({"cwd": {"env": "SECRET_HOME", "relative": "."}})),
        ("drop main command", lambda a: a[0]["items"][0]["commands"].pop()),
        ("remove cleanup", lambda a: a[0]["items"][0]["cleanup"].pop()),
        ("remove receipt field", lambda a: a[0]["items"][0]["required_receipt"]["required_fields"].pop()),
        ("canary executed", lambda a: a[0]["items"][8]["canary"].update({"current_state": "EXECUTED", "execution_receipt": "fake"})),
        ("canary digest", lambda a: a[0]["items"][8]["canary"].update({"contract_digest": "sha256:" + "0" * 64})),
        ("queue executed", lambda a: a[0].update({"queue_execution": "PASS"})),
        ("closure credit", lambda a: a[0]["closure_projection"].update({"requirements_closure_credit": 15})),
        ("required lane promotion", lambda a: a[0]["closure_projection"].update({"requirements_required_lane_satisfied": 15})),
        ("contradiction loss", lambda a: a[0]["closure_projection"].update({"contradictions_total": 13})),
        ("stronger loss", lambda a: a[0]["closure_projection"].update({"stronger_no_credit_lanes": 12})),
        ("full closure", lambda a: a[0]["closure_projection"].update({"full_architecture": "PASS"})),
        ("release", lambda a: a[0]["closure_projection"].update({"profile_release": "ADMITTED"})),
        ("human auto-pass", lambda a: a[0]["items"][-1].update({"state": "PASS"})),
        ("history executed", lambda a: a[2].update({"queue_execution": "PASS", "execution_receipt": "fake"})),
        ("active root subject drift", lambda a: a[0]["items"][0]["subjects"][0].update({"tree": "0" * 40})),
        ("active eas-a widening", lambda a: a[0]["items"][0]["subjects"][4].update({"authority": "CANONICAL"})),
        ("rollback drift", lambda a: a[0]["items"][0]["rollback_subject"].update({"commit": "0" * 40})),
    ]
    for label, mutate in cases:
        must_refuse(label, mutate)
    require(len(cases) == 34, "SELFTEST_DENOMINATOR")
    print("PASS P7 queue-v4 planted refusals=34/34")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    selftest() if args.selftest else verify()
