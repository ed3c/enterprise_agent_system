#!/usr/bin/env python3
"""Deterministic controls for the Inception four-tier policy candidate."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "evidence" / "compliance" / "four-tier-policy.example.json"
FLOW = ROOT / "evidence" / "compliance" / "telemetry-flow.example.json"
POLICY_SCHEMA = ROOT / "policies" / "provenance" / "four-tier-policy-candidate.schema.json"
FLOW_SCHEMA = ROOT / "policies" / "provenance" / "telemetry-flow.schema.json"

DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
ALLOWED_STATES = {"CANDIDATE", "BLOCKED", "UNKNOWN", "HUMAN_REVIEW_REQUIRED", "EXPIRED"}
FORBIDDEN_CONCLUSIONS = {"ADMITTED", "COMMERCIALLY_SAFE", "ZERO_LEAKAGE"}


class PolicyContractError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolicyContractError(message)


def validate_policy(value: dict[str, Any]) -> None:
    _require(value.get("schema_version") == "enterprise-agent-system/inception-four-tier-policy-candidate/v1", "schema_version")
    _require(set(value.get("dimensions", {})) == {"code", "model", "data", "trace"}, "four-tier denominator")
    _require(value.get("overall_state") in ALLOWED_STATES, "overall_state")
    _require(value.get("overall_state") not in FORBIDDEN_CONCLUSIONS, "automated legal conclusion")
    claims = value.get("claims_not_proven")
    _require(isinstance(claims, list) and claims and len(claims) == len(set(claims)), "claims_not_proven")
    for name, dimension in value["dimensions"].items():
        for field in ("subject", "version", "content_digest", "terms_digest", "obligations", "blockers", "expiry_trigger", "policy_state", "human_review_subject"):
            _require(field in dimension, f"{name}:{field}")
        _require(isinstance(dimension["subject"], str) and dimension["subject"].strip(), f"{name}:subject")
        _require(isinstance(dimension["version"], str) and dimension["version"].strip(), f"{name}:version")
        _require(bool(DIGEST.fullmatch(dimension["content_digest"])), f"{name}:content_digest")
        _require(bool(DIGEST.fullmatch(dimension["terms_digest"])), f"{name}:terms_digest")
        _require(isinstance(dimension["obligations"], list) and dimension["obligations"], f"{name}:obligations")
        _require(isinstance(dimension["blockers"], list), f"{name}:blockers")
        _require(isinstance(dimension["expiry_trigger"], str) and dimension["expiry_trigger"].strip(), f"{name}:expiry_trigger")
        _require(dimension["policy_state"] in ALLOWED_STATES, f"{name}:policy_state")
        _require(dimension["policy_state"] not in FORBIDDEN_CONCLUSIONS, f"{name}:forbidden conclusion")
        human = dimension["human_review_subject"]
        _require(human is None or (isinstance(human, str) and human.strip()), f"{name}:human_review_subject")


def validate_flow(value: dict[str, Any]) -> None:
    _require(value.get("schema_version") == "enterprise-agent-system/inception-telemetry-flow/v1", "flow schema_version")
    stages = value.get("stages")
    _require(isinstance(stages, list) and len(stages) == len(set(stages)), "stages")
    for required in ("CLASSIFY", "SANITIZE", "NEGATIVE_LEAK_CONTROLS", "EXPORT", "STORE"):
        _require(required in stages, f"missing stage:{required}")
    _require(stages.index("CLASSIFY") < stages.index("SANITIZE"), "classify before sanitize")
    _require(stages.index("SANITIZE") < stages.index("NEGATIVE_LEAK_CONTROLS"), "sanitize before leak controls")
    _require(stages.index("NEGATIVE_LEAK_CONTROLS") < stages.index("EXPORT"), "controls before export")
    _require(value.get("state") in ALLOWED_STATES, "flow state")
    _require(value.get("state") not in FORBIDDEN_CONCLUSIONS, "flow automated conclusion")
    exporter = value.get("exporter")
    _require(isinstance(exporter, dict), "exporter")
    for field in ("subject", "version", "allowlisted_destination"):
        _require(isinstance(exporter.get(field), str) and exporter[field].strip(), f"exporter:{field}")
    _require(value.get("training_use_policy") in {"PROHIBITED", "HUMAN_REVIEW_REQUIRED", "UNKNOWN"}, "training_use_policy")
    claims = value.get("claims_not_proven")
    _require(isinstance(claims, list) and claims, "flow claims_not_proven")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expect_refusal(label: str, value: dict[str, Any], validator, contains: str) -> None:
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
    bad["overall_state"] = "COMMERCIALLY_SAFE"
    expect_refusal("commercial clearance", bad, validate_policy, "overall_state")

    bad = copy.deepcopy(policy)
    bad["dimensions"]["trace"]["policy_state"] = "ADMITTED"
    expect_refusal("human authority", bad, validate_policy, "policy_state")

    bad = copy.deepcopy(flow)
    bad["stages"] = ["CLASSIFY", "EXPORT", "SANITIZE", "NEGATIVE_LEAK_CONTROLS", "STORE"]
    expect_refusal("sanitize after export", bad, validate_flow, "controls before export")

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
