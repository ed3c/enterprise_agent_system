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

ROOT_D = ("68828ec8de5f3ad5aa133a5c772eefb80c775568", "bf338e0cd959a2b97adee79af7459222bd5211b9")
GENERIC_X = ("8b1bfa38c103e1c064b8ef0aafecfc8f2a2642dc", "9c8fb0e8e25f357fdb695a94c4ab74fc3dcd4631")
PROFILE_X = ("fe2748e09a5222f439f09c5d0d71e486e1ade3e8", "0425916bea831c125702696544ae2848fdf9bd0e")
PROFILE_D = ("a7a034ef1db778fcee586fff8d8ff7848bc9a1ab", "62796ebb2e48e60ab30809470d3b6c02f44009fc")
OLD_QUEUE = ("9223107163b27984ed490246b4c0899caeb1bdae", "d462e2a1a69d225bf8161ce01918e5e8bb8d102f")
OLD_P7 = ("00b9ae644352485e4779102b1c3c2d18f6a7155c", "4effe7ce338753ee61972890f676700ad33c3e04")
CANARY = "sha256:7a881bbe4b2b9605d56838f5f1e9a3c76dbf45ebc1b0aa7a973fd1329f88efbb"

EXPECTED_IDS = [
    "LH-P7-01-ROOT-D-V2-LOCAL-READBACK",
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
    "queue_id","item_id","started_at","finished_at","subject_before","subject_after",
    "commands","exit_codes","stdout_digests","stderr_digests","observed_commit","observed_tree",
    "evidence_lane","result","dirty_state_before","dirty_state_after","residue_inventory",
    "cleanup_result","failures","retries","claims_not_proven","next_transition",
]
EXPECTED_CLOSURE = {
    "requirements_total": 15,
    "requirements_required_lane_satisfied": 1,
    "requirements_closure_credit": 0,
    "contradictions_total": 14,
    "contradictions_preserved": 14,
    "stronger_no_credit_lanes": 13,
    "profile_x_hosted_gate": "ABSENT",
    "full_architecture": "BLOCKED_FOR_CLOSURE",
    "vertical_canary": "PLAN_ONLY",
    "vertical_execution_receipt": None,
    "EAS_A": "NOT_IMPLEMENTED",
    "profile_release": "NOT_ADMITTED",
    "human_admission": "NOT_PERFORMED",
}
EXPECTED_ENVS = {
    "EAS_CHECKOUT","EAS_WORKTREES","EAS_RECEIPT_DIR","RUNTIME_ENV_CHECKOUT",
    "BETTOR_ARENA_CHECKOUT","AGENT_SHIELD_CHECKOUT","TRUTH_VERIFY_CHECKOUT",
}
STALE_CURRENT = {
    "89e12f5863c9bfd02bddb28de121d9c19cc25d16",
    "16e51462b2a0a693c1af92ad344fa3db6bbd4879",
    "3f8af3d75b28ca1904fe07b8ea9ee0d291f5989c",
    "690154a5f7154d551bef6942fe5d1f34091c2197",
    "2146c02c23bbf87b6797900141c491a53f6936714b0b620a23016a2b20eaab79",
}

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
    require(queue.get("schema_version") == "enterprise-agent-system/local-handoff-queue/v3", "QUEUE_SCHEMA")
    require(queue.get("queue_id") == "LH-EAS-INCEPTION-P7-V3-2026-08-20", "QUEUE_ID")
    require(queue.get("state") == "READY_FOR_LOCAL_EXECUTION_PREPARATION", "QUEUE_STATE")
    require(queue.get("queue_execution") == "NOT_PERFORMED", "FALSE_QUEUE_EXECUTION")
    require(queue.get("evidence_ceiling") == "P7_EXECUTABLE_QUEUE_PREPARATION_ONLY", "QUEUE_CEILING")
    require(queue.get("secret_values_allowed") is False, "SECRET_VALUES_ALLOWED")
    require(queue.get("credential_values_allowed") is False, "CREDENTIAL_VALUES_ALLOWED")
    require(queue.get("failed_blocked_retried_attempts_must_remain_visible") is True, "ATTEMPT_DENOMINATOR")

    compiled = queue.get("compiled_from", {})
    require((compiled.get("commit"), compiled.get("tree")) == ROOT_D, "ROOT_D_DRIFT")
    require(compiled.get("pull_request") == 57, "ROOT_D_PR")
    require(compiled.get("verification_run") == 32284239386, "ROOT_D_VERIFY_RUN")
    require(compiled.get("shadow_review") == 4975173485, "ROOT_D_SHADOW")
    require(compiled.get("p6_state") == "ADMIT_FOR_P7_PREPARATION", "P6_STATE")

    superseded = queue.get("superseded_candidates")
    require(isinstance(superseded, list) and len(superseded) == 2, "SUPERSEDED_DENOMINATOR")
    by_pr = {x.get("pull_request"): x for x in superseded}
    require(set(by_pr) == {27, 50}, "SUPERSEDED_PRS")
    require((by_pr[27].get("commit"), by_pr[27].get("tree")) == OLD_QUEUE, "OLD_QUEUE_SUBJECT")
    require((by_pr[50].get("commit"), by_pr[50].get("tree")) == OLD_P7, "OLD_P7_SUBJECT")
    require(all(x.get("authority") == "NONE" for x in superseded), "SUPERSEDED_AUTHORITY")
    require(by_pr[27].get("disposition") == "SUPERSEDED_STALE_SUBJECT", "OLD_QUEUE_DISPOSITION")
    require(by_pr[50].get("disposition") == "SUPERSEDED_STALE_ROOT_D", "OLD_P7_DISPOSITION")

    prompt = queue.get("p7_prompt", {})
    require(prompt.get("path") == "docs/prompts/P7-local-handoff-compiler.system.md", "P7_PROMPT_PATH")
    require(prompt.get("blob") == "6f200e6c4e7a6f4cb6ee68340b3b3f8a4361f55b", "P7_PROMPT_BLOB")
    require(prompt.get("source_commit") == ROOT_D[0], "P7_PROMPT_SOURCE")
    require(queue.get("closure_projection") == EXPECTED_CLOSURE, "CLOSURE_PROMOTION")

    allow = queue.get("environment_name_allowlist")
    require(isinstance(allow, list) and set(allow) == EXPECTED_ENVS and len(allow) == len(EXPECTED_ENVS), "ENV_ALLOWLIST")

    items = queue.get("items")
    require(isinstance(items, list) and [x.get("item_id") for x in items] == EXPECTED_IDS, "ITEM_DENOMINATOR")
    active = [x for x in items if x.get("state") == "ACTIVE"]
    require(len(active) == 1 and active[0].get("item_id") == queue.get("active_item_id") == EXPECTED_IDS[0], "ACTIVE_CARDINALITY")
    require(items[-1].get("state") == "HUMAN_ADMIT_REQUIRED", "HUMAN_TERMINAL_STATE")
    require(items[-1].get("required_evidence_lane") == "HUMAN_ADMIT", "HUMAN_TERMINAL_LANE")
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
    subject_rows = {x.get("subject_id"): x for x in first.get("subjects", [])}
    require(set(subject_rows) == {"ROOT-D","GENERIC-X","PROFILE-X","PROFILE-D"}, "ACTIVE_SUBJECT_DENOMINATOR")
    require((subject_rows["ROOT-D"].get("commit"), subject_rows["ROOT-D"].get("tree")) == ROOT_D, "ACTIVE_ROOT_D")
    require(subject_rows["ROOT-D"].get("verification_run") == 32284239386 and subject_rows["ROOT-D"].get("shadow_review") == 4975173485, "ACTIVE_ROOT_D_RECEIPTS")
    require((subject_rows["GENERIC-X"].get("commit"), subject_rows["GENERIC-X"].get("tree")) == GENERIC_X, "ACTIVE_GENERIC_X")
    require(subject_rows["GENERIC-X"].get("shadow_review") == 4973896050, "ACTIVE_GENERIC_X_SHADOW")
    require((subject_rows["PROFILE-X"].get("commit"), subject_rows["PROFILE-X"].get("tree")) == PROFILE_X, "ACTIVE_PROFILE_X")
    require(subject_rows["PROFILE-X"].get("shadow_review") == 4974017388 and subject_rows["PROFILE-X"].get("hosted_gate") == "ABSENT", "ACTIVE_PROFILE_X_RECEIPTS")
    require((subject_rows["PROFILE-D"].get("commit"), subject_rows["PROFILE-D"].get("tree")) == PROFILE_D, "ACTIVE_PROFILE_D")
    require(subject_rows["PROFILE-D"].get("verification_run") == 32282726313 and subject_rows["PROFILE-D"].get("shadow_review") == 4975046170, "ACTIVE_PROFILE_D_RECEIPTS")

    commands = first.get("commands")
    require(isinstance(commands, list) and [x.get("command_id") for x in commands] == [
        "FETCH_ROOT_D","CREATE_ROOT_D_WORKTREE","ASSERT_ROOT_D_SUBJECT","REPLAY_GENERIC_X",
        "REPLAY_PROFILE_X","REPLAY_PROFILE_X_MUTATIONS","REPLAY_PROFILE_D",
        "REPLAY_PROFILE_D_MUTATIONS","ASSERT_ROOT_D_PROJECTION",
    ], "ACTIVE_COMMANDS")
    cleanup = first.get("cleanup")
    require(isinstance(cleanup, list) and [x.get("command_id") for x in cleanup] == [
        "REMOVE_ROOT_D_WORKTREE","PRUNE_WORKTREES","DELETE_TEMP_ROOT_D_REF"
    ], "CLEANUP_ORDER")

    command_text = json.dumps(commands, sort_keys=True)
    require("agent/eas-d-final-docs-convergence-v2:refs/remotes/origin/p7-root-d-v2" in command_text, "ROOT_D_FETCH_REF")
    require(ROOT_D[0] in command_text and ROOT_D[1] in command_text, "ROOT_D_ASSERT_BINDING")
    require("verify_profile_convergence_mutations.py" in command_text, "PROFILE_X_MUTATION_REPLAY")
    require("--skip-git-context" in command_text, "PROFILE_D_CHILD_COMPOSITION")
    require("ROOT_D_V2_CANDIDATE" in command_text and "BLOCKED_PENDING_CURRENT_ROOT_D_RECEIPT" in command_text, "ROOT_D_PROJECTION_ASSERTION")

    receipt = first.get("required_receipt", {})
    require(receipt.get("schema") == "handoff/local-handoff-receipt.schema.json", "RECEIPT_SCHEMA_ROUTE")
    require(receipt.get("required_fields") == RECEIPT_FIELDS, "RECEIPT_FIELDS")
    require(receipt.get("path", {}).get("relative") == "LH-P7-01-ROOT-D-V2-LOCAL-READBACK.json", "RECEIPT_PATH")
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
            require(env in EXPECTED_ENVS, f"ENV_NOT_ALLOWED:{env}")

    canary = items[8].get("canary", {})
    require(canary == {"contract_digest": CANARY, "current_state": "PLAN_ONLY", "execution_receipt": None}, "CANARY_PROMOTION")

    require(schema.get("title") == "EAS Local Handoff Receipt v2", "SCHEMA_TITLE")
    require(set(RECEIPT_FIELDS).issubset(set(schema.get("required", []))), "SCHEMA_REQUIRED")
    require(schema.get("properties", {}).get("result", {}).get("enum") == ["PASS","FAIL","BLOCKED","NOT_EXERCISED","UNKNOWN_EFFECT","HUMAN_ADMIT_REQUIRED"], "RESULT_ENUM")

    require((history.get("commit"), history.get("tree")) == OLD_QUEUE, "HISTORY_SUBJECT")
    require(history.get("disposition") == "SUPERSEDED_STALE_SUBJECT", "HISTORY_DISPOSITION")
    require(history.get("execution_receipt") is None and history.get("queue_execution") == "NOT_PERFORMED", "HISTORY_EXECUTION")

    serialized = json.dumps(queue, sort_keys=True)
    for stale in STALE_CURRENT:
        require(stale not in serialized, f"STALE_CURRENT_AUTHORITY:{stale}")

    for token in (
        "P7 queue v3","exactly one `ACTIVE`",ROOT_D[0],"32284239386","4975173485",
        "PLAN_ONLY","NOT_PERFORMED","authority NONE","PR #50",
    ):
        require(token in readme, f"README:{token}")

    require("canonical reducer" in queue.get("advance_rule", "").lower(), "ADVANCE_RULE_REDUCER")
    require("command exit alone cannot advance" in queue.get("advance_rule", ""), "ADVANCE_RULE_EXIT")

