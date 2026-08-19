#!/usr/bin/env python3
"""Fail-closed profile-specific Shadow reconciliation for Agent Thinking Inception."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "shadow" / "profile-shadow-review.json"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
EXPECTED_ATOMS = ("A1", "A2R", "A2", "A3", "A4", "A5", "A6")
EXPECTED_OWNERS = {
    "A1": "ed3c/bettor-arena",
    "A2R": "ed3c/runtime-env",
    "A2": "ed3c/agent-shield-monorepo",
    "A3": "ed3c/truth-verify-loop",
    "A4": "ed3c/enterprise_agent_system",
    "A5": "ed3c/bettor-arena",
    "A6": "ed3c/bettor-arena",
}
EXPECTED_REQUIREMENTS = {
    "REQ-PDF-INCEPTION-STATE-001",
    "REQ-PDF-INCEPTION-DAG-001",
    "REQ-PDF-INCEPTION-CONTEXT-001",
    "REQ-PDF-INCEPTION-CONTEXT-002",
    "REQ-PDF-INCEPTION-CONTEXT-003",
    "REQ-PDF-INCEPTION-STEERING-001",
    "REQ-PDF-INCEPTION-SANDBOX-001",
    "REQ-PDF-INCEPTION-EVIDENCE-001",
    "REQ-PDF-INCEPTION-EVIDENCE-002",
    "REQ-PDF-INCEPTION-COMPLIANCE-001",
    "REQ-PDF-INCEPTION-TELEMETRY-001",
    "REQ-PDF-INCEPTION-CONVERGE-001",
    "REQ-PDF-INCEPTION-INGRESS-001",
    "REQ-PDF-INCEPTION-INGRESS-002",
    "REQ-PDF-INCEPTION-HITL-001",
}
NO_CREDIT_STATES = {
    "NOT_EXERCISED",
    "NOT_PERFORMED",
    "NOT_VERIFIED",
    "HUMAN_ADMIT_REQUIRED",
    "UNBOUND",
    "BLOCKED",
}


class ProfileShadowError(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ProfileShadowError(reason)


def exact_subject(value: dict[str, Any], label: str) -> None:
    require(value.get("repository") and "/" in value["repository"], f"{label}_REPOSITORY")
    require(HEX40.fullmatch(str(value.get("commit", ""))) is not None, f"{label}_COMMIT")
    require(HEX40.fullmatch(str(value.get("tree", ""))) is not None, f"{label}_TREE")


def validate(snapshot: dict[str, Any]) -> dict[str, Any]:
    require(
        snapshot.get("schema_version")
        == "enterprise-agent-system/inception-profile-shadow/v1",
        "SCHEMA_VERSION",
    )
    require(snapshot.get("profile_id") == "PROFILE-AGENT-THINKING-INCEPTION-001", "PROFILE_ID")

    source = snapshot["source_subject"]
    require(source["id"] == "SRC-PDF-INCEPTION-001", "SOURCE_ID")
    require(DIGEST.fullmatch(source["digest"]) is not None, "SOURCE_DIGEST")
    require(source["class"] == "SOURCE_PROPOSAL", "SOURCE_PROMOTED")
    require(source["claims_current_fact"] is False, "SOURCE_PROMOTED_TO_CURRENT_FACT")

    exact_subject(snapshot["profile_k_subject"], "PROFILE_K")
    exact_subject(snapshot["generic_shadow_subject"], "GENERIC_SHADOW")
    base = snapshot["profile_shadow_base"]
    require(HEX40.fullmatch(base["commit"]) is not None, "SHADOW_BASE_COMMIT")
    require(
        base["parents"]
        == [
            snapshot["generic_shadow_subject"]["commit"],
            snapshot["profile_k_subject"]["commit"],
        ],
        "SHADOW_MULTI_PARENT_BINDING",
    )

    shadow = snapshot["shadow"]
    require(shadow == {"read_only": True, "separate_evaluation_path": True, "may_commit": []}, "SHADOW_AUTHORITY")

    receipt = snapshot["public_denominator_receipt"]
    require(receipt["kind"] == "ISSUE_COMMENT", "SHADOW_RECEIPT_KIND")
    require(receipt["receipt_class"] == "PROFILE_PUBLIC_DENOMINATOR", "SHADOW_RECEIPT_CLASS")
    require(receipt["comment_id"] == 5343381027, "SHADOW_RECEIPT_ID")
    require(receipt["state"] == "PUBLIC_VERIFICATION_DENOMINATOR_ADMITTED", "SHADOW_RECEIPT_STATE")

    owners = snapshot["owners"]
    require(len(owners) == 7, "OWNER_DENOMINATOR")
    atoms = [item["atom"] for item in owners]
    require(tuple(atoms) == EXPECTED_ATOMS, "OWNER_ORDER_OR_DENOMINATOR")
    require(len({item["interface"] for item in owners}) == 7, "DUPLICATE_OWNER_INTERFACE")
    require(len({(item["repository"], item["commit"], item["tree"]) for item in owners}) == 7, "DUPLICATE_EXACT_SUBJECT")
    for owner in owners:
        atom = owner["atom"]
        require(owner["repository"] == EXPECTED_OWNERS[atom], f"OWNER_SUBSTITUTION:{atom}")
        require(isinstance(owner["pull_request"], int) and owner["pull_request"] > 0, f"OWNER_PR:{atom}")
        exact_subject(owner, f"OWNER_{atom}")
        require(owner["hosted_runs"] and all(isinstance(x, int) and x > 0 for x in owner["hosted_runs"]), f"HOSTED_RUNS:{atom}")
        require(owner["public_evidence"], f"PUBLIC_EVIDENCE:{atom}")
        require(owner["no_credit"], f"NO_CREDIT_DENOMINATOR:{atom}")

    requirements = snapshot["requirements"]
    requirement_ids = {item["requirement_id"] for item in requirements}
    require(len(requirements) == 15 and requirement_ids == EXPECTED_REQUIREMENTS, "REQUIREMENT_DENOMINATOR")
    require(all(item["owner_atom"] for item in requirements), "REQUIREMENT_OWNER_ABSENT")

    contradictions = snapshot["contradictions"]
    require(len(contradictions) == 14, "CONTRADICTION_DENOMINATOR")
    require(
        [item["id"] for item in contradictions]
        == [f"UNK-INCEPTION-{i:03d}" for i in range(1, 15)],
        "CONTRADICTION_IDENTITY",
    )
    require(all(item["state"] == "PUBLIC_CONTROL_PRESENT" for item in contradictions), "CONTRADICTION_CONTROL_STATE")
    require(all(item["owner_route"] for item in contradictions), "CONTRADICTION_OWNER_ROUTE")

    attempts = snapshot["attempts"]
    require(snapshot["attempt_denominator"] == len(attempts), "ATTEMPT_DENOMINATOR_DROPPED")
    attempt_ids = [item["id"] for item in attempts]
    require(len(attempt_ids) == len(set(attempt_ids)), "DUPLICATE_ATTEMPT")
    require(any(item["state"] == "FAIL" for item in attempts), "FAILED_ATTEMPTS_ERASED")
    require(any(item["state"] == "BLOCKED" for item in attempts), "BLOCKED_ATTEMPTS_ERASED")
    require(all(item["state"] in {"PASS", "FAIL", "BLOCKED"} for item in attempts), "ATTEMPT_STATE")

    lanes = snapshot["stronger_lanes"]
    require(len(lanes) == 13, "STRONGER_LANE_DENOMINATOR")
    require(len({item["lane"] for item in lanes}) == 13, "DUPLICATE_STRONGER_LANE")
    require(all(item["state"] in NO_CREDIT_STATES for item in lanes), "STRONGER_LANE_PROMOTION")

    closure = snapshot["closure"]
    require(closure["highest_state"] == "DETERMINISTIC_EVIDENCE_VERIFIED", "FALSE_CLOSURE_PROMOTION")
    require(closure["profile_verdict"] == "ADMIT_FOR_PROFILE_CONVERGENCE", "PROFILE_VERDICT")
    require(closure["full_architecture_verdict"] == "BLOCKED_FOR_CLOSURE", "FULL_CLOSURE_PROMOTED")

    claims = snapshot["claims_not_proven"]
    require(isinstance(claims, list) and claims and len(claims) == len(set(claims)), "CLAIMS_NOT_PROVEN")

    digest = snapshot["snapshot_digest"]
    require(DIGEST.fullmatch(digest) is not None, "SNAPSHOT_DIGEST")
    unsigned = dict(snapshot)
    unsigned.pop("snapshot_digest")
    encoded = json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    expected = "sha256:" + hashlib.sha256(encoded).hexdigest()
    require(digest == expected, "SNAPSHOT_DIGEST_MISMATCH")

    return {
        "owners": len(owners),
        "requirements": len(requirements),
        "contradictions": len(contradictions),
        "attempts": len(attempts),
        "stronger_lanes": len(lanes),
        "profile_verdict": closure["profile_verdict"],
        "full_architecture_verdict": closure["full_architecture_verdict"],
    }


def main() -> int:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    result = validate(snapshot)
    print("PASS", json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ProfileShadowError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
