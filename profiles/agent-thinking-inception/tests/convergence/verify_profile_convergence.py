#!/usr/bin/env python3
"""Fail-closed verifier for INCEPTION-X v3 profile convergence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REQ = ROOT / "requirements"
CLOSURE = ROOT / "plans" / "closure-record.json"
CANARY = ROOT / "plans" / "vertical-canary.json"
RECEIPTS = ROOT / "evidence" / "convergence" / "receipt-index.json"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
EXPECTED_PARENT_COMMIT = "718a17820779809f070ca324ce62695114b9d3dc"
EXPECTED_GENERIC_X = {
    "repository": "ed3c/enterprise_agent_system",
    "pull_request": 31,
    "commit": "8b1bfa38c103e1c064b8ef0aafecfc8f2a2642dc",
    "tree": "9c8fb0e8e25f357fdb695a94c4ab74fc3dcd4631",
    "shadow_review": 4973896050,
}
EXPECTED_PROFILE_E = {
    "repository": "ed3c/enterprise_agent_system",
    "pull_request": 32,
    "commit": "9f25b94ca891faf0d926b0fc22b67be88925aa81",
    "tree": "1452d1b9931c70ef70ed3b7dec78cedc51d6db35",
    "shadow_review": 4973593318,
}
EXPECTED_OWNERS = {
    "A1": ("ed3c/bettor-arena", "21ac4fdcd6ce4c5acea920dc4e59a53d13ecd328", "31ea6bec01899a4c9e4f994998ea6041116db49d", (32259216877,)),
    "A2R": ("ed3c/runtime-env", "2ff4efe7bee3d12fb3063fed93631f8d323cd64a", "273c6873e7075d90a7f11275c5d39e746dd075dc", (32249588945, 32249588946)),
    "A2": ("ed3c/agent-shield-monorepo", "8ec782b78ec9e13f78f2faf14e6ffa722c1b78f2", "51adf9791485d597849c026a3828ded0088b3805", (32262032532, 32262032583, 32262032553)),
    "A3": ("ed3c/truth-verify-loop", "5ea4dd42d2ee5bbd22537f5426cd276f10222980", "fc6486b9ab6a48752e32a536a847c6e5635f8547", (32260293092, 32260291970)),
    "A4": ("ed3c/enterprise_agent_system", "bf976c7c33e315d1743733a79c15521e645ff6dc", "c09bef2457ad507433f253c8a5fd211147fae247", (32261864341,)),
    "A5": ("ed3c/bettor-arena", "81f02f4148273ffe5f5571c8605e1ee0afc59866", "f9612314e47ced69796db00703dd5d34ab592e36", (32260835956,)),
    "A6": ("ed3c/bettor-arena", "c2613432736c65756ed13d871feb2df486c69118", "53680d47048f88b9402c6320355121b7ec2f7244", (32262080676,)),
}
EXPECTED_STRONGER = {
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
NO_CREDIT = {"NOT_EXERCISED", "NOT_PERFORMED", "NOT_VERIFIED", "UNBOUND", "HUMAN_ADMIT_REQUIRED", "BLOCKED"}


class ProfileConvergenceError(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ProfileConvergenceError(reason)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"NOT_OBJECT:{path}")
    return value


def exact_subject(value: Any, reason: str) -> None:
    require(isinstance(value, dict), f"{reason}:NOT_OBJECT")
    require(set(value) == {"repository", "commit", "tree"}, f"{reason}:FIELDS")
    require(isinstance(value["repository"], str) and "/" in value["repository"], f"{reason}:REPOSITORY")
    require(HEX40.fullmatch(value["commit"]) is not None, f"{reason}:COMMIT")
    require(HEX40.fullmatch(value["tree"]) is not None, f"{reason}:TREE")


def source_denominator() -> tuple[dict[str, dict[str, Any]], set[str]]:
    requirements: dict[str, dict[str, Any]] = {}
    for name in ("control-requirements.json", "assurance-requirements.json", "delivery-requirements.json"):
        shard = load(REQ / name)
        require(shard.get("schema_version") == "enterprise-agent-system/inception-requirement-shard/v1", f"SOURCE_SCHEMA:{name}")
        for item in shard.get("requirements", []):
            rid = item.get("requirement_id")
            require(isinstance(rid, str) and rid.startswith("REQ-PDF-INCEPTION-"), f"SOURCE_REQUIREMENT:{name}")
            require(rid not in requirements, f"SOURCE_REQUIREMENT_DUPLICATE:{rid}")
            requirements[rid] = item
    contradictions = load(REQ / "contradictions.json")
    ids = {item["id"] for item in contradictions.get("items", [])}
    require(len(requirements) == 15, f"SOURCE_REQUIREMENT_DENOMINATOR:{len(requirements)}")
    require(ids == {f"UNK-INCEPTION-{i:03d}" for i in range(1, 15)}, "SOURCE_CONTRADICTION_DENOMINATOR")
    return requirements, ids


def canonical_canary_digest(canary: dict[str, Any]) -> str:
    payload = json.dumps(canary["contract"], sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def validate_canary(canary: dict[str, Any]) -> None:
    require(canary.get("schema_version") == "enterprise-agent-system/inception-profile-vertical-canary/v1", "CANARY_SCHEMA")
    require(canary.get("profile_id") == "PROFILE-AGENT-THINKING-INCEPTION-001", "CANARY_PROFILE")
    require(canary.get("canary_id") == "INCEPTION-X-PUBLIC-NO-EFFECT-001", "CANARY_ID")
    require(canary.get("state") == "PLAN_ONLY", "CANARY_FALSE_EXECUTION")
    require(canary.get("execution_receipt") is None, "CANARY_FALSE_RECEIPT")
    require(DIGEST.fullmatch(str(canary.get("contract_digest", ""))) is not None, "CANARY_DIGEST")
    require(canonical_canary_digest(canary) == canary["contract_digest"], "CANARY_DIGEST_MISMATCH")
    contract = canary["contract"]
    require(contract["generic_x"] == EXPECTED_GENERIC_X, "CANARY_GENERIC_X_DRIFT")
    require(contract["profile_shadow"] == EXPECTED_PROFILE_E, "CANARY_PROFILE_E_DRIFT")
    constraints = contract["constraints"]
    require(constraints.get("public_only") is True and constraints.get("reversible") is True, "CANARY_PUBLIC_REVERSIBLE")
    for key in ("private_data", "external_effects", "human_operation", "provider_enrollment", "production_credentials"):
        require(constraints.get(key) is False, f"CANARY_AUTHORITY_WIDENING:{key}")
    steps = contract["steps"]
    require(len(steps) == 7, "CANARY_STEP_DENOMINATOR")
    require([step["atom"] for step in steps] == list(EXPECTED_OWNERS), "CANARY_STEP_ORDER")
    identities: set[tuple[str, str, str]] = set()
    for index, step in enumerate(steps, 1):
        require(step["order"] == index, f"CANARY_ORDER:{index}")
        expected = EXPECTED_OWNERS[step["atom"]]
        require((step["repository"], step["commit"], step["tree"], tuple(step["hosted_runs"])) == expected, f"CANARY_SUBJECT:{step['atom']}")
        require(step["mode"] == "CONSTITUENT_RECEIPT_ONLY", f"CANARY_MODE:{step['atom']}")
        identity = (step["repository"], step["commit"], step["tree"])
        require(identity not in identities, f"CANARY_DUPLICATE_SUBJECT:{step['atom']}")
        identities.add(identity)
    require(canary.get("claims_not_proven"), "CANARY_CLAIMS_NOT_PROVEN")


def validate_receipts(receipts: dict[str, Any], canary: dict[str, Any]) -> None:
    require(receipts.get("schema_version") == "enterprise-agent-system/inception-profile-convergence-receipts/v3", "RECEIPT_SCHEMA")
    require(receipts.get("state") == "P5_PROFILE_CONVERGENCE_CANDIDATE", "RECEIPT_STATE")
    multi = receipts["multi_parent_input"]
    require(multi["commit"] == EXPECTED_PARENT_COMMIT, "MULTI_PARENT_COMMIT")
    parents = multi["parents"]
    require(len(parents) == 2 and {p["atom"] for p in parents} == {"EAS-X", "INCEPTION-E"}, "MULTI_PARENT_DENOMINATOR")
    gx = next(p for p in parents if p["atom"] == "EAS-X")
    pe = next(p for p in parents if p["atom"] == "INCEPTION-E")
    for key, value in EXPECTED_GENERIC_X.items():
        require(gx.get(key) == value, f"GENERIC_X_RECEIPT_DRIFT:{key}")
    require(gx["review"] == EXPECTED_GENERIC_X["shadow_review"] and gx["verdict"] == "ADMIT_FOR_PROFILE_X_REBIND", "GENERIC_X_REVIEW")
    for key, value in EXPECTED_PROFILE_E.items():
        require(pe.get(key) == value, f"PROFILE_E_RECEIPT_DRIFT:{key}")
    require(pe["review"] == EXPECTED_PROFILE_E["shadow_review"] and pe["verdict"] == "ADMIT_FOR_PROFILE_CONVERGENCE", "PROFILE_E_REVIEW")

    owners = receipts["owners"]
    require(len(owners) == 7 and [owner["atom"] for owner in owners] == list(EXPECTED_OWNERS), "RECEIPT_OWNER_DENOMINATOR")
    for owner in owners:
        expected = EXPECTED_OWNERS[owner["atom"]]
        require((owner["repository"], owner["commit"], owner["tree"], tuple(owner["hosted_runs"])) == expected, f"RECEIPT_OWNER:{owner['atom']}")

    handoff = receipts["local_handoff_contract"]
    require(handoff["commit"] == "9223107163b27984ed490246b4c0899caeb1bdae", "HANDOFF_COMMIT")
    require(handoff["tree"] == "d462e2a1a69d225bf8161ce01918e5e8bb8d102f", "HANDOFF_TREE")
    require(handoff["state"] == "DETERMINISTIC_QUEUE_CONTRACT_ONLY", "HANDOFF_STATE")
    require(handoff["queue_execution"] == "NOT_PERFORMED", "HANDOFF_FALSE_EXECUTION")
    require(receipts["source"] == {"id": "SRC-PDF-INCEPTION-001", "digest": "sha256:a6f1245ff865cae24838ed8ec4828330be684f3c03b29b9064ade8bfac94d8da", "class": "SOURCE_PROPOSAL", "requirements": 15, "contradictions": 14}, "SOURCE_PROMOTION_OR_DENOMINATOR")
    require(receipts["vertical_canary"] == {"path": "profiles/agent-thinking-inception/plans/vertical-canary.json", "digest": canary["contract_digest"], "state": "PLAN_ONLY", "execution_receipt": None}, "RECEIPT_CANARY")
    require(receipts["closure"]["highest_state"] == "DETERMINISTIC_EVIDENCE_VERIFIED", "RECEIPT_FALSE_CLOSURE")
    require(receipts["closure"]["full_architecture"] == "BLOCKED_FOR_CLOSURE" and receipts["closure"]["closure_credit"] == 0, "RECEIPT_FULL_CLOSURE_PROMOTION")
    residues = receipts["residue"]["superseded_branches"]
    require(len(residues) == 2, "RESIDUE_DENOMINATOR")
    require({x["branch"] for x in residues} == {"agent/inception-x-profile-convergence", "agent/inception-x-profile-convergence-v2"}, "RESIDUE_BRANCHES")
    require(all(x["authority"] == "NONE" for x in residues), "RESIDUE_AUTHORITY")
    v2 = next(x for x in residues if x["branch"].endswith("-v2"))
    require(v2.get("pull_request") == 36 and v2["relationship"] == "SUPERSEDED_BY_EAS_X_PARENT_REBIND", "RESIDUE_V2_TRACE")


def validate_closure(closure: dict[str, Any], canary: dict[str, Any]) -> None:
    source, contradiction_ids = source_denominator()
    require(closure.get("schema_version") == "enterprise-agent-system/inception-profile-closure/v3", "CLOSURE_SCHEMA")
    require(closure.get("profile_id") == "PROFILE-AGENT-THINKING-INCEPTION-001", "CLOSURE_PROFILE")
    require(closure.get("state") == "PROFILE_CLOSURE_CANDIDATE_BLOCKED_STRONGER_LANES", "CLOSURE_STATE")
    require(closure["source_subject"] == {"id": "SRC-PDF-INCEPTION-001", "digest": "sha256:a6f1245ff865cae24838ed8ec4828330be684f3c03b29b9064ade8bfac94d8da", "class": "SOURCE_PROPOSAL"}, "CLOSURE_SOURCE_PROMOTION")
    multi = closure["multi_parent_input"]
    require(multi["commit"] == EXPECTED_PARENT_COMMIT, "CLOSURE_MULTI_PARENT_COMMIT")
    require(multi["parents"] == [EXPECTED_GENERIC_X, EXPECTED_PROFILE_E], "CLOSURE_MULTI_PARENT_DRIFT")

    rows = closure["requirements"]
    require(len(rows) == 15, "REQUIREMENT_DENOMINATOR")
    indexed = {row["requirement_id"]: row for row in rows}
    require(set(indexed) == set(source), "REQUIREMENT_ID_DENOMINATOR")
    require(sum(1 for row in rows if row["required_lane_satisfied"]) == 1, "REQUIRED_LANE_SATISFIED_COUNT")
    for rid, row in indexed.items():
        src = source[rid]
        require(row["canonical_owner_repository"] == src["owner"]["repository"], f"OWNER_SUBSTITUTION:{rid}")
        require(row["owner_issue"] == src["owner"]["issue"], f"OWNER_ISSUE:{rid}")
        require(row["required_evidence_lane"] == src["required_evidence_lane"], f"REQUIRED_LANE_DRIFT:{rid}")
        exact_subject(row["owner_subject"], f"OWNER_SUBJECT:{rid}")
        exact_subject(row["evidence_subject"], f"EVIDENCE_SUBJECT:{rid}")
        require(row["owner_subject"]["repository"] == row["canonical_owner_repository"], f"OWNER_SUBJECT_REPOSITORY:{rid}")
        require(row["closure_credit"] == 0, f"FALSE_CLOSURE_CREDIT:{rid}")
        require(isinstance(row["blockers"], list) and row["blockers"], f"BLOCKER_MISSING:{rid}")
        require(isinstance(row["next_transition"], str) and row["next_transition"], f"NEXT_TRANSITION:{rid}")
    require(indexed["REQ-PDF-INCEPTION-DAG-001"]["required_lane_satisfied"] is True, "DAG_REQUIRED_LANE")
    require(all(not row["required_lane_satisfied"] for rid, row in indexed.items() if rid != "REQ-PDF-INCEPTION-DAG-001"), "FALSE_REQUIRED_LANE_PROMOTION")

    contradictions = closure["contradictions"]
    require(len(contradictions) == 14 and {item["id"] for item in contradictions} == contradiction_ids, "CONTRADICTION_DENOMINATOR")
    for item in contradictions:
        require(item["state"] == "PRESERVED_WITH_PARTIAL_CONTROL", f"CONTRADICTION_FALSE_RESOLUTION:{item['id']}")
        require(item["control_atom"] and item["remaining_blocker"], f"CONTRADICTION_CONTROL:{item['id']}")

    stronger = closure["stronger_lanes"]
    require(len(stronger) == 13 and {x["lane"] for x in stronger} == EXPECTED_STRONGER, "STRONGER_LANE_DENOMINATOR")
    require(all(x["state"] in NO_CREDIT for x in stronger), "STRONGER_LANE_FALSE_CREDIT")
    selected = closure["selected_vertical_canary"]
    require(selected == {"path": "profiles/agent-thinking-inception/plans/vertical-canary.json", "contract_digest": canary["contract_digest"], "state": "PLAN_ONLY", "execution_receipt": None}, "SELECTED_CANARY_DRIFT")
    require(closure["closure_summary"] == {
        "requirements_total": 15,
        "requirements_required_lane_satisfied": 1,
        "requirements_closure_credit": 0,
        "contradictions_total": 14,
        "contradictions_preserved": 14,
        "profile_shadow": "ADMIT_FOR_PROFILE_CONVERGENCE",
        "generic_x": "ADMIT_FOR_PROFILE_X_REBIND",
        "vertical_canary": "PLAN_ONLY",
        "highest_state": "DETERMINISTIC_EVIDENCE_VERIFIED",
        "full_architecture": "BLOCKED_FOR_CLOSURE",
        "profile_release_state": "NOT_ADMITTED"
    }, "CLOSURE_SUMMARY_PROMOTION")
    require(closure.get("next_transition") == "P6_DOCUMENTATION_CONVERGENCE_AND_P7_HANDOFF_COMPILATION", "CLOSURE_NEXT_TRANSITION")
    claims = " ".join(closure.get("claims_not_proven", [])).lower()
    for word in ("physical", "provider", "external", "human", "release", "rollback"):
        require(word in claims, f"CLAIMS_NOT_PROVEN:{word}")


def validate_all() -> dict[str, Any]:
    canary = load(CANARY)
    receipts = load(RECEIPTS)
    closure = load(CLOSURE)
    validate_canary(canary)
    validate_receipts(receipts, canary)
    validate_closure(closure, canary)
    return {"owners": 7, "requirements": 15, "contradictions": 14, "stronger_lanes": 13, "required_lanes_satisfied": 1, "closure_credit": 0, "canary": "PLAN_ONLY", "highest_state": "DETERMINISTIC_EVIDENCE_VERIFIED", "full_architecture": "BLOCKED_FOR_CLOSURE"}


def main() -> int:
    print("PASS", json.dumps(validate_all(), sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ProfileConvergenceError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