def verify() -> None:
    validate(load(QUEUE_PATH), load(SCHEMA_PATH), load(HISTORY_PATH), README_PATH.read_text(encoding="utf-8"))
    print("PASS P7 queue-v3 items=11 active=1 blocked=9 human=1 commands=9 cleanup=3 execution=NOT_PERFORMED")

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
        ("wrong root verify", lambda a: a[0]["compiled_from"].update({"verification_run": 1})),
        ("wrong root shadow", lambda a: a[0]["compiled_from"].update({"shadow_review": 1})),
        ("old p7 authority", lambda a: a[0]["superseded_candidates"][1].update({"authority": "CURRENT"})),
        ("drop superseded", lambda a: a[0]["superseded_candidates"].pop()),
        ("drop item", lambda a: a[0]["items"].pop(5)),
        ("break chain", lambda a: a[0]["items"][4].update({"blocked_by": ["wrong"]})),
        ("allow secrets", lambda a: a[0].update({"secret_values_allowed": True})),
        ("allow credentials", lambda a: a[0].update({"credential_values_allowed": True})),
        ("unsafe shell", lambda a: a[0]["items"][0]["commands"][0]["argv"].append({"literal": "echo x && rm -rf /"})),
        ("unlisted env", lambda a: a[0]["items"][0]["commands"][0].update({"cwd": {"env": "SECRET_HOME", "relative": "."}})),
        ("remove cleanup", lambda a: a[0]["items"][0]["cleanup"].pop()),
        ("remove receipt field", lambda a: a[0]["items"][0]["required_receipt"]["required_fields"].pop()),
        ("wrong fetch ref", lambda a: a[0]["items"][0]["commands"][0]["argv"][-1].update({"literal": "old-branch"})),
        ("wrong rollback", lambda a: a[0]["items"][0]["rollback_subject"].update({"commit": "1" * 40})),
        ("canary executed", lambda a: a[0]["items"][8]["canary"].update({"current_state": "EXECUTED", "execution_receipt": "x"})),
        ("old canary digest", lambda a: a[0]["items"][8]["canary"].update({"contract_digest": "sha256:" + "0" * 64})),
        ("queue executed", lambda a: a[0].update({"queue_execution": "PASS"})),
        ("closure credit", lambda a: a[0]["closure_projection"].update({"requirements_closure_credit": 15})),
        ("profile-x gate promoted", lambda a: a[0]["closure_projection"].update({"profile_x_hosted_gate": "PASS"})),
        ("full architecture promoted", lambda a: a[0]["closure_projection"].update({"full_architecture": "PASS"})),
        ("EAS-A invented", lambda a: a[0]["closure_projection"].update({"EAS_A": "IMPLEMENTED"})),
        ("human auto-pass", lambda a: a[0]["items"][-1].update({"state": "PASS"})),
        ("history executed", lambda a: a[2].update({"queue_execution": "PASS", "execution_receipt": "fake"})),
        ("old root in active subject", lambda a: a[0]["items"][0]["subjects"][0].update({"commit": "89e12f5863c9bfd02bddb28de121d9c19cc25d16"})),
        ("profile-d receipt drift", lambda a: a[0]["items"][0]["subjects"][3].update({"verification_run": 1})),
        ("missing p7 prompt", lambda a: a[0]["p7_prompt"].update({"source_commit": "0" * 40})),
    ]
    for label, mutate in tests:
        must_refuse(label, mutate)
    print(f"PASS P7 planted refusals={len(tests)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    selftest() if args.selftest else verify()
