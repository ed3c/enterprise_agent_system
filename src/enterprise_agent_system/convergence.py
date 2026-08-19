"""Fail-closed cross-repository convergence for exact public owner subjects.

EAS-X is an aggregate control-plane view.  It never becomes a second runtime,
workflow reducer, effect ledger, provider adapter, verifier, Human authority, or
release authority.
"""

from __future__ import annotations

import json
import re
from typing import Any, Mapping

SHA40 = re.compile(r"^[0-9a-f]{40}$")
REPOSITORY = re.compile(r"^[^/\s]+/[^/\s]+$")
ISSUE = re.compile(r"^https://github\.com/[^/]+/[^/]+/issues/[1-9][0-9]*$")

REQUIRED_INTERFACES = {
    "A1_COMPACTION_RECOVERY": "ed3c/bettor-arena",
    "A2R_RUNTIME_CONTRACT": "ed3c/runtime-env",
    "A2_SANDBOX_STEERING": "ed3c/agent-shield-monorepo",
    "A3_EXACT_EVIDENCE": "ed3c/truth-verify-loop",
    "A4_PROVENANCE_TELEMETRY": "ed3c/enterprise_agent_system",
    "A5_DISCOVERY_ADMISSION": "ed3c/bettor-arena",
    "A6_INGRESS_EFFECTS": "ed3c/bettor-arena",
}

ALLOWED_OWNER_EVIDENCE = {"DETERMINISTIC_VERIFIED", "PUBLIC_VERIFIED"}
NO_CREDIT_STATES = {
    "ABSENT",
    "NOT_IMPLEMENTED",
    "NOT_EXERCISED",
    "NOT_PERFORMED",
    "NOT_VERIFIED",
    "BLOCKED",
    "PARTIAL_OR_UNBOUND",
    "HUMAN_ADMIT_REQUIRED",
}
EXPECTED_STRONGER_LANES = {
    "PHYSICAL_POWER_LOSS_MULTI_HOST",
    "NETWORK_GVISOR_ISOLATION",
    "PROVIDER_CAPABILITY_ENROLLMENT",
    "EXTERNAL_INDEPENDENT_SEMANTIC",
    "PRIVATE_EVIDENCE",
    "EXACT_EXTERNAL_MODEL_DATA_TRACE_TERMS",
    "LIVE_TELEMETRY_EXPORT_STORE_DELETE",
    "EXTERNAL_CANDIDATE_BENCHMARK",
    "REAL_EXTERNAL_EFFECT_REMOTE_READBACK",
    "COMPENSATION",
    "BUSINESS_USER_OUTCOME",
    "HUMAN_LEGAL_SECURITY_ADMISSION",
    "MERGE_RELEASE_ROLLBACK",
}


