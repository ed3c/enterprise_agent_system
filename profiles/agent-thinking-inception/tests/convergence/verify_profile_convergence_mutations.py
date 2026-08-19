#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from verify_profile_convergence import (  # noqa: E402
    ProfileConvergenceError,
    load,
    validate_canary,
    validate_closure,
    validate_receipts,
)

CLOSURE = ROOT / "plans" / "closure-record.json"
CANARY = ROOT / "plans" / "vertical-canary.json"
RECEIPTS = ROOT / "evidence" / "convergence" / "receipt-index.json"


def rehash(canary: dict) -> None:
    payload = json.dumps(canary["contract"], sort_keys=True, separators=(",", ":")).encode()
    canary["contract_digest"] = "sha256:" + hashlib.sha256(payload).hexdigest()


def refuse(label: str, operation, expected: str) -> None:
    try:
        operation()
    except ProfileConvergenceError as exc:
        if expected not in str(exc):
            raise AssertionError(f"{label}: wrong refusal {exc}") from exc
        return
    raise AssertionError(f"{label}: mutation was not refused")


def main() -> None:
    base_closure = load(CLOSURE)
    base_canary = load(CANARY)
    base_receipts = load(RECEIPTS)

    def canary_case(label, mutate, expected, *, rehash_after=False):
        value = copy.deepcopy(base_canary)
        mutate(value)
        if rehash_after:
            rehash(value)
        refuse(label, lambda: validate_canary(value), expected)

    canary_case("false execution", lambda v: v.__setitem__("state", "EXECUTED"), "CANARY_FALSE_EXECUTION")
    canary_case("false receipt", lambda v: v.__setitem__("execution_receipt", {"digest": "sha256:" + "a" * 64}), "CANARY_FALSE_RECEIPT")
    canary_case("external effects", lambda v: v["contract"]["constraints"].__setitem__("external_effects", True), "CANARY_AUTHORITY_WIDENING:external_effects", rehash_after=True)
    canary_case("human operation", lambda v: v["contract"]["constraints"].__setitem__("human_operation", True), "CANARY_AUTHORITY_WIDENING:human_operation", rehash_after=True)
    canary_case("provider enrollment", lambda v: v["contract"]["constraints"].__setitem__("provider_enrollment", True), "CANARY_AUTHORITY_WIDENING:provider_enrollment", rehash_after=True)
    canary_case("generic X review drift", lambda v: v["contract"]["generic_x"].__setitem__("shadow_review", 1), "CANARY_GENERIC_X_DRIFT", rehash_after=True)
    canary_case("profile Shadow review drift", lambda v: v["contract"]["profile_shadow"].__setitem__("shadow_review", 1), "CANARY_PROFILE_E_DRIFT", rehash_after=True)
    canary_case("owner substitution", lambda v: v["contract"]["steps"][1].__setitem__("repository", "ed3c/agent-shield-monorepo"), "CANARY_SUBJECT:A2R", rehash_after=True)
    canary_case("canary denominator drop", lambda v: v["contract"]["steps"].pop(), "CANARY_STEP_DENOMINATOR", rehash_after=True)

    receipts = copy.deepcopy(base_receipts)
    receipts["local_handoff_contract"]["queue_execution"] = "PASS"
    refuse("handoff false execution", lambda: validate_receipts(receipts, base_canary), "HANDOFF_FALSE_EXECUTION")

    receipts = copy.deepcopy(base_receipts)
    receipts["residue"]["authority"] = "PASS"
    refuse("stale branch authority", lambda: validate_receipts(receipts, base_canary), "RESIDUE_AUTHORITY")

    receipts = copy.deepcopy(base_receipts)
    receipts["owners"].pop()
    refuse("owner denominator drop", lambda: validate_receipts(receipts, base_canary), "RECEIPT_OWNER_DENOMINATOR")

    closure = copy.deepcopy(base_closure)
    closure["source_subject"]["class"] = "CURRENT_FACT"
    refuse("source proposal promotion", lambda: validate_closure(closure, base_canary), "CLOSURE_SOURCE_PROMOTION")

    closure = copy.deepcopy(base_closure)
    closure["requirements"].pop()
    refuse("requirement denominator drop", lambda: validate_closure(closure, base_canary), "REQUIREMENT_DENOMINATOR")

    closure = copy.deepcopy(base_closure)
    closure["requirements"][0]["canonical_owner_repository"] = "ed3c/runtime-env"
    refuse("canonical owner substitution", lambda: validate_closure(closure, base_canary), "OWNER_SUBSTITUTION:REQ-PDF-INCEPTION-STATE-001")

    closure = copy.deepcopy(base_closure)
    closure["requirements"][0]["required_evidence_lane"] = "CLOUD_DETERMINISTIC"
    refuse("required lane rewrite", lambda: validate_closure(closure, base_canary), "REQUIRED_LANE_DRIFT:REQ-PDF-INCEPTION-STATE-001")

    closure = copy.deepcopy(base_closure)
    closure["requirements"][0]["required_lane_satisfied"] = True
    refuse("false required lane satisfaction", lambda: validate_closure(closure, base_canary), "REQUIRED_LANE_SATISFIED_COUNT")

    closure = copy.deepcopy(base_closure)
    closure["requirements"][0]["closure_credit"] = 1
    refuse("false closure credit", lambda: validate_closure(closure, base_canary), "FALSE_CLOSURE_CREDIT:REQ-PDF-INCEPTION-STATE-001")

    closure = copy.deepcopy(base_closure)
    closure["contradictions"].pop()
    refuse("contradiction denominator drop", lambda: validate_closure(closure, base_canary), "CONTRADICTION_DENOMINATOR")

    closure = copy.deepcopy(base_closure)
    closure["contradictions"][0]["state"] = "RESOLVED"
    refuse("contradiction false resolution", lambda: validate_closure(closure, base_canary), "CONTRADICTION_FALSE_RESOLUTION:UNK-INCEPTION-001")

    closure = copy.deepcopy(base_closure)
    closure["stronger_lanes"][0]["state"] = "PASS"
    refuse("stronger lane promotion", lambda: validate_closure(closure, base_canary), "STRONGER_LANE_FALSE_CREDIT")

    closure = copy.deepcopy(base_closure)
    closure["closure_summary"]["highest_state"] = "HUMAN_ADMITTED"
    refuse("Human state laundering", lambda: validate_closure(closure, base_canary), "CLOSURE_SUMMARY_PROMOTION")

    closure = copy.deepcopy(base_closure)
    closure["closure_summary"]["full_architecture"] = "PASS"
    refuse("full architecture laundering", lambda: validate_closure(closure, base_canary), "CLOSURE_SUMMARY_PROMOTION")

    closure = copy.deepcopy(base_closure)
    closure["multi_parent_input"]["parents"].reverse()
    refuse("parent order drift", lambda: validate_closure(closure, base_canary), "CLOSURE_MULTI_PARENT_DRIFT")

    print("PASS profile convergence semantic mutations 24/24")


if __name__ == "__main__":
    main()
