#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from verify_profile_shadow import ProfileShadowError, validate  # noqa: E402

SNAPSHOT = ROOT / "shadow" / "profile-shadow-review.json"


def digest(value: dict) -> None:
    unsigned = dict(value)
    unsigned.pop("snapshot_digest", None)
    encoded = json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    value["snapshot_digest"] = "sha256:" + hashlib.sha256(encoded).hexdigest()


def refuse(label: str, mutate, expected: str) -> None:
    value = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    mutate(value)
    digest(value)
    try:
        validate(value)
    except ProfileShadowError as exc:
        if expected not in str(exc):
            raise AssertionError(f"{label}: wrong refusal {exc}") from exc
        return
    raise AssertionError(f"{label}: mutation was not refused")


def main() -> None:
    refuse("owner loss", lambda v: v["owners"].pop(), "OWNER_DENOMINATOR")
    refuse("duplicate interface", lambda v: v["owners"][1].__setitem__("interface", v["owners"][0]["interface"]), "DUPLICATE_OWNER_INTERFACE")
    refuse("owner substitution", lambda v: v["owners"][1].__setitem__("repository", "ed3c/agent-shield-monorepo"), "OWNER_SUBSTITUTION:A2R")
    refuse("mutable commit", lambda v: v["owners"][0].__setitem__("commit", "main"), "OWNER_A1_COMMIT")
    refuse("source promotion", lambda v: v["source_subject"].__setitem__("claims_current_fact", True), "SOURCE_PROMOTED_TO_CURRENT_FACT")
    refuse("second state writer", lambda v: v["shadow"].__setitem__("may_commit", ["TASK_STATE"]), "SHADOW_AUTHORITY")
    refuse("model judge receipt", lambda v: v["public_denominator_receipt"].__setitem__("kind", "MODEL_JUDGE"), "SHADOW_RECEIPT_KIND")
    refuse("requirement loss", lambda v: v["requirements"].pop(), "REQUIREMENT_DENOMINATOR")
    refuse("contradiction loss", lambda v: v["contradictions"].pop(), "CONTRADICTION_DENOMINATOR")
    refuse("failed attempts erased", lambda v: v.__setitem__("attempts", [x for x in v["attempts"] if x["state"] != "FAIL"]), "ATTEMPT_DENOMINATOR_DROPPED")
    refuse("stronger lane promoted", lambda v: v["stronger_lanes"][0].__setitem__("state", "PASS"), "STRONGER_LANE_PROMOTION")
    refuse("terminal closure promoted", lambda v: v["closure"].__setitem__("highest_state", "HUMAN_ADMITTED"), "FALSE_CLOSURE_PROMOTION")
    refuse("full closure promoted", lambda v: v["closure"].__setitem__("full_architecture_verdict", "PASS"), "FULL_CLOSURE_PROMOTED")
    refuse("parent binding drift", lambda v: v["profile_shadow_base"]["parents"].reverse(), "SHADOW_MULTI_PARENT_BINDING")
    print("PASS profile Shadow semantic mutations 14/14")


if __name__ == "__main__":
    main()
