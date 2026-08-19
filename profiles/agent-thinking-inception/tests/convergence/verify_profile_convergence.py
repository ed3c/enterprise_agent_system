#!/usr/bin/env python3
"""Fail-closed verifier for Agent Thinking Inception profile convergence."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
REQ_DIR = ROOT / "requirements"
CLOSURE = ROOT / "plans" / "closure-record.json"
CANARY = ROOT / "plans" / "vertical-canary.json"

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REPOSITORY = re.compile(r"^[^/\s]+/[^/\s]+$")

BANNED_PROFILE_STATES = {
    "LIVE_OR_PHYSICAL_EVIDENCE_VERIFIED",
    "USER_OUTCOME_VERIFIED",
    "HUMAN_ADMITTED",
    "RELEASED",
    "OPERATED_WITH_ROLLBACK",
}
ALLOWED_CONTRADICTION_STATES = {
    "PRESERVED_BLOCKED",
    "PRESERVED_WITH_PARTIAL_CONTROL",
}
EXPECTED_GENERIC_X = {
    "repository": "ed3c/enterprise_agent_system",
    "pull_request": 31,
    "commit": "3f8af3d75b28ca1904fe07b8ea9ee0d291f5989c",
    "tree": "e1be41234ff336297ce591b564291c9a0cd819ed",
    "shadow_review": 4973461122,
    "relationship": "PROCESS_EVIDENCE_DEPENDENCY_NOT_GIT_PARENT",
}
EXPECTED_PROFILE_PARENT = {
    "repository": "ed3c/enterprise_agent_system",
    "pull_request": 29,
    "commit": "6e0a916fd06dd8635d77c9a8c4d1b475185ea13e",
    "tree": "c3851a6953d456d0342a9776eed28561c1af0ca1",
    "relationship": "TRUE_GIT_PARENT",
}
EXPECTED_PROFILE_SHADOW = {
    "issue": "https://github.com/ed3c/enterprise_agent_system/issues/19",
    "comment_id": 5343381027,
    "verdict": "PUBLIC_VERIFICATION_DENOMINATOR_ADMITTED",
    "aggregate_state": "BLOCKED_FOR_CLOSURE",
}
EXPECTED_SOURCE_BLOBS = {
    "manifest": "06698be5e2a5d7b583078ec8b282f6c6c1f98198",
    "control": "160be43c55f7c031e48abb4ebe264dcbd93150fb",
    "assurance": "ddac27b1ca1b2c5f2fbc57f5c02018f89ed74cfe",
    "delivery": "565a9227a9ef0d1eda3cc57a90727859bf56f1f5",
    "contradictions": "ecbb4e5faa0df3b1acf3a0fbf506bb7c44dc76f8",
}


class ProfileConvergenceError(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ProfileConvergenceError(reason)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"NOT_OBJECT:{path}")
    return value


def strict_keys(value: dict[str, Any], expected: set[str], reason: str) -> None:
    require(set(value) == expected, f"{reason}:missing={sorted(expected - set(value))}:extra={sorted(set(value) - expected)}")


def exact_subject(value: Any, reason: str) -> None:
    require(isinstance(value, dict), f"{reason}:NOT_OBJECT")
    strict_keys(value, {"repository", "commit", "tree"}, reason)
    require(isinstance(value["repository"], str) and REPOSITORY.fullmatch(value["repository"]) is not None, f"{reason}:REPOSITORY")
    require(isinstance(value["commit"], str) and SHA40.fullmatch(value["commit"]) is not None, f"{reason}:COMMIT")
    require(isinstance(value["tree"], str) and SHA40.fullmatch(value["tree"]) is not None, f"{reason}:TREE")


def source_requirements() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    requirements: dict[str, dict[str, Any]] = {}
    for name in ("control-requirements.json", "assurance-requirements.json", "delivery-requirements.json"):
        shard = load_json(REQ_DIR / name)
        require(shard.get("schema_version") == "enterprise-agent-system/inception-requirement-shard/v1", f"SOURCE_SCHEMA:{name}")
        for item in shard.get("requirements", []):
            rid = item.get("requirement_id")
            require(isinstance(rid, str) and rid.startswith("REQ-PDF-INCEPTION-"), f"SOURCE_REQUIREMENT_ID:{name}")
            require(rid not in requirements, f"SOURCE_REQUIREMENT_DUPLICATE:{rid}")
            requirements[rid] = item
    contradictions_source = load_json(REQ_DIR / "contradictions.json")
    require(contradictions_source.get("schema_version") == "enterprise-agent-system/inception-contradictions/v1", "CONTRADICTION_SOURCE_SCHEMA")
    contradictions: dict[str, dict[str, Any]] = {}
    for item in contradictions_source.get("items", []):
        cid = item.get("id")
        require(isinstance(cid, str) and cid.startswith("UNK-INCEPTION-"), "CONTRADICTION_SOURCE_ID")
        require(cid not in contradictions, f"CONTRADICTION_SOURCE_DUPLICATE:{cid}")
        contradictions[cid] = item
    require(len(requirements) == 15, f"SOURCE_REQUIREMENT_DENOMINATOR:{len(requirements)}")
    require(len(contradictions) == 14, f"SOURCE_CONTRADICTION_DENOMINATOR:{len(contradictions)}")
    return requirements, contradictions


def canary_contract_digest(canary: dict[str, Any]) -> str:
    payload = json.dumps(canary["contract"], sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def validate_canary(canary: dict[str, Any]) -> None:
    require(canary.get("schema_version") == "enterprise-agent-system/inception-profile-vertical-canary/v1", "CANARY_SCHEMA")
    require(canary.get("profile_id") == "PROFILE-AGENT-THINKING-INCEPTION-001", "CANARY_PROFILE")
    require(canary.get("canary_id") == "INCEPTION-P5-PUBLIC-REVERSIBLE-CHAIN", "CANARY_ID")
    require(canary.get("state") == "PLAN_ONLY", "CANARY_FALSE_EXECUTION")
    require(isinstance(canary.get("contract_digest"), str) and SHA256.fullmatch(canary["contract_digest"]) is not None, "CANARY_DIGEST_SHAPE")
    require(canary_contract_digest(canary) == canary["contract_digest"], "CANARY_DIGEST_MISMATCH")
    contract = canary.get("contract")
    require(isinstance(contract, dict), "CANARY_CONTRACT")
    require(contract.get("generic_x") == {"commit": EXPECTED_GENERIC_X["commit"], "tree": EXPECTED_GENERIC_X["tree"], "shadow_review": EXPECTED_GENERIC_X["shadow_review"]}, "CANARY_GENERIC_X_DRIFT")
    constraints = contract.get("constraints")
    require(isinstance(constraints, dict), "CANARY_CONSTRAINTS")
    for key in ("private_data", "external_effects", "human_operation", "provider_enrollment", "network_claim", "production_claim"):
        require(constraints.get(key) is False, f"CANARY_AUTHORITY_WIDENING:{key}")
    require(canary.get("execution_receipt") is None, "CANARY_EXECUTION_RECEIPT_FALSE_CLAIM")
    receipts = canary.get("independent_receipts")
    require(isinstance(receipts, dict), "CANARY_RECEIPTS")
    require(receipts.get("profile_shadow", {}).get("id") == EXPECTED_PROFILE_SHADOW["comment_id"], "CANARY_PROFILE_SHADOW")
    require(receipts.get("profile_shadow", {}).get("aggregate_state") == "BLOCKED_FOR_CLOSURE", "CANARY_PROFILE_SHADOW_PROMOTION")
    require(receipts.get("generic_x_shadow", {}).get("id") == EXPECTED_GENERIC_X["shadow_review"], "CANARY_GENERIC_X_SHADOW")
    truth = receipts.get("truth_verify")
    require(isinstance(truth, dict), "CANARY_TRUTH_VERIFY")
    require(truth.get("repository") == "ed3c/truth-verify-loop", "CANARY_TRUTH_VERIFY_REPOSITORY")
    require(truth.get("commit") == "5ea4dd42d2ee5bbd22537f5426cd276f10222980", "CANARY_TRUTH_VERIFY_COMMIT")
    require(truth.get("tree") == "fc6486b9ab6a48752e32a536a847c6e5635f8547", "CANARY_TRUTH_VERIFY_TREE")
    require(truth.get("hosted_runs") == [32260293092, 32260291970], "CANARY_TRUTH_VERIFY_RUNS")


def validate_closure(closure: dict[str, Any], canary: dict[str, Any]) -> None:
    source_req, source_contradictions = source_requirements()
    require(closure.get("schema_version") == "enterprise-agent-system/inception-profile-closure/v1", "CLOSURE_SCHEMA")
    require(closure.get("profile_id") == "PROFILE-AGENT-THINKING-INCEPTION-001", "CLOSURE_PROFILE")
    require(closure.get("state") == "PROFILE_CLOSURE_CANDIDATE_BLOCKED_STRONGER_LANES", "CLOSURE_STATE_PROMOTION")
    require(closure.get("profile_parent") == EXPECTED_PROFILE_PARENT, "PROFILE_PARENT_DRIFT")
    require(closure.get("generic_x_dependency") == EXPECTED_GENERIC_X, "GENERIC_X_DRIFT_OR_FALSE_PARENT")
    require(closure.get("profile_shadow_dependency") == EXPECTED_PROFILE_SHADOW, "PROFILE_SHADOW_DRIFT_OR_PROMOTION")
    require(closure.get("requirement_source_blobs") == EXPECTED_SOURCE_BLOBS, "SOURCE_BLOB_DRIFT")

    requirements = closure.get("requirements")
    require(isinstance(requirements, list), "REQUIREMENTS_NOT_ARRAY")
    indexed: dict[str, dict[str, Any]] = {}
    for item in requirements:
        require(isinstance(item, dict), "REQUIREMENT_NOT_OBJECT")
        rid = item.get("requirement_id")
        require(isinstance(rid, str) and rid in source_req, f"REQUIREMENT_UNKNOWN:{rid}")
        require(rid not in indexed, f"REQUIREMENT_DUPLICATE:{rid}")
        indexed[rid] = item
        required_fields = {
            "requirement_id", "canonical_owner_repository", "owner_issue", "owner_subject", "evidence_subject",
            "required_evidence_lane", "observed_evidence_lane", "observed_state", "required_lane_satisfied",
            "closure_credit", "blockers", "next_transition"
        }
        strict_keys(item, required_fields, f"REQUIREMENT_FIELDS:{rid}")
        source_owner = source_req[rid].get("owner", {})
        require(item["canonical_owner_repository"] == source_owner.get("repository"), f"REQUIREMENT_OWNER_SUBSTITUTION:{rid}")
        require(item["owner_issue"] == source_owner.get("issue"), f"REQUIREMENT_OWNER_ISSUE:{rid}")
        exact_subject(item["owner_subject"], f"REQUIREMENT_OWNER_SUBJECT:{rid}")
        exact_subject(item["evidence_subject"], f"REQUIREMENT_EVIDENCE_SUBJECT:{rid}")
        require(item["owner_subject"]["repository"] == item["canonical_owner_repository"], f"REQUIREMENT_OWNER_SUBJECT_REPOSITORY:{rid}")
        require(item["required_evidence_lane"] == source_req[rid].get("required_evidence_lane"), f"REQUIREMENT_REQUIRED_LANE_DRIFT:{rid}")
        require(isinstance(item["observed_evidence_lane"], str) and item["observed_evidence_lane"], f"REQUIREMENT_OBSERVED_LANE:{rid}")
        require(isinstance(item["observed_state"], str) and item["observed_state"] not in BANNED_PROFILE_STATES, f"REQUIREMENT_FALSE_LATE_STATE:{rid}")
        require(isinstance(item["required_lane_satisfied"], bool), f"REQUIREMENT_REQUIRED_LANE_FLAG:{rid}")
        require(item["closure_credit"] == 0, f"REQUIREMENT_FALSE_CLOSURE_CREDIT:{rid}")
        require(isinstance(item["blockers"], list) and item["blockers"], f"REQUIREMENT_BLOCKER_MISSING:{rid}")
        require(isinstance(item["next_transition"], str) and item["next_transition"], f"REQUIREMENT_NEXT_TRANSITION:{rid}")
    require(set(indexed) == set(source_req), "REQUIREMENT_DENOMINATOR")

    contradictions = closure.get("contradictions")
    require(isinstance(contradictions, list), "CONTRADICTIONS_NOT_ARRAY")
    contradiction_index: dict[str, dict[str, Any]] = {}
    for item in contradictions:
        require(isinstance(item, dict), "CONTRADICTION_NOT_OBJECT")
        cid = item.get("id")
        require(isinstance(cid, str) and cid in source_contradictions, f"CONTRADICTION_UNKNOWN:{cid}")
        require(cid not in contradiction_index, f"CONTRADICTION_DUPLICATE:{cid}")
        contradiction_index[cid] = item
        strict_keys(item, {"id", "owner_issue", "state", "control_evidence", "remaining_blocker"}, f"CONTRADICTION_FIELDS:{cid}")
        require(item["owner_issue"] == source_contradictions[cid].get("owner_issue"), f"CONTRADICTION_OWNER_ISSUE:{cid}")
        require(item["state"] in ALLOWED_CONTRADICTION_STATES, f"CONTRADICTION_FALSE_RESOLUTION:{cid}")
        require(isinstance(item["control_evidence"], str) and item["control_evidence"], f"CONTRADICTION_CONTROL_EVIDENCE:{cid}")
        require(isinstance(item["remaining_blocker"], str) and item["remaining_blocker"], f"CONTRADICTION_BLOCKER:{cid}")
    require(set(contradiction_index) == set(source_contradictions), "CONTRADICTION_DENOMINATOR")

    selected = closure.get("selected_vertical_canary")
    require(isinstance(selected, dict), "SELECTED_CANARY")
    require(selected.get("contract_digest") == canary.get("contract_digest"), "SELECTED_CANARY_DIGEST_DRIFT")
    require(selected.get("state") == "PLAN_ONLY", "SELECTED_CANARY_FALSE_EXECUTION")
    require(selected.get("execution_receipt") is None, "SELECTED_CANARY_FALSE_RECEIPT")
    summary = closure.get("closure_summary")
    require(isinstance(summary, dict), "CLOSURE_SUMMARY")
    expected_summary = {
        "requirements_total": 15,
        "requirements_with_exact_owner_subject": 15,
        "requirements_required_lane_satisfied": 1,
        "requirements_closure_credit": 0,
        "contradictions_total": 14,
        "contradictions_preserved": 14,
        "profile_shadow": "BLOCKED_FOR_CLOSURE",
        "generic_x": "ADMIT_FOR_DOWNSTREAM_REVIEW",
        "profile_release_state": "NOT_ADMITTED",
    }
    require(summary == expected_summary, "CLOSURE_SUMMARY_PROMOTION_OR_DRIFT")
    claims = closure.get("claims_not_proven")
    require(isinstance(claims, list) and claims, "CLAIMS_NOT_PROVEN")
    joined = " ".join(str(item) for item in claims).lower()
    for word in ("physical", "provider", "human", "release"):
        require(word in joined, f"CLAIMS_NOT_PROVEN_MISSING:{word}")
    require(closure.get("next_transition") == "PROFILE_SHADOW_REVIEW_THEN_P6_DOCUMENTATION_CONVERGENCE", "NEXT_TRANSITION_DRIFT")
    validate_canary(canary)


def verify() -> None:
    manifest = load_json(REQ_DIR / "requirements.json")
    require(manifest.get("denominator") == {"total": 15, "states": {"SOURCE_PROPOSAL": 13, "OWNER_PROPOSED": 2}, "closure_credit": 0}, "SOURCE_MANIFEST_DENOMINATOR_DRIFT")
    closure = load_json(CLOSURE)
    canary = load_json(CANARY)
    validate_closure(closure, canary)
    print("PASS inception-x profile convergence requirements=15 contradictions=14 canary=PLAN_ONLY")


def expect_refusal(label: str, operation: Callable[[], None], pattern: str) -> None:
    try:
        operation()
    except ProfileConvergenceError as exc:
        require(pattern in str(exc), f"SELFTEST_WRONG_REFUSAL:{label}:{exc}")
        return
    raise ProfileConvergenceError(f"SELFTEST_NOT_REFUSED:{label}")


def selftest() -> None:
    closure = load_json(CLOSURE)
    canary = load_json(CANARY)
    source_req, source_contradictions = source_requirements()
    controls = 0

    for rid in sorted(source_req):
        mutated = copy.deepcopy(closure)
        mutated["requirements"] = [item for item in mutated["requirements"] if item["requirement_id"] != rid]
        expect_refusal(f"missing requirement {rid}", lambda m=mutated: validate_closure(m, canary), "REQUIREMENT_DENOMINATOR")
        controls += 1

    for cid in sorted(source_contradictions):
        mutated = copy.deepcopy(closure)
        mutated["contradictions"] = [item for item in mutated["contradictions"] if item["id"] != cid]
        expect_refusal(f"missing contradiction {cid}", lambda m=mutated: validate_closure(m, canary), "CONTRADICTION_DENOMINATOR")
        controls += 1

        promoted = copy.deepcopy(closure)
        target = next(item for item in promoted["contradictions"] if item["id"] == cid)
        target["state"] = "RESOLVED"
        expect_refusal(f"false contradiction resolution {cid}", lambda m=promoted: validate_closure(m, canary), f"CONTRADICTION_FALSE_RESOLUTION:{cid}")
        controls += 1

    owner_swap = copy.deepcopy(closure)
    target = next(item for item in owner_swap["requirements"] if item["requirement_id"] == "REQ-PDF-INCEPTION-TELEMETRY-001")
    target["canonical_owner_repository"] = "ed3c/enterprise_agent_system"
    expect_refusal("telemetry owner substitution", lambda: validate_closure(owner_swap, canary), "REQUIREMENT_OWNER_SUBSTITUTION:REQ-PDF-INCEPTION-TELEMETRY-001")
    controls += 1

    fake_parent = copy.deepcopy(closure)
    fake_parent["generic_x_dependency"]["relationship"] = "TRUE_GIT_PARENT"
    expect_refusal("generic X false git parent", lambda: validate_closure(fake_parent, canary), "GENERIC_X_DRIFT_OR_FALSE_PARENT")
    controls += 1

    shadow_promotion = copy.deepcopy(closure)
    shadow_promotion["profile_shadow_dependency"]["aggregate_state"] = "ADMIT_FOR_CLOSURE"
    expect_refusal("profile Shadow promotion", lambda: validate_closure(shadow_promotion, canary), "PROFILE_SHADOW_DRIFT_OR_PROMOTION")
    controls += 1

    closure_credit = copy.deepcopy(closure)
    closure_credit["requirements"][0]["closure_credit"] = 1
    expect_refusal("requirement closure laundering", lambda: validate_closure(closure_credit, canary), "REQUIREMENT_FALSE_CLOSURE_CREDIT")
    controls += 1

    executed = copy.deepcopy(canary)
    executed["state"] = "EXECUTED"
    expect_refusal("canary execution promotion", lambda: validate_canary(executed), "CANARY_FALSE_EXECUTION")
    controls += 1

    authority = copy.deepcopy(canary)
    authority["contract"]["constraints"]["external_effects"] = True
    expect_refusal("canary external effect authority", lambda: validate_canary(authority), "CANARY_DIGEST_MISMATCH")
    controls += 1

    missing_truth = copy.deepcopy(canary)
    del missing_truth["independent_receipts"]["truth_verify"]
    expect_refusal("missing Truth Verify receipt", lambda: validate_canary(missing_truth), "CANARY_TRUTH_VERIFY")
    controls += 1

    print(f"PASS inception-x planted refusals={controls} contradiction-replays={len(source_contradictions) * 2}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    try:
        if args.selftest:
            selftest()
        else:
            verify()
    except ProfileConvergenceError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
