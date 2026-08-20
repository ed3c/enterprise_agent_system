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
    count = 0

    def canary_case(label, mutate, expected, *, rehash_after=False):
        nonlocal count
        value = copy.deepcopy(base_canary)
        mutate(value)
        if rehash_after:
            rehash(value)
        refuse(label, lambda: validate_canary(value), expected)
        count += 1

    canary_case("false execution", lambda v: v.__setitem__("state", "EXECUTED"), "CANARY_FALSE_EXECUTION")
    canary_case("false receipt", lambda v: v.__setitem__("execution_receipt", {"digest": "sha256:" + "a" * 64}), "CANARY_FALSE_RECEIPT")
    canary_case("digest mismatch", lambda v: v["contract"]["constraints"].__setitem__("public_only", False), "CANARY_DIGEST_MISMATCH")
    canary_case("external effects", lambda v: v["contract"]["constraints"].__setitem__("external_effects", True), "CANARY_AUTHORITY_WIDENING:external_effects", rehash_after=True)
    canary_case("human operation", lambda v: v["contract"]["constraints"].__setitem__("human_operation", True), "CANARY_AUTHORITY_WIDENING:human_operation", rehash_after=True)
    canary_case("provider enrollment", lambda v: v["contract"]["constraints"].__setitem__("provider_enrollment", True), "CANARY_AUTHORITY_WIDENING:provider_enrollment", rehash_after=True)
    canary_case("generic X drift", lambda v: v["contract"]["generic_x"].__setitem__("commit", "1" * 40), "CANARY_GENERIC_X_DRIFT", rehash_after=True)
    canary_case("profile E drift", lambda v: v["contract"]["profile_shadow"].__setitem__("shadow_review", 1), "CANARY_PROFILE_E_DRIFT", rehash_after=True)
    canary_case("EAS-A commit drift", lambda v: v["contract"]["advisory_process_dependency"].__setitem__("commit", "2" * 40), "CANARY_EAS_A_DRIFT", rehash_after=True)
    canary_case("EAS-A authority widening", lambda v: v["contract"]["advisory_process_dependency"].__setitem__("authority", "CANONICAL"), "CANARY_EAS_A_DRIFT", rehash_after=True)
    canary_case("owner substitution", lambda v: v["contract"]["steps"][1].__setitem__("repository", "ed3c/agent-shield-monorepo"), "CANARY_SUBJECT:A2R", rehash_after=True)
    canary_case("canary denominator drop", lambda v: v["contract"]["steps"].pop(), "CANARY_STEP_DENOMINATOR", rehash_after=True)

    def receipts_case(label, mutate, expected):
        nonlocal count
        value = copy.deepcopy(base_receipts)
        mutate(value)
        refuse(label, lambda: validate_receipts(value, base_canary), expected)
        count += 1

    receipts_case("multi parent drift", lambda v: v["multi_parent_input"].__setitem__("commit", "3" * 40), "MULTI_PARENT_SUBJECT")
    receipts_case("parent order drift", lambda v: v["multi_parent_input"]["parents"].reverse(), "MULTI_PARENT_DRIFT")
    receipts_case("EAS-A verify drift", lambda v: v["process_dependencies"]["EAS-A"].__setitem__("verification_run", 1), "RECEIPT_EAS_A_DRIFT")
    receipts_case("EAS-A Shadow drift", lambda v: v["process_dependencies"]["EAS-A"].__setitem__("shadow_review", 1), "RECEIPT_EAS_A_DRIFT")
    receipts_case("EAS-A ceiling widening", lambda v: v["process_dependencies"]["EAS-A"].__setitem__("evidence_ceiling", "GOOGLE_LIVE"), "RECEIPT_EAS_A_DRIFT")
    receipts_case("EAS-A false Git parent", lambda v: v["process_dependencies"]["EAS-A"].__setitem__("git_relation", "TRUE_GIT_PARENT"), "RECEIPT_EAS_A_DRIFT")
    receipts_case("owner denominator drop", lambda v: v["owners"].pop(), "RECEIPT_OWNER_DENOMINATOR")
    receipts_case("old Profile-X authority restored", lambda v: v["residue"]["superseded_subjects"][0].__setitem__("authority", "ACTIVE"), "OLD_PROFILE_X_AUTHORITY")
    receipts_case("Profile-D falsely current", lambda v: v["downstream"]["profile_d"].__setitem__("state", "CURRENT"), "PROFILE_D_FALSE_CURRENT")
    receipts_case("P7 execution authority restored", lambda v: v["downstream"]["local_handoff"].__setitem__("state", "READY_FOR_EXECUTION"), "P7_FALSE_AUTHORITY")
    receipts_case("P7 false execution", lambda v: v["downstream"]["local_handoff"].__setitem__("queue_execution", "PASS"), "P7_FALSE_EXECUTION")

    def closure_case(label, mutate, expected):
        nonlocal count
        value = copy.deepcopy(base_closure)
        mutate(value)
        refuse(label, lambda: validate_closure(value, base_canary), expected)
        count += 1

    closure_case("source proposal promotion", lambda v: v["source_subject"].__setitem__("class", "CURRENT_FACT"), "CLOSURE_SOURCE_PROMOTION")
    closure_case("EAS-A authority widening closure", lambda v: v["process_dependencies"]["EAS-A"].__setitem__("authority", "CANONICAL"), "CLOSURE_EAS_A_DRIFT")
    closure_case("requirement denominator drop", lambda v: v["requirements"].pop(), "REQUIREMENT_DENOMINATOR")
    closure_case("canonical owner substitution", lambda v: v["requirements"][0].__setitem__("canonical_owner_repository", "ed3c/runtime-env"), "OWNER_SUBSTITUTION:REQ-PDF-INCEPTION-STATE-001")
    closure_case("required lane rewrite", lambda v: v["requirements"][0].__setitem__("required_evidence_lane", "CLOUD_DETERMINISTIC"), "REQUIRED_LANE_DRIFT:REQ-PDF-INCEPTION-STATE-001")
    closure_case("false required lane satisfaction", lambda v: v["requirements"][0].__setitem__("required_lane_satisfied", True), "REQUIRED_LANE_SATISFIED_COUNT")
    closure_case("false closure credit", lambda v: v["requirements"][0].__setitem__("closure_credit", 1), "FALSE_CLOSURE_CREDIT:REQ-PDF-INCEPTION-STATE-001")
    closure_case("contradiction denominator drop", lambda v: v["contradictions"].pop(), "CONTRADICTION_DENOMINATOR")
    closure_case("contradiction false resolution", lambda v: v["contradictions"][0].__setitem__("state", "RESOLVED"), "CONTRADICTION_FALSE_RESOLUTION:UNK-INCEPTION-001")
    closure_case("stronger lane promotion", lambda v: v["stronger_lanes"][0].__setitem__("state", "PASS"), "STRONGER_LANE_FALSE_CREDIT")
    closure_case("stronger lane denominator drop", lambda v: v["stronger_lanes"].pop(), "STRONGER_LANE_DENOMINATOR")
    closure_case("Human state laundering", lambda v: v["closure_summary"].__setitem__("highest_state", "HUMAN_ADMITTED"), "CLOSURE_SUMMARY_PROMOTION")
    closure_case("full architecture laundering", lambda v: v["closure_summary"].__setitem__("full_architecture", "PASS"), "CLOSURE_SUMMARY_PROMOTION")
    closure_case("Local Handoff laundering", lambda v: v["closure_summary"].__setitem__("local_handoff", "EXECUTED"), "CLOSURE_SUMMARY_PROMOTION")
    closure_case("closure parent order drift", lambda v: v["multi_parent_input"]["parents"].reverse(), "CLOSURE_MULTI_PARENT_DRIFT")

    if count != 38:
        raise AssertionError(f"mutation denominator drift: {count}")
    print(f"PASS profile convergence semantic mutations {count}/{count}")


if __name__ == "__main__":
    main()
