#!/usr/bin/env python3
"""Ordered semantic refusal controls for the Inception profile canary.

The main convergence selftest already proves that a changed canary contract cannot
silently retain the old content digest. This companion control recomputes the digest
after mutation so the validator must reach the intended authority-widening refusal.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROFILE = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from verify_profile_convergence import (  # noqa: E402
    ProfileConvergenceError,
    canary_contract_digest,
    validate_canary,
)

CANARY = PROFILE / "plans" / "vertical-canary.json"


def load_canary() -> dict:
    return json.loads(CANARY.read_text(encoding="utf-8"))


def expect_refusal(value: dict, expected: str) -> None:
    try:
        validate_canary(value)
    except ProfileConvergenceError as exc:
        if expected not in str(exc):
            raise AssertionError(f"wrong refusal: {exc}") from exc
        return
    raise AssertionError(f"mutation was not refused: expected {expected}")


def main() -> int:
    original = load_canary()
    validate_canary(original)

    digest_mutation = copy.deepcopy(original)
    digest_mutation["contract"]["constraints"]["external_effects"] = True
    expect_refusal(digest_mutation, "CANARY_DIGEST_MISMATCH")

    authority_mutation = copy.deepcopy(original)
    authority_mutation["contract"]["constraints"]["external_effects"] = True
    authority_mutation["contract_digest"] = canary_contract_digest(authority_mutation)
    expect_refusal(authority_mutation, "CANARY_AUTHORITY_WIDENING:external_effects")

    provider_mutation = copy.deepcopy(original)
    provider_mutation["contract"]["constraints"]["provider_enrollment"] = True
    provider_mutation["contract_digest"] = canary_contract_digest(provider_mutation)
    expect_refusal(provider_mutation, "CANARY_AUTHORITY_WIDENING:provider_enrollment")

    human_mutation = copy.deepcopy(original)
    human_mutation["contract"]["constraints"]["human_operation"] = True
    human_mutation["contract_digest"] = canary_contract_digest(human_mutation)
    expect_refusal(human_mutation, "CANARY_AUTHORITY_WIDENING:human_operation")

    print("PASS inception-x ordered controls: digest + external-effect + provider + Human widening refused")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