class ConvergenceContractError(ValueError):
    """Raised when a convergence record widens authority or launders evidence."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ConvergenceContractError(reason)


def _strict_mapping(
    value: Any,
    *,
    required: set[str],
    optional: set[str] | None = None,
    name: str,
) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), f"{name}_NOT_OBJECT")
    optional = optional or set()
    missing = required - set(value)
    unknown = set(value) - required - optional
    _require(
        not missing and not unknown,
        f"{name}_FIELDS:missing={sorted(missing)}:unknown={sorted(unknown)}",
    )
    return value


def _nonempty_string(value: Any, reason: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()) and value == value.strip(), reason)
    return value


def _exact_subject(value: Any, *, prefix: str) -> Mapping[str, Any]:
    subject = _strict_mapping(
        value,
        required={"repository", "commit", "tree"},
        name=prefix,
    )
    repository = _nonempty_string(subject["repository"], f"{prefix}_REPOSITORY")
    _require(REPOSITORY.fullmatch(repository) is not None, f"{prefix}_REPOSITORY")
    _require(SHA40.fullmatch(str(subject["commit"])) is not None, f"{prefix}_COMMIT")
    _require(SHA40.fullmatch(str(subject["tree"])) is not None, f"{prefix}_TREE")
    return subject


def _issue(value: Any, reason: str) -> str:
    issue = _nonempty_string(value, reason)
    _require(ISSUE.fullmatch(issue) is not None, reason)
    return issue


def _unique_strings(value: Any, reason: str, *, nonempty: bool = True) -> list[str]:
    _require(isinstance(value, list), f"{reason}_NOT_ARRAY")
    if nonempty:
        _require(bool(value), f"{reason}_EMPTY")
    _require(all(isinstance(item, str) and bool(item.strip()) for item in value), f"{reason}_ITEM")
    _require(len(value) == len(set(value)), f"{reason}_DUPLICATE")
    return value


def validate_owner_record(value: Mapping[str, Any]) -> None:
    record = _strict_mapping(
        value,
        required={
            "interface",
            "repository",
            "issue",
            "subject",
            "evidence_state",
            "hosted_runs",
            "shadow_review",
            "lane",
            "next_transition",
        },
        name="OWNER",
    )
    interface = _nonempty_string(record["interface"], "OWNER_INTERFACE")
    _require(interface in REQUIRED_INTERFACES, f"OWNER_INTERFACE_UNKNOWN:{interface}")
    repository = _nonempty_string(record["repository"], "OWNER_REPOSITORY")
    _require(repository == REQUIRED_INTERFACES[interface], f"OWNER_REPOSITORY_MISMATCH:{interface}")
    _issue(record["issue"], "OWNER_ISSUE")
    subject = _exact_subject(record["subject"], prefix="OWNER_SUBJECT")
    _require(subject["repository"] == repository, f"OWNER_SUBJECT_REPOSITORY_MISMATCH:{interface}")
    _require(record["evidence_state"] in ALLOWED_OWNER_EVIDENCE, f"OWNER_EVIDENCE_STATE:{interface}")
    runs = record["hosted_runs"]
    _require(isinstance(runs, list) and runs, f"OWNER_HOSTED_RUNS:{interface}")
    _require(all(isinstance(item, int) and item > 0 for item in runs), f"OWNER_HOSTED_RUN_ID:{interface}")
    _require(len(runs) == len(set(runs)), f"OWNER_HOSTED_RUN_DUPLICATE:{interface}")
    _require(isinstance(record["shadow_review"], int) and record["shadow_review"] > 0, f"OWNER_SHADOW_REVIEW:{interface}")
    _nonempty_string(record["lane"], f"OWNER_LANE:{interface}")
    _nonempty_string(record["next_transition"], f"OWNER_NEXT_TRANSITION:{interface}")


def validate_convergence_snapshot(snapshot: Mapping[str, Any]) -> None:
    """Validate the aggregate P5 snapshot without promoting stronger evidence lanes."""

    snapshot = _strict_mapping(
        snapshot,
        required={
            "schema_version",
            "atom_id",
            "state",
            "git_parent",
            "process_dependencies",
            "owners",
            "stronger_lanes",
            "selected_vertical_canary",
            "release_owner",
            "claims_not_proven",
        },
        name="CONVERGENCE",
    )
    _require(
        snapshot["schema_version"] == "enterprise-agent-system/cross-repo-convergence/v1",
        "CONVERGENCE_SCHEMA_VERSION",
    )
    _require(snapshot["atom_id"] == "EAS-X", "CONVERGENCE_ATOM")
    _require(snapshot["state"] == "P5_CROSS_REPO_CONVERGENCE_CANDIDATE", "CONVERGENCE_STATE_PROMOTION")

    parent = _strict_mapping(
        snapshot["git_parent"],
        required={"repository", "commit", "tree", "pull_request", "atom"},
        name="GIT_PARENT",
    )
    _exact_subject(
        {"repository": parent["repository"], "commit": parent["commit"], "tree": parent["tree"]},
        prefix="GIT_PARENT_SUBJECT",
    )
    _require(parent["repository"] == "ed3c/enterprise_agent_system", "GIT_PARENT_REPOSITORY")
    _require(parent["atom"] == "EAS-E", "FALSE_GIT_PARENT")
    _require(isinstance(parent["pull_request"], int) and parent["pull_request"] > 0, "GIT_PARENT_PR")

    process_dependencies = snapshot["process_dependencies"]
    _require(isinstance(process_dependencies, list) and process_dependencies, "PROCESS_DEPENDENCIES")
    process_atoms: set[str] = set()
    for item in process_dependencies:
        dep = _strict_mapping(
            item,
            required={"atom", "issue", "state", "subject"},
            name="PROCESS_DEPENDENCY",
        )
        atom = _nonempty_string(dep["atom"], "PROCESS_DEPENDENCY_ATOM")
        _require(atom not in process_atoms, f"PROCESS_DEPENDENCY_DUPLICATE:{atom}")
        process_atoms.add(atom)
        _issue(dep["issue"], "PROCESS_DEPENDENCY_ISSUE")
        if dep["state"] == "NOT_IMPLEMENTED":
            _require(dep["subject"] is None, f"NOT_IMPLEMENTED_HAS_SUBJECT:{atom}")
        else:
            _require(dep["state"] == "DETERMINISTIC_VERIFIED", f"PROCESS_DEPENDENCY_STATE:{atom}")
            _exact_subject(dep["subject"], prefix=f"PROCESS_DEPENDENCY_{atom}")
    _require(process_atoms == {"EAS-K", "EAS-A"}, "PROCESS_DEPENDENCY_DENOMINATOR")

    owners = snapshot["owners"]
    _require(isinstance(owners, list), "OWNERS_NOT_ARRAY")
    interfaces: list[str] = []
    subjects: set[tuple[str, str, str]] = set()
    for owner in owners:
        validate_owner_record(owner)
        interfaces.append(str(owner["interface"]))
        subject = owner["subject"]
        identity = (str(subject["repository"]), str(subject["commit"]), str(subject["tree"]))
        _require(identity not in subjects, f"DUPLICATE_OWNER_SUBJECT:{owner['interface']}")
        subjects.add(identity)
    _require(set(interfaces) == set(REQUIRED_INTERFACES), "OWNER_INTERFACE_DENOMINATOR")
    _require(len(interfaces) == len(set(interfaces)), "DUPLICATE_OWNER_INTERFACE")

    stronger = snapshot["stronger_lanes"]
    _require(isinstance(stronger, list), "STRONGER_LANES_NOT_ARRAY")
    lane_names: list[str] = []
    for item in stronger:
        lane = _strict_mapping(
            item,
            required={"lane", "state", "owner_issue"},
            name="STRONGER_LANE",
        )
        lane_name = _nonempty_string(lane["lane"], "STRONGER_LANE_NAME")
        lane_names.append(lane_name)
        _require(lane["state"] in NO_CREDIT_STATES, f"STRONGER_LANE_FALSE_CREDIT:{lane_name}")
        _issue(lane["owner_issue"], "STRONGER_LANE_OWNER_ISSUE")
    _require(set(lane_names) == EXPECTED_STRONGER_LANES, "STRONGER_LANE_DENOMINATOR")
    _require(len(lane_names) == len(set(lane_names)), "STRONGER_LANE_DUPLICATE")

    canary = _strict_mapping(
        snapshot["selected_vertical_canary"],
        required={"id", "state", "interfaces", "private_data", "external_effects", "human_operation", "purpose"},
        name="VERTICAL_CANARY",
    )
    _nonempty_string(canary["id"], "VERTICAL_CANARY_ID")
    _require(canary["state"] == "PLAN_ONLY", "VERTICAL_CANARY_FALSE_EXECUTION")
    canary_interfaces = _unique_strings(canary["interfaces"], "VERTICAL_CANARY_INTERFACES")
    _require(set(canary_interfaces) == set(REQUIRED_INTERFACES), "VERTICAL_CANARY_INTERFACE_DENOMINATOR")
    _require(canary["private_data"] is False, "VERTICAL_CANARY_PRIVATE_DATA")
    _require(canary["external_effects"] is False, "VERTICAL_CANARY_EXTERNAL_EFFECT")
    _require(canary["human_operation"] is False, "VERTICAL_CANARY_HUMAN_OPERATION")
    _nonempty_string(canary["purpose"], "VERTICAL_CANARY_PURPOSE")

    _issue(snapshot["release_owner"], "RELEASE_OWNER")
    claims = _unique_strings(snapshot["claims_not_proven"], "CLAIMS_NOT_PROVEN")
    joined = " ".join(claims).lower()
    for required_phrase in ("physical", "provider", "human", "release"):
        _require(required_phrase in joined, f"CLAIMS_NOT_PROVEN_MISSING:{required_phrase}")


def load_and_validate_convergence_json(path: str) -> Mapping[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        snapshot = json.load(handle)
    validate_convergence_snapshot(snapshot)
    return snapshot
