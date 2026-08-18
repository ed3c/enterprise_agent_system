#!/usr/bin/env python3
"""Deterministic Tech Lead gate for the Agent Thinking Inception profile DAG."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pathlib
import re
import sys
from collections.abc import Callable
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[4]
PROFILE = ROOT / "profiles" / "agent-thinking-inception"
ORCHESTRATION = PROFILE / "orchestration"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ORCHESTRATION))

from enterprise_agent_system.orchestration import (  # noqa: E402
    HUMAN_ONLY,
    assert_disjoint_leases,
    compile_prompt_packet,
    topological_waves,
    validate_exact_subject,
    validate_prompt_packet,
    validate_run,
)
from compile_profile_packets import compile_packets  # noqa: E402

INPUT_PATH = ORCHESTRATION / "profile-input-binding.json"
RUN_PATH = ORCHESTRATION / "profile-run.json"
CAPABILITY_PATH = ORCHESTRATION / "profile-capability-plan.json"
SPECS_PATH = ORCHESTRATION / "profile-worker-packet-specs.json"
STACK_PATH = ORCHESTRATION / "profile-molecular-stack-index.json"

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REPOSITORY = re.compile(r"^[^/\s]+/[^/\s]+$")
ISSUE = re.compile(
    r"^https://github\.com/ed3c/enterprise_agent_system/issues/[1-9][0-9]*$"
)
SECRET_OR_PRIVATE = re.compile(
    r"(?i)(PRIVATE KEY|(?:password|secret|token|cookie|session)\s*[:=]\s*\S{6,}"
    r"|/Users/|/home/|/mnt/data/|gemini\.google\.com/app/)"
)

EXACT = {
    "eas_c": {
        "repository": "ed3c/enterprise_agent_system",
        "commit": "ac0a7645392f689ae488328a53e7b6f3bb6ad02d",
        "tree": "51c94cb43ed1e4a3a3ac05e42838532c3ec2e598",
    },
    "eas_k": {
        "repository": "ed3c/enterprise_agent_system",
        "commit": "b1362f48b6edc0b4cd6d301da2a5d0e94d970f8c",
        "tree": "19353937e8d642a0bd731e20b3f61ffa3af2b913",
    },
    "profile_c0": {
        "repository": "ed3c/enterprise_agent_system",
        "commit": "1f0d196c19b7fa4505894ff1fb8b27cd33c5fb9f",
        "tree": "924967e5fb51dad8ad09e321109063d4f7b2ec70",
    },
    "profile_c1": {
        "repository": "ed3c/enterprise_agent_system",
        "commit": "1977c015cd2b85eb350deae6d39018ba5437a482",
        "tree": "7bed929490035f7431547fe22eb8201cd71dae50",
    },
    "profile_k_base": {
        "repository": "ed3c/enterprise_agent_system",
        "commit": "1474882226fff6078afe467731db5adec9a09a50",
        "tree": "3aadb4377d9596823b070f996a5f94ccb8f05220",
    },
    "shadow_preflight": {
        "repository": "ed3c/enterprise_agent_system",
        "commit": "177ba870c41cc5605532ea79770d54aea124fa0c",
        "tree": "20073aa3b719f30c95a6cbf449f0d6a2144f71c3",
    },
}
SOURCE_DIGEST = (
    "sha256:a6f1245ff865cae24838ed8ec4828330be684f3c03b29b9064ade8bfac94d8da"
)
CONTRACT_DIGEST = (
    "sha256:f19249d8e40fbf0c6db6f71ed943192cfc4debe097cd7b517164a159c0c040bf"
)

TASK_K = "TASK-INCEPTION-K"
A_TASKS = {
    "TASK-INCEPTION-A1",
    "TASK-INCEPTION-A2",
    "TASK-INCEPTION-A3",
    "TASK-INCEPTION-A4",
    "TASK-INCEPTION-A5",
    "TASK-INCEPTION-A6",
}
PACKET_TASKS = A_TASKS | {
    "TASK-INCEPTION-E",
    "TASK-INCEPTION-X",
    "TASK-INCEPTION-D",
    "TASK-INCEPTION-H",
}
EXPECTED_TASKS = PACKET_TASKS | {TASK_K}
EXPECTED_WAVES = [
    [TASK_K],
    sorted(A_TASKS),
    ["TASK-INCEPTION-E"],
    ["TASK-INCEPTION-X"],
    ["TASK-INCEPTION-D"],
    ["TASK-INCEPTION-H"],
]
LANES = {
    "TASK-INCEPTION-A1": "LOCAL",
    "TASK-INCEPTION-A2": "LOCAL",
    "TASK-INCEPTION-A3": "PRIVATE",
    "TASK-INCEPTION-A4": "HUMAN",
    "TASK-INCEPTION-A5": "HUMAN",
    "TASK-INCEPTION-A6": "LOCAL",
    "TASK-INCEPTION-E": "CLOUD",
    "TASK-INCEPTION-X": "CLOUD",
    "TASK-INCEPTION-D": "CLOUD",
    "TASK-INCEPTION-H": "LOCAL",
}
OWNER_MAP = {
    "TASK-INCEPTION-A1": (
        "ed3c/bettor-arena",
        "inception/domain-state-compaction",
        5,
    ),
    "TASK-INCEPTION-A2": (
        "ed3c/agent-shield-monorepo",
        "inception/runtime-sandbox-steering",
        7,
    ),
    "TASK-INCEPTION-A3": (
        "ed3c/truth-verify-loop",
        "inception/code-source-citation-evidence",
        15,
    ),
    "TASK-INCEPTION-A4": (
        "ed3c/enterprise_agent_system",
        "inception/four-tier-provenance",
        16,
    ),
    "TASK-INCEPTION-A5": (
        "ed3c/bettor-arena",
        "inception/discovery-admission",
        17,
    ),
    "TASK-INCEPTION-A6": (
        "ed3c/bettor-arena",
        "inception/ingress-effect-writeback",
        18,
    ),
    "TASK-INCEPTION-E": (
        "ed3c/enterprise_agent_system",
        "inception/profile-shadow",
        19,
    ),
    "TASK-INCEPTION-X": (
        "ed3c/enterprise_agent_system",
        "inception/profile-convergence",
        22,
    ),
    "TASK-INCEPTION-D": (
        "ed3c/enterprise_agent_system",
        "inception/profile-docs-stack",
        23,
    ),
    "TASK-INCEPTION-H": (
        "ed3c/enterprise_agent_system",
        "inception/profile-local-handoff-request",
        14,
    ),
}
CAPABILITY_IDS = {
    "CAP-INPUT-READBACK",
    "CAP-PACKET-COMPILER",
    "CAP-A1-COMPACTION-OWNER",
    "CAP-A2-RUNTIME-OWNER",
    "CAP-A3-EVIDENCE-OWNER",
    "CAP-A4-PROVENANCE-OWNER",
    "CAP-A5-DISCOVERY-OWNER",
    "CAP-A6-INGRESS-OWNER",
    "CAP-PROFILE-SHADOW",
    "CAP-PROFILE-CONVERGENCE",
    "CAP-PROFILE-DOCS",
    "CAP-PROFILE-HANDOFF",
}
ATOM_IDS = {
    "EAS-C",
    "EAS-K",
    "INCEPTION-C0",
    "INCEPTION-C1",
    "INCEPTION-K",
    "INCEPTION-A1",
    "INCEPTION-A2",
    "INCEPTION-A3",
    "INCEPTION-A4",
    "INCEPTION-A5",
    "INCEPTION-A6",
    "INCEPTION-E",
    "INCEPTION-X",
    "INCEPTION-D",
    "INCEPTION-H",
}


class Refusal(ValueError):
    pass


def req(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    req(isinstance(value, dict), f"ROOT_NOT_OBJECT:{path}")
    return value


def strict(
    value: Any,
    required: set[str],
    name: str,
    optional: set[str] | None = None,
) -> dict[str, Any]:
    req(isinstance(value, dict), f"{name}_NOT_OBJECT")
    optional = optional or set()
    missing = required - set(value)
    unknown = set(value) - required - optional
    req(
        not missing and not unknown,
        f"{name}_FIELDS:missing={sorted(missing)}:unknown={sorted(unknown)}",
    )
    return value


def unique_strings(value: Any, name: str, *, nonempty: bool = True) -> list[str]:
    req(isinstance(value, list), f"{name}_NOT_ARRAY")
    if nonempty:
        req(bool(value), f"{name}_EMPTY")
    req(
        all(isinstance(item, str) and bool(item.strip()) for item in value),
        f"{name}_ITEM",
    )
    req(len(value) == len(set(value)), f"{name}_DUPLICATE")
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


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sign_packet(packet: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(packet)
    value.pop("packet_digest", None)
    value["packet_digest"] = "sha256:" + hashlib.sha256(canonical(value)).hexdigest()
    return value


def validate_input_binding(value: dict[str, Any]) -> None:
    strict(
        value,
        {
            "schema_version",
            "binding_id",
            "inputs",
            "output_state",
            "evidence_ceiling",
            "claims_not_proven",
        },
        "INPUT_BINDING",
    )
    req(
        value["schema_version"]
        == "enterprise-agent-system/inception-profile-input-binding/v1",
        "INPUT_BINDING_VERSION",
    )
    inputs = value["inputs"]
    req(isinstance(inputs, dict) and set(inputs) == set(EXACT), "INPUT_DENOMINATOR")
    for name, expected in EXACT.items():
        item = inputs[name]
        for field in ("repository", "commit", "tree"):
            req(item.get(field) == expected[field], f"INPUT_SUBJECT_DRIFT:{name}:{field}")
        validate_exact_subject(
            {
                "repository": item["repository"],
                "commit": item["commit"],
                "tree": item["tree"],
            }
        )
    req(inputs["eas_c"]["state"] == "ADMIT_FOR_REVIEW", "INPUT_C_STATE")
    req(inputs["eas_k"]["state"] == "ADMIT_FOR_REVIEW", "INPUT_K_STATE")
    req(inputs["profile_c0"]["source_digest"] == SOURCE_DIGEST, "INPUT_SOURCE_DIGEST")
    req(inputs["profile_c0"]["requirements"] == 15, "INPUT_REQUIREMENTS")
    req(inputs["profile_c0"]["contradictions"] == 14, "INPUT_CONTRADICTIONS")
    req(inputs["profile_c1"]["bundle_digest"] == CONTRACT_DIGEST, "INPUT_CONTRACT_DIGEST")
    req(inputs["profile_c1"]["record_count"] == 11, "INPUT_CONTRACT_COUNT")
    req(
        inputs["profile_k_base"]["parents"]
        == [EXACT["profile_c1"]["commit"], EXACT["eas_k"]["commit"]],
        "INPUT_MULTI_PARENT_BINDING",
    )
    req(
        inputs["shadow_preflight"]["verdict"] == "ADMIT_FOR_REVIEW",
        "INPUT_SHADOW_PREFLIGHT",
    )
    req(
        inputs["shadow_preflight"]["full_architecture_verdict"]
        == "BLOCKED_FOR_CLOSURE",
        "INPUT_FALSE_ARCHITECTURE_CLOSURE",
    )
    req(value["output_state"] == "PROFILE_K_INPUTS_BOUND", "INPUT_OUTPUT_STATE")
    req(value["evidence_ceiling"] == "EXACT_INPUT_BINDING_ONLY", "INPUT_CEILING")
    unique_strings(value["claims_not_proven"], "INPUT_CLAIMS")


def task_map(run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {task["id"]: task for task in run["tasks"]}


def lease_map(run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {lease["task_id"]: lease for lease in run["leases"]}


def validate_profile_run(run: dict[str, Any]) -> None:
    try:
        validate_run(run)
    except ValueError as exc:
        raise Refusal(str(exc)) from exc
    tasks = task_map(run)
    req(set(tasks) == EXPECTED_TASKS, "TASK_DENOMINATOR")
    req(
        run["request_subject"] == EXACT["profile_k_base"],
        "RUN_REQUEST_SUBJECT",
    )
    try:
        start_waves = topological_waves(run, dependency_field="start_dependencies")
        completion_waves = topological_waves(
            run, dependency_field="completion_dependencies"
        )
    except ValueError as exc:
        raise Refusal(str(exc)) from exc
    req(start_waves == EXPECTED_WAVES, f"START_WAVES:{start_waves}")
    req(completion_waves == EXPECTED_WAVES, f"COMPLETION_WAVES:{completion_waves}")
    for task_id in A_TASKS:
        task = tasks[task_id]
        req(task["start_dependencies"] == [TASK_K], f"A_START:{task_id}")
        req(task["completion_dependencies"] == [TASK_K], f"A_COMPLETION:{task_id}")
        req(task["state"] == "PLANNED", f"A_FALSE_EXECUTION:{task_id}")
        req(task["required_lane"] == LANES[task_id], f"A_LANE:{task_id}")
    req(tasks[TASK_K]["state"] == "CANDIDATE", "K_STATE")
    for task_id in PACKET_TASKS - A_TASKS:
        req(tasks[task_id]["state"] == "BLOCKED", f"DOWNSTREAM_FALSE_READY:{task_id}")
        req(tasks[task_id]["required_lane"] == LANES[task_id], f"DOWNSTREAM_LANE:{task_id}")
    try:
        assert_disjoint_leases(run, sorted(A_TASKS))
    except ValueError as exc:
        raise Refusal(str(exc)) from exc
    req(run["shadow"] == {"read_only": True, "separate_evaluation_path": True, "may_commit": []}, "RUN_SHADOW_AUTHORITY")
    req(set(run["authority"]["automation_forbidden"]) >= HUMAN_ONLY, "RUN_FORBIDDEN_AUTHORITY")
    req(set(run["authority"]["human_owned"]) >= HUMAN_ONLY, "RUN_HUMAN_AUTHORITY")
    req(run["state"] == "PROMPT_PACKETS_EMITTED", "RUN_STATE")


def validate_capability_plan(value: dict[str, Any], run: dict[str, Any]) -> None:
    strict(
        value,
        {
            "schema_version",
            "plan_id",
            "subject",
            "transitions",
            "evidence_ceiling",
            "claims_not_proven",
        },
        "CAPABILITY_PLAN",
    )
    req(
        value["schema_version"]
        == "enterprise-agent-system/inception-capability-plan/v1",
        "CAPABILITY_VERSION",
    )
    req(value["subject"] == EXACT["profile_k_base"], "CAPABILITY_SUBJECT")
    transitions = value["transitions"]
    req(isinstance(transitions, list), "CAPABILITY_TRANSITIONS_NOT_ARRAY")
    by_id: dict[str, dict[str, Any]] = {}
    tasks = task_map(run)
    allowed_states = {
        "CLOSED",
        "CANDIDATE",
        "NOT_EXERCISED",
        "BLOCKED_BY_PREDECESSOR",
    }
    for index, raw in enumerate(transitions):
        item = strict(
            raw,
            {
                "transition_id",
                "task_id",
                "selection",
                "trigger",
                "module",
                "predecessors",
                "required_input_states",
                "produced_state",
                "downstream_state",
                "fallback",
                "authority_ceiling",
                "current_state",
                "claims_not_proven",
            },
            f"CAPABILITY_{index}",
        )
        transition_id = item["transition_id"]
        req(transition_id not in by_id, f"DUPLICATE_CAPABILITY:{transition_id}")
        req(item["task_id"] in tasks, f"CAPABILITY_TASK:{transition_id}")
        req(item["selection"] in {"REQUIRED", "OPTIONAL_SELECTED"}, f"CAPABILITY_SELECTION:{transition_id}")
        req(item["fallback"] in {"STOP", "LOCAL_HANDOFF", "HUMAN_ADMIT"}, f"CAPABILITY_FALLBACK:{transition_id}")
        req(item["current_state"] in allowed_states, f"CAPABILITY_STATE:{transition_id}")
        req(item["current_state"] != "PASS", f"CAPABILITY_FALSE_PASS:{transition_id}")
        req(isinstance(item["trigger"], str) and bool(item["trigger"]), f"CAPABILITY_TRIGGER:{transition_id}")
        req(isinstance(item["module"], str) and bool(item["module"]), f"CAPABILITY_MODULE:{transition_id}")
        unique_strings(item["predecessors"], f"CAPABILITY_PREDECESSORS:{transition_id}", nonempty=False)
        unique_strings(item["required_input_states"], f"CAPABILITY_INPUTS:{transition_id}")
        unique_strings(item["claims_not_proven"], f"CAPABILITY_CLAIMS:{transition_id}")
        by_id[transition_id] = item
    req(set(by_id) == CAPABILITY_IDS, "CAPABILITY_DENOMINATOR")
    for transition_id, item in by_id.items():
        for predecessor in item["predecessors"]:
            req(predecessor in by_id and predecessor != transition_id, f"CAPABILITY_PREDECESSOR:{transition_id}:{predecessor}")
    remaining = {
        transition_id: set(item["predecessors"])
        for transition_id, item in by_id.items()
    }
    while remaining:
        ready = {key for key, dependencies in remaining.items() if not dependencies}
        req(bool(ready), "CAPABILITY_CYCLE")
        for key in ready:
            remaining.pop(key)
        for dependencies in remaining.values():
            dependencies.difference_update(ready)
    req(by_id["CAP-INPUT-READBACK"]["current_state"] == "CLOSED", "CAPABILITY_INPUT_NOT_CLOSED")
    req(by_id["CAP-PACKET-COMPILER"]["current_state"] == "CANDIDATE", "CAPABILITY_COMPILER_STATE")
    for transition_id in CAPABILITY_IDS - {"CAP-INPUT-READBACK", "CAP-PACKET-COMPILER"}:
        req(by_id[transition_id]["current_state"] in {"NOT_EXERCISED", "BLOCKED_BY_PREDECESSOR"}, f"CAPABILITY_FALSE_EXECUTION:{transition_id}")
    req(by_id["CAP-PROFILE-SHADOW"]["authority_ceiling"] == "READ_ONLY_EVALUATOR", "CAPABILITY_SHADOW_AUTHORITY")
    req(value["evidence_ceiling"] == "CAPABILITY_PLAN_CANDIDATE_ONLY", "CAPABILITY_CEILING")
    unique_strings(value["claims_not_proven"], "CAPABILITY_PLAN_CLAIMS")


def validate_specs(value: dict[str, Any], run: dict[str, Any]) -> None:
    strict(
        value,
        {
            "schema_version",
            "spec_set_id",
            "input_binding",
            "defaults",
            "specs",
            "evidence_ceiling",
            "claims_not_proven",
        },
        "PACKET_SPECS",
    )
    req(
        value["schema_version"]
        == "enterprise-agent-system/inception-worker-packet-specs/v1",
        "PACKET_SPECS_VERSION",
    )
    binding = strict(
        value["input_binding"],
        {
            "path",
            "profile_k_base_commit",
            "profile_k_base_tree",
            "source_digest",
            "contract_bundle_digest",
        },
        "PACKET_INPUT_BINDING",
    )
    req(binding["profile_k_base_commit"] == EXACT["profile_k_base"]["commit"], "PACKET_BASE_COMMIT")
    req(binding["profile_k_base_tree"] == EXACT["profile_k_base"]["tree"], "PACKET_BASE_TREE")
    req(binding["source_digest"] == SOURCE_DIGEST, "PACKET_SOURCE_DIGEST")
    req(binding["contract_bundle_digest"] == CONTRACT_DIGEST, "PACKET_CONTRACT_DIGEST")
    defaults = strict(
        value["defaults"],
        {
            "non_goals",
            "invariants",
            "unknowns",
            "read_only_paths",
            "acceptance_criteria",
            "negative_controls",
            "cleanup_requirements",
            "receipt_fields",
            "forbidden_actions",
        },
        "PACKET_DEFAULTS",
    )
    for key in defaults:
        unique_strings(defaults[key], f"PACKET_DEFAULT:{key}")
    req(set(defaults["forbidden_actions"]) >= HUMAN_ONLY, "PACKET_DEFAULT_AUTHORITY")
    specs = value["specs"]
    req(isinstance(specs, list), "PACKET_SPEC_LIST")
    by_task: dict[str, dict[str, Any]] = {}
    tasks = task_map(run)
    for index, raw in enumerate(specs):
        item = strict(
            raw,
            {
                "task_id",
                "role",
                "owner_issue",
                "target_repository",
                "target_interface",
                "objective",
                "required_gates",
                "positive_controls",
                "runtime_requirements",
                "capability_requirements",
                "retry_budget",
                "timeout_seconds",
                "next_authority",
                "evidence_ceiling",
                "packet_state",
                "claims_not_proven",
            },
            f"PACKET_SPEC_{index}",
        )
        task_id = item["task_id"]
        req(task_id not in by_task, f"DUPLICATE_PACKET_SPEC:{task_id}")
        req(task_id in tasks, f"PACKET_TASK:{task_id}")
        expected_repo, expected_interface, expected_issue = OWNER_MAP[task_id]
        req(item["target_repository"] == expected_repo, f"PACKET_OWNER_SUBSTITUTION:{task_id}")
        req(item["target_interface"] == expected_interface, f"PACKET_INTERFACE:{task_id}")
        req(item["owner_issue"] == f"https://github.com/ed3c/enterprise_agent_system/issues/{expected_issue}", f"PACKET_ISSUE:{task_id}")
        req(REPOSITORY.fullmatch(item["target_repository"]) is not None, f"PACKET_REPOSITORY:{task_id}")
        req(ISSUE.fullmatch(item["owner_issue"]) is not None, f"PACKET_ISSUE_FORMAT:{task_id}")
        for key in (
            "required_gates",
            "positive_controls",
            "runtime_requirements",
            "capability_requirements",
            "claims_not_proven",
        ):
            unique_strings(item[key], f"PACKET_SPEC:{task_id}:{key}")
        req(isinstance(item["retry_budget"], int) and item["retry_budget"] >= 0, f"PACKET_RETRY:{task_id}")
        req(isinstance(item["timeout_seconds"], int) and item["timeout_seconds"] > 0, f"PACKET_TIMEOUT:{task_id}")
        req(item["packet_state"] in {"PLANNED", "BLOCKED_BY_PREDECESSOR"}, f"PACKET_STATE:{task_id}")
        by_task[task_id] = item
    req(set(by_task) == PACKET_TASKS, "PACKET_SPEC_DENOMINATOR")
    for task_id in A_TASKS:
        req(by_task[task_id]["packet_state"] == "PLANNED", f"PACKET_A_STATE:{task_id}")
    for task_id in PACKET_TASKS - A_TASKS:
        req(by_task[task_id]["packet_state"] == "BLOCKED_BY_PREDECESSOR", f"PACKET_DOWNSTREAM_STATE:{task_id}")
    req(value["evidence_ceiling"] == "ZERO_CONTEXT_PACKET_SPEC_CANDIDATE_ONLY", "PACKET_SPEC_CEILING")
    unique_strings(value["claims_not_proven"], "PACKET_SPEC_CLAIMS")


def render_packets(
    run: dict[str, Any], specs: dict[str, Any], inputs: dict[str, Any]
) -> dict[str, Any]:
    defaults = specs["defaults"]
    packets: list[dict[str, Any]] = []
    for spec in specs["specs"]:
        input_contract = {
            "input_binding": {
                "path": specs["input_binding"]["path"],
                "profile_k_base_commit": specs["input_binding"]["profile_k_base_commit"],
                "profile_k_base_tree": specs["input_binding"]["profile_k_base_tree"],
                "source_digest": specs["input_binding"]["source_digest"],
                "contract_bundle_digest": specs["input_binding"]["contract_bundle_digest"],
            },
            "exact_inputs": inputs["inputs"],
            "owner_contract": {
                "role": spec["role"],
                "owner_issue": spec["owner_issue"],
                "target_repository": spec["target_repository"],
                "target_interface": spec["target_interface"],
                "packet_state": spec["packet_state"],
                "claims_not_proven": spec["claims_not_proven"],
            },
        }
        try:
            packet = compile_prompt_packet(
                run,
                spec["task_id"],
                objective=spec["objective"],
                invariants=defaults["invariants"],
                required_gates=spec["required_gates"],
                evidence_ceiling=spec["evidence_ceiling"],
                non_goals=defaults["non_goals"],
                unknowns=defaults["unknowns"],
                read_only_paths=defaults["read_only_paths"],
                input_contract=input_contract,
                acceptance_criteria=defaults["acceptance_criteria"],
                positive_controls=spec["positive_controls"],
                negative_controls=defaults["negative_controls"],
                runtime_requirements=spec["runtime_requirements"],
                capability_requirements=spec["capability_requirements"],
                cleanup_requirements=defaults["cleanup_requirements"],
                forbidden_actions=defaults["forbidden_actions"],
                receipt_fields=defaults["receipt_fields"],
                retry_budget=spec["retry_budget"],
                timeout_seconds=spec["timeout_seconds"],
                next_authority=spec["next_authority"],
            )
        except ValueError as exc:
            raise Refusal(str(exc)) from exc
        packets.append(packet)
    body: dict[str, Any] = {
        "schema_version": "enterprise-agent-system/inception-packet-bundle/v1",
        "bundle_id": "PACKET-BUNDLE-INCEPTION-K-2026-08-18",
        "request_subject": run["request_subject"],
        "packet_count": len(packets),
        "packets": packets,
        "evidence_ceiling": "ZERO_CONTEXT_PACKET_BUNDLE_CANDIDATE_ONLY",
        "claims_not_proven": [
            "Packet generation is not Worker execution.",
            "Owner repository subjects must be rebound before mutation.",
            "Local provider effect user Human release and rollback lanes remain open.",
        ],
    }
    body["bundle_digest"] = "sha256:" + hashlib.sha256(canonical(body)).hexdigest()
    return body


def validate_packet_bundle(
    bundle: dict[str, Any],
    run: dict[str, Any],
    specs: dict[str, Any],
    inputs: dict[str, Any],
) -> None:
    strict(
        bundle,
        {
            "schema_version",
            "bundle_id",
            "request_subject",
            "packet_count",
            "packets",
            "evidence_ceiling",
            "claims_not_proven",
            "bundle_digest",
        },
        "PACKET_BUNDLE",
    )
    req(bundle["request_subject"] == EXACT["profile_k_base"], "PACKET_BUNDLE_SUBJECT")
    req(bundle["packet_count"] == 10, "PACKET_COUNT")
    req(isinstance(bundle["packets"], list), "PACKETS_NOT_ARRAY")
    req(len(bundle["packets"]) == bundle["packet_count"], "PACKET_COUNT_MISMATCH")
    unsigned = copy.deepcopy(bundle)
    claimed = unsigned.pop("bundle_digest")
    expected = "sha256:" + hashlib.sha256(canonical(unsigned)).hexdigest()
    req(claimed == expected, "PACKET_BUNDLE_DIGEST_MISMATCH")
    by_spec = {item["task_id"]: item for item in specs["specs"]}
    tasks = task_map(run)
    packet_ids: set[str] = set()
    for packet in bundle["packets"]:
        try:
            validate_prompt_packet(packet)
        except ValueError as exc:
            raise Refusal(str(exc)) from exc
        task_id = packet["task_id"]
        req(task_id not in packet_ids, f"DUPLICATE_PACKET:{task_id}")
        packet_ids.add(task_id)
        req(task_id in by_spec, f"PACKET_WITHOUT_SPEC:{task_id}")
        spec = by_spec[task_id]
        req(packet["subject"] == EXACT["profile_k_base"], f"PACKET_SUBJECT:{task_id}")
        req(packet["dependencies"]["start"] == tasks[task_id]["start_dependencies"], f"PACKET_START:{task_id}")
        req(packet["dependencies"]["completion"] == tasks[task_id]["completion_dependencies"], f"PACKET_COMPLETION:{task_id}")
        lease = lease_map(run)[task_id]
        req(packet["leases"]["writer_id"] == lease["writer_id"], f"PACKET_WRITER:{task_id}")
        req(packet["leases"]["write_paths"] == lease["paths"], f"PACKET_PATHS:{task_id}")
        req(packet["leases"]["resources"] == lease["resources"], f"PACKET_RESOURCES:{task_id}")
        req(packet["runtime"]["required_lane"] == LANES[task_id], f"PACKET_LANE:{task_id}")
        contract = packet["input_contract"]
        req(contract["input_binding"]["source_digest"] == SOURCE_DIGEST, f"PACKET_SOURCE:{task_id}")
        req(contract["input_binding"]["contract_bundle_digest"] == CONTRACT_DIGEST, f"PACKET_CONTRACT:{task_id}")
        req(contract["exact_inputs"] == inputs["inputs"], f"PACKET_EXACT_INPUTS:{task_id}")
        owner_contract = contract["owner_contract"]
        req(owner_contract["target_repository"] == spec["target_repository"], f"PACKET_TARGET:{task_id}")
        req(owner_contract["target_interface"] == spec["target_interface"], f"PACKET_TARGET_INTERFACE:{task_id}")
        req(owner_contract["owner_issue"] == spec["owner_issue"], f"PACKET_TARGET_ISSUE:{task_id}")
        req(owner_contract["packet_state"] == spec["packet_state"], f"PACKET_TARGET_STATE:{task_id}")
        req(packet["evidence_ceiling"] == spec["evidence_ceiling"], f"PACKET_CEILING:{task_id}")
        req(packet["handoff"]["next_authority"] == spec["next_authority"], f"PACKET_NEXT:{task_id}")
        req(set(packet["forbidden_actions"]) >= HUMAN_ONLY, f"PACKET_AUTHORITY:{task_id}")
    req(packet_ids == PACKET_TASKS, "PACKET_DENOMINATOR")
    req(bundle["evidence_ceiling"] == "ZERO_CONTEXT_PACKET_BUNDLE_CANDIDATE_ONLY", "PACKET_BUNDLE_CEILING")
    unique_strings(bundle["claims_not_proven"], "PACKET_BUNDLE_CLAIMS")


def validate_stack(value: dict[str, Any]) -> None:
    strict(
        value,
        {
            "schema_version",
            "stack_id",
            "required_atom_classes",
            "atoms",
            "evidence_ceiling",
            "claims_not_proven",
        },
        "STACK",
    )
    req(
        value["schema_version"]
        == "enterprise-agent-system/inception-molecular-stack-index/v1",
        "STACK_VERSION",
    )
    req(set(value["required_atom_classes"]) == {"C", "K", "A", "E", "X", "D", "H"}, "STACK_CLASSES")
    atoms = value["atoms"]
    req(isinstance(atoms, list), "STACK_ATOMS_NOT_ARRAY")
    by_id: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(atoms):
        item = strict(
            raw,
            {
                "atom_id",
                "class",
                "kind",
                "issue",
                "pull_request",
                "subject",
                "git_parents",
                "process_dependencies",
                "owns_paths",
                "oracle",
                "required_lane",
                "receipt_lane",
                "state",
                "blockers",
                "next_authority",
            },
            f"STACK_ATOM_{index}",
        )
        atom_id = item["atom_id"]
        req(atom_id not in by_id, f"DUPLICATE_ATOM:{atom_id}")
        req(item["class"] in {"C", "K", "A", "E", "X", "D", "H"}, f"STACK_CLASS:{atom_id}")
        req(ISSUE.fullmatch(item["issue"]) is not None, f"STACK_ISSUE:{atom_id}")
        unique_strings(item["git_parents"], f"STACK_GIT_PARENTS:{atom_id}", nonempty=False)
        unique_strings(item["process_dependencies"], f"STACK_PROCESS_DEPS:{atom_id}", nonempty=False)
        unique_strings(item["owns_paths"], f"STACK_PATHS:{atom_id}")
        unique_strings(item["blockers"], f"STACK_BLOCKERS:{atom_id}")
        req(isinstance(item["oracle"], str) and bool(item["oracle"]), f"STACK_ORACLE:{atom_id}")
        req(isinstance(item["next_authority"], str) and bool(item["next_authority"]), f"STACK_NEXT:{atom_id}")
        req(item["required_lane"] in {"CLOUD", "LOCAL", "PRIVATE", "HUMAN"}, f"STACK_LANE:{atom_id}")
        if item["subject"] is not None:
            subject = item["subject"]
            validate_exact_subject(
                {
                    "repository": subject["repository"],
                    "commit": subject["commit"],
                    "tree": subject["tree"],
                }
            )
            if "digest" in subject:
                req(SHA256.fullmatch(subject["digest"]) is not None, f"STACK_DIGEST:{atom_id}")
        if item["pull_request"] is not None:
            req(isinstance(item["pull_request"], int) and item["pull_request"] > 0, f"STACK_PR:{atom_id}")
        by_id[atom_id] = item
    req(set(by_id) == ATOM_IDS, "STACK_DENOMINATOR")
    for atom_id, item in by_id.items():
        for dependency in item["git_parents"] + item["process_dependencies"]:
            req(dependency in by_id and dependency != atom_id, f"STACK_DEPENDENCY:{atom_id}:{dependency}")
        if item["kind"] in {"true-child", "multi-parent-true-child"}:
            req(bool(item["git_parents"]), f"STACK_TRUE_CHILD_WITHOUT_PARENT:{atom_id}")
        if item["state"] in {"PLANNED", "BLOCKED_BY_PREDECESSOR"}:
            req(item["subject"] is None and item["pull_request"] is None, f"STACK_PLANNED_AS_OBSERVED:{atom_id}")
    req(by_id["INCEPTION-K"]["git_parents"] == ["INCEPTION-C1", "EAS-K"], "STACK_K_PARENTS")
    req(by_id["INCEPTION-K"]["state"] in {"CANDIDATE_BRANCH", "CANDIDATE_PR"}, "STACK_K_STATE")
    if by_id["INCEPTION-K"]["state"] == "CANDIDATE_PR":
        req(by_id["INCEPTION-K"]["pull_request"] is not None, "STACK_K_PR_ABSENT")
    req(by_id["INCEPTION-E"]["kind"] == "read-only-process-gate", "STACK_SHADOW_KIND")
    req(value["evidence_ceiling"] == "PROFILE_STACK_TOPOLOGY_CANDIDATE_ONLY", "STACK_CEILING")
    unique_strings(value["claims_not_proven"], "STACK_CLAIMS")


def validate_docs() -> None:
    required = [
        PROFILE / "prompts" / "02-tech-lead-profile-controller.system.md",
        PROFILE / "prompts" / "03-profile-worker-envelope.system.md",
        ORCHESTRATION / "compile_profile_packets.py",
    ]
    for path in required:
        req(path.is_file(), f"DOC_PATH_ABSENT:{path.relative_to(ROOT)}")
    controller = required[0].read_text(encoding="utf-8")
    envelope = required[1].read_text(encoding="utf-8")
    for token in (
        EXACT["eas_c"]["commit"],
        EXACT["eas_k"]["commit"],
        EXACT["profile_c0"]["commit"],
        EXACT["profile_c1"]["commit"],
        SOURCE_DIGEST,
        CONTRACT_DIGEST,
    ):
        req(token in controller, f"CONTROLLER_EXACT_INPUT:{token}")
    req("Prior chat memory is not an input" in controller, "CONTROLLER_ZERO_CONTEXT")
    req("attached machine packet is the complete contract" in envelope, "WORKER_ZERO_CONTEXT")
    req("private chain of thought" in envelope, "WORKER_PRIVATE_REASONING_BOUNDARY")


def validate_all(data: dict[str, dict[str, Any]]) -> dict[str, Any]:
    req(
        not any(
            SECRET_OR_PRIVATE.search(item)
            for value in data.values()
            for item in strings(value)
        ),
        "SECRET_SESSION_OR_LOCAL_PATH",
    )
    validate_input_binding(data["inputs"])
    validate_profile_run(data["run"])
    validate_capability_plan(data["capability"], data["run"])
    validate_specs(data["specs"], data["run"])
    bundle = render_packets(data["run"], data["specs"], data["inputs"])
    validate_packet_bundle(bundle, data["run"], data["specs"], data["inputs"])
    validate_stack(data["stack"])
    return bundle


def load_all() -> dict[str, dict[str, Any]]:
    return {
        "inputs": load(INPUT_PATH),
        "run": load(RUN_PATH),
        "capability": load(CAPABILITY_PATH),
        "specs": load(SPECS_PATH),
        "stack": load(STACK_PATH),
    }


def mutate_path_lease_collision(value: dict[str, dict[str, Any]]) -> None:
    """Plant a real concurrent-path collision without violating task/lease parity first."""

    collision = "profiles/agent-thinking-inception/owners/compaction/**"
    task = next(
        item
        for item in value["run"]["tasks"]
        if item["id"] == "TASK-INCEPTION-A2"
    )
    lease = next(
        item
        for item in value["run"]["leases"]
        if item["task_id"] == "TASK-INCEPTION-A2"
    )
    task["owns_paths"][0] = collision
    lease["paths"][0] = collision


def selftest(data: dict[str, dict[str, Any]]) -> None:
    mutations: list[tuple[str, Callable[[dict[str, dict[str, Any]]], None]]] = [
        ("INPUT_SUBJECT_DRIFT", lambda value: value["inputs"]["inputs"]["eas_k"].update(commit="0" * 40)),
        ("INPUT_SOURCE_DIGEST", lambda value: value["inputs"]["inputs"]["profile_c0"].update(source_digest="sha256:" + "0" * 64)),
        ("INPUT_CONTRACT_DIGEST", lambda value: value["inputs"]["inputs"]["profile_c1"].update(bundle_digest="sha256:" + "0" * 64)),
        ("DUPLICATE_TASK", lambda value: value["run"]["tasks"].append(copy.deepcopy(value["run"]["tasks"][0]))),
        ("COMPLETION_WITHOUT_START", lambda value: next(task for task in value["run"]["tasks"] if task["id"] == "TASK-INCEPTION-A1").update(start_dependencies=[])),
        ("CYCLIC_DAG:start_dependencies", lambda value: next(task for task in value["run"]["tasks"] if task["id"] == TASK_K).update(start_dependencies=["TASK-INCEPTION-H"])),
        ("PATH_LEASE_COLLISION", mutate_path_lease_collision),
        ("RESOURCE_LEASE_COLLISION", lambda value: next(lease for lease in value["run"]["leases"] if lease["task_id"] == "TASK-INCEPTION-A2")["resources"].append("local-storage-namespace:inception-compaction")),
        ("SHADOW_SECOND_STATE_WRITER", lambda value: value["run"]["shadow"].update(may_commit=["TASK_STATE"])),
        ("HUMAN_AUTHORITY_MISSING", lambda value: value["run"]["authority"]["human_owned"].remove("merge")),
        ("CAPABILITY_CYCLE", lambda value: next(item for item in value["capability"]["transitions"] if item["transition_id"] == "CAP-INPUT-READBACK")["predecessors"].append("CAP-PROFILE-HANDOFF")),
        ("CAPABILITY_FALSE_EXECUTION", lambda value: next(item for item in value["capability"]["transitions"] if item["transition_id"] == "CAP-A1-COMPACTION-OWNER").update(current_state="CANDIDATE")),
        ("CAPABILITY_SHADOW_AUTHORITY", lambda value: next(item for item in value["capability"]["transitions"] if item["transition_id"] == "CAP-PROFILE-SHADOW").update(authority_ceiling="TASK_STATE_ONLY")),
        ("PACKET_SPEC_DENOMINATOR", lambda value: value["specs"]["specs"].pop()),
        ("PACKET_OWNER_SUBSTITUTION", lambda value: next(item for item in value["specs"]["specs"] if item["task_id"] == "TASK-INCEPTION-A1").update(target_repository="ed3c/enterprise_agent_system")),
        ("PACKET_DEFAULT_AUTHORITY", lambda value: value["specs"]["defaults"]["forbidden_actions"].remove("merge")),
        ("STACK_PLANNED_AS_OBSERVED", lambda value: next(item for item in value["stack"]["atoms"] if item["atom_id"] == "INCEPTION-A1").update(subject=copy.deepcopy(EXACT["profile_k_base"]))),
        ("STACK_TRUE_CHILD_WITHOUT_PARENT", lambda value: next(item for item in value["stack"]["atoms"] if item["atom_id"] == "INCEPTION-C1").update(git_parents=[])),
        ("DUPLICATE_ATOM", lambda value: value["stack"]["atoms"].append(copy.deepcopy(value["stack"]["atoms"][0]))),
        ("SECRET_SESSION_OR_LOCAL_PATH", lambda value: value["specs"]["claims_not_proven"].append("/mnt/data/private.pdf")),
    ]
    for expected, mutate in mutations:
        candidate = copy.deepcopy(data)
        mutate(candidate)
        try:
            validate_all(candidate)
        except (Refusal, ValueError, KeyError, StopIteration) as exc:
            req(expected in str(exc), f"WRONG_REFUSAL:{expected}:{exc}")
        else:
            raise Refusal(f"MUTATION_DID_NOT_FAIL:{expected}")

    bundle = validate_all(copy.deepcopy(data))
    packet_mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("PACKET_DIGEST_MISMATCH", lambda value: value["packets"][0].update(objective="tampered")),
        ("PROMPT_READ_WRITE_LEASE_COLLISION", lambda value: (value["packets"][0]["leases"]["read_only_paths"].append(value["packets"][0]["leases"]["write_paths"][0]), value["packets"].__setitem__(0, sign_packet(value["packets"][0])))),
        ("PROMPT_AUTHORITY_WIDENED", lambda value: (value["packets"][0]["forbidden_actions"].remove("merge"), value["packets"].__setitem__(0, sign_packet(value["packets"][0])))),
        ("PACKET_SUBJECT", lambda value: (value["packets"][0]["subject"].update(commit="0" * 40), value["packets"][0]["rollback_subject"].update(commit="0" * 40), value["packets"].__setitem__(0, sign_packet(value["packets"][0])))),
        ("PACKET_BUNDLE_DIGEST_MISMATCH", lambda value: value.update(bundle_id="tampered")),
    ]
    for expected, mutate in packet_mutations:
        candidate = copy.deepcopy(bundle)
        mutate(candidate)
        if expected != "PACKET_BUNDLE_DIGEST_MISMATCH":
            unsigned = copy.deepcopy(candidate)
            unsigned.pop("bundle_digest")
            candidate["bundle_digest"] = "sha256:" + hashlib.sha256(canonical(unsigned)).hexdigest()
        try:
            validate_packet_bundle(
                candidate,
                data["run"],
                data["specs"],
                data["inputs"],
            )
        except (Refusal, ValueError, KeyError) as exc:
            req(expected in str(exc), f"WRONG_PACKET_REFUSAL:{expected}:{exc}")
        else:
            raise Refusal(f"PACKET_MUTATION_DID_NOT_FAIL:{expected}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    try:
        data = load_all()
        bundle = validate_all(data)
        generated = compile_packets()
        req(generated == bundle, "COMPILER_OUTPUT_DRIFT")
        validate_docs()
        if args.selftest:
            selftest(data)
    except (OSError, json.JSONDecodeError, Refusal, ValueError, KeyError, StopIteration) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(
        "PASS tasks=11 packets=10 capabilities=12 atoms=15 "
        f"mutations={25 if args.selftest else 0} "
        f"bundle={bundle['bundle_digest']} "
        "evidence_ceiling=PROFILE_K_PLAN_CANDIDATE_ONLY"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
