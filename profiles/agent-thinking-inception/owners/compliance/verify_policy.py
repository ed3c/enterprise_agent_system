#!/usr/bin/env python3
"""Deterministic controls for the Inception four-tier policy candidate."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "evidence" / "compliance" / "four-tier-policy.example.json"
FLOW = ROOT / "evidence" / "compliance" / "telemetry-flow.example.json"
POLICY_SCHEMA = ROOT / "policies" / "provenance" / "four-tier-policy-candidate.schema.json"
FLOW_SCHEMA = ROOT / "policies" / "provenance" / "telemetry-flow.schema.json"

DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
ALLOWED_STATES = {"CANDIDATE", "BLOCKED", "UNKNOWN", "HUMAN_REVIEW_REQUIRED", "EXPIRED"}
FORBIDDEN_CONCLUSIONS = {"ADMITTED", "COMMERCIALLY_SAFE", "ZERO_LEAKAGE"}
POLICY_ROOT_KEYS = {"schema_version", "candidate_id", "dimensions", "overall_state", "claims_not_proven"}
DIMENSION_KEYS = {
    "subject", "version", "content_digest", "terms_digest", "obligations", "blockers",
    "expiry_trigger", "policy_state", "human_review_owner", "human_review_subject",
}
FLOW_ROOT_KEYS = {
    "schema_version", "flow_id", "classification", "payload_classes", "redacted_fields",
    "dropped_fields", "stages", "collector", "exporter", "storage", "access_policy",
    "retention", "deletion_policy", "training_use_policy", "negative_controls", "state",
    "claims_not_proven",
}
COMPONENT_KEYS = {"subject", "version", "config_digest"}
EXPORTER_KEYS = COMPONENT_KEYS | {"allowlisted_destination"}
ACCESS_KEYS = {"rbac_roles", "tenant_scope"}
RETENTION_KEYS = {"policy_id", "duration", "delete_after_retention"}
DELETION_KEYS = {"mode", "receipt_required", "rebuild_behavior"}
CONTROL_KEYS = {"control_id", "assertion", "evidence_lane", "expected_result"}
ALLOWED_PAYLOAD_CLASSES = {
    "PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED", "SECRET", "PII",
    "PROPRIETARY_SOURCE", "PROMPT_CONTENT",
}
ALLOWED_CONTROL_LANES = {"DETERMINISTIC_FIXTURE", "LOCAL_LIVE", "PROVIDER_LIVE", "PHYSICAL"}
ALLOWED_CONTROL_RESULTS = {"REFUSE", "REDACT", "DROP", "BLOCK_EXPORT"}


class PolicyContractError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolicyContractError(message)


def _strict_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    _require(isinstance(value, dict), f"{label}:object")
    _require(set(value) == expected, f"{label}:keys")


def _nonempty_unique_strings(value: Any, label: str) -> None:
    _require(isinstance(value, list) and value, label)
    _require(all(isinstance(item, str) and item.strip() for item in value), label)
    _require(len(value) == len(set(value)), f"{label}:unique")


def _digest(value: Any, label: str) -> None:
    _require(isinstance(value, str) and bool(DIGEST.fullmatch(value)), label)


def validate_policy(value: dict[str, Any]) -> None:
    _strict_keys(value, POLICY_ROOT_KEYS, "policy")
    _require(value["schema_version"] == "enterprise-agent-system/inception-four-tier-policy-candidate/v1", "schema_version")
    _require(isinstance(value["candidate_id"], str) and value["candidate_id"].strip(), "candidate_id")
    _require(isinstance(value["dimensions"], dict), "dimensions")
    _require(set(value["dimensions"]) == {"code", "model", "data", "trace"}, "four-tier denominator")
    _require(value["overall_state"] in ALLOWED_STATES, "overall_state")
    _require(value["overall_state"] not in FORBIDDEN_CONCLUSIONS, "automated legal conclusion")
    _nonempty_unique_strings(value["claims_not_proven"], "claims_not_proven")

    for name, dimension in value["dimensions"].items():
        _strict_keys(dimension, DIMENSION_KEYS, f"{name}:dimension")
        _require(isinstance(dimension["subject"], str) and dimension["subject"].strip(), f"{name}:subject")
        _require(isinstance(dimension["version"], str) and dimension["version"].strip(), f"{name}:version")
        _digest(dimension["content_digest"], f"{name}:content_digest")
        _digest(dimension["terms_digest"], f"{name}:terms_digest")
        _nonempty_unique_strings(dimension["obligations"], f"{name}:obligations")
        _require(isinstance(dimension["blockers"], list), f"{name}:blockers")
        _require(all(isinstance(item, str) and item.strip() for item in dimension["blockers"]), f"{name}:blockers")
        _require(len(dimension["blockers"]) == len(set(dimension["blockers"])), f"{name}:blockers:unique")
        _require(isinstance(dimension["expiry_trigger"], str) and dimension["expiry_trigger"].strip(), f"{name}:expiry_trigger")
        _require(dimension["policy_state"] in ALLOWED_STATES, f"{name}:policy_state")
        _require(dimension["policy_state"] not in FORBIDDEN_CONCLUSIONS, f"{name}:forbidden conclusion")
        _require(isinstance(dimension["human_review_owner"], str) and dimension["human_review_owner"].strip(), f"{name}:human_review_owner")
        human = dimension["human_review_subject"]
        _require(human is None or (isinstance(human, str) and human.strip()), f"{name}:human_review_subject")


def _validate_component(value: dict[str, Any], keys: set[str], label: str) -> None:
    _strict_keys(value, keys, label)
    for field in ("subject", "version"):
        _require(isinstance(value[field], str) and value[field].strip(), f"{label}:{field}")
    _digest(value["config_digest"], f"{label}:config_digest")


def validate_flow(value: dict[str, Any]) -> None:
    _strict_keys(value, FLOW_ROOT_KEYS, "flow")
    _require(value["schema_version"] == "enterprise-agent-system/inception-telemetry-flow/v1", "flow schema_version")
    _require(isinstance(value["flow_id"], str) and value["flow_id"].strip(), "flow_id")
    _require(value["classification"] in {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"}, "classification")

    payload_classes = value["payload_classes"]
    _nonempty_unique_strings(payload_classes, "payload_classes")
    _require(set(payload_classes) <= ALLOWED_PAYLOAD_CLASSES, "payload_classes:enum")
    _nonempty_unique_strings(value["redacted_fields"], "redacted_fields")
    _nonempty_unique_strings(value["dropped_fields"], "dropped_fields")

    stages = value["stages"]
    _require(isinstance(stages, list) and len(stages) == len(set(stages)), "stages")
    required_stages = ["CLASSIFY", "SANITIZE", "NEGATIVE_LEAK_CONTROLS", "EXPORT", "STORE", "DELETE"]
    _require(set(stages) == set(required_stages), "stages:denominator")
    for left, right in zip(required_stages, required_stages[1:]):
        _require(stages.index(left) < stages.index(right), f"stage order:{left}->{right}")

    _validate_component(value["collector"], COMPONENT_KEYS, "collector")
    _validate_component(value["exporter"], EXPORTER_KEYS, "exporter")
    _require(isinstance(value["exporter"]["allowlisted_destination"], str) and value["exporter"]["allowlisted_destination"].strip(), "exporter:allowlisted_destination")
    _validate_component(value["storage"], COMPONENT_KEYS, "storage")

    _strict_keys(value["access_policy"], ACCESS_KEYS, "access_policy")
    _nonempty_unique_strings(value["access_policy"]["rbac_roles"], "access_policy:rbac_roles")
    _require(isinstance(value["access_policy"]["tenant_scope"], str) and value["access_policy"]["tenant_scope"].strip(), "access_policy:tenant_scope")

    _strict_keys(value["retention"], RETENTION_KEYS, "retention")
    _require(isinstance(value["retention"]["policy_id"], str) and value["retention"]["policy_id"].strip(), "retention:policy_id")
    _require(isinstance(value["retention"]["duration"], str) and value["retention"]["duration"].strip(), "retention:duration")
    _require(value["retention"]["delete_after_retention"] is True, "retention:delete_after_retention")

    _strict_keys(value["deletion_policy"], DELETION_KEYS, "deletion_policy")
    _require(value["deletion_policy"]["mode"] in {"DELETE", "TOMBSTONE_THEN_DELETE", "REBUILD_WITHOUT_SUBJECT"}, "deletion_policy:mode")
    _require(value["deletion_policy"]["receipt_required"] is True, "deletion_policy:receipt_required")
    _require(isinstance(value["deletion_policy"]["rebuild_behavior"], str) and value["deletion_policy"]["rebuild_behavior"].strip(), "deletion_policy:rebuild_behavior")

    _require(value["training_use_policy"] in {"PROHIBITED", "HUMAN_REVIEW_REQUIRED", "UNKNOWN"}, "training_use_policy")
    controls = value["negative_controls"]
    _require(isinstance(controls, list) and controls, "negative_controls")
    seen: set[str] = set()
    for control in controls:
        _strict_keys(control, CONTROL_KEYS, "negative_control")
        _require(isinstance(control["control_id"], str) and control["control_id"].strip(), "negative_control:control_id")
        _require(control["control_id"] not in seen, "negative_control:duplicate")
        seen.add(control["control_id"])
        _require(isinstance(control["assertion"], str) and control["assertion"].strip(), "negative_control:assertion")
        _require(control["evidence_lane"] in ALLOWED_CONTROL_LANES, "negative_control:evidence_lane")
        _require(control["expected_result"] in ALLOWED_CONTROL_RESULTS, "negative_control:expected_result")

    _require(value["state"] in ALLOWED_STATES, "flow state")
    _require(value["state"] not in FORBIDDEN_CONCLUSIONS, "flow automated conclusion")
    _nonempty_unique_strings(value["claims_not_proven"], "flow claims_not_proven")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expect_refusal(label: str, value: dict[str, Any], validator: Callable[[dict[str, Any]], None], contains: str) -> None:
    try:
        validator(value)
    except PolicyContractError as exc:
        _require(contains in str(exc), f"{label}:wrong refusal:{exc}")
        return
    raise AssertionError(f"{label}: mutation was not refused")


def selftest() -> None:
    policy = load(POLICY)
    flow = load(FLOW)

    bad = copy.deepcopy(policy)
    del bad["dimensions"]["data"]
    expect_refusal("missing dimension", bad, validate_policy, "four-tier")

    bad = copy.deepcopy(policy)
    bad["dimensions"]["code"]["terms_digest"] = "latest"
    expect_refusal("mutable terms", bad, validate_policy, "terms_digest")

    bad = copy.deepcopy(policy)
    bad["dimensions"]["model"]["obligations"] = []
    expect_refusal("missing obligations", bad, validate_policy, "obligations")

    bad = copy.deepcopy(policy)
    bad["dimensions"]["model"]["human_review_owner"] = ""
    expect_refusal("missing human owner", bad, validate_policy, "human_review_owner")

    bad = copy.deepcopy(policy)
    bad["dimensions"]["trace"]["unexpected"] = true if False else "not-allowed"
    expect_refusal("unknown nested policy field", bad, validate_policy, "dimension:keys")

    bad = copy.deepcopy(policy)
    bad["overall_state"] = "COMMERCIALLY_SAFE"
    expect_refusal("commercial clearance", bad, validate_policy, "overall_state")

    bad = copy.deepcopy(policy)
    bad["dimensions"]["trace"]["policy_state"] = "ADMITTED"
    expect_refusal("human authority", bad, validate_policy, "policy_state")

    bad = copy.deepcopy(flow)
    bad["stages"] = ["CLASSIFY", "EXPORT", "SANITIZE", "NEGATIVE_LEAK_CONTROLS", "STORE", "DELETE"]
    expect_refusal("sanitize after export", bad, validate_flow, "stage order:NEGATIVE_LEAK_CONTROLS->EXPORT")

    bad = copy.deepcopy(flow)
    bad["redacted_fields"] = []
    expect_refusal("missing redaction denominator", bad, validate_flow, "redacted_fields")

    bad = copy.deepcopy(flow)
    bad["access_policy"]["rbac_roles"] = []
    expect_refusal("missing rbac", bad, validate_flow, "rbac_roles")

    bad = copy.deepcopy(flow)
    bad["stages"].remove("DELETE")
    expect_refusal("missing delete stage", bad, validate_flow, "stages:denominator")

    bad = copy.deepcopy(flow)
    bad["deletion_policy"]["receipt_required"] = False
    expect_refusal("deletion receipt optional", bad, validate_flow, "receipt_required")

    bad = copy.deepcopy(flow)
    bad["negative_controls"] = []
    expect_refusal("missing leak controls", bad, validate_flow, "negative_controls")

    bad = copy.deepcopy(flow)
    bad["exporter"]["unexpected"] = "not-allowed"
    expect_refusal("unknown nested flow field", bad, validate_flow, "exporter:keys")

    bad = copy.deepcopy(flow)
    bad["state"] = "ZERO_LEAKAGE"
    expect_refusal("zero leakage", bad, validate_flow, "flow state")

    bad = copy.deepcopy(flow)
    bad["exporter"]["version"] = ""
    expect_refusal("mutable exporter", bad, validate_flow, "exporter:version")


def main() -> int:
    for schema in (POLICY_SCHEMA, FLOW_SCHEMA):
        loaded = load(schema)
        _require(loaded.get("additionalProperties") is False, f"open schema:{schema.name}")
    validate_policy(load(POLICY))
    validate_flow(load(FLOW))
    selftest()
    print("PASS inception-a4 four-tier policy and telemetry disagreement controls")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PolicyContractError, AssertionError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
