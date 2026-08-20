from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from enterprise_agent_system.shadow import (  # noqa: E402
    evaluate_shadow_snapshot,
    validate_shadow_snapshot,
)

EXPECTED_SUBJECT = {
    "repository": "ed3c/enterprise_agent_system",
    "commit": "b1362f48b6edc0b4cd6d301da2a5d0e94d970f8c",
    "tree": "19353937e8d642a0bd731e20b3f61ffa3af2b913",
}
DEFAULT_OWNER_ISSUE = (
    "https://github.com/ed3c/enterprise_agent_system/issues/11"
)


def load_snapshot(name: str) -> dict:
    path = ROOT / "evidence" / "shadow" / name
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    preflight = load_snapshot("control-plane-preflight-review.json")
    closure = load_snapshot("dual-agent-closure-review.json")

    for snapshot in (preflight, closure):
        validate_shadow_snapshot(snapshot)

    preflight_verdict = evaluate_shadow_snapshot(
        preflight,
        expected_subject=EXPECTED_SUBJECT,
        default_owner_issue=DEFAULT_OWNER_ISSUE,
    )
    closure_verdict = evaluate_shadow_snapshot(
        closure,
        expected_subject=EXPECTED_SUBJECT,
        default_owner_issue=DEFAULT_OWNER_ISSUE,
    )

    assert preflight_verdict.state == "ADMIT_FOR_REVIEW", (
        preflight_verdict.as_dict()
    )
    assert not preflight_verdict.generated_findings, (
        preflight_verdict.as_dict()
    )

    assert closure_verdict.state == "BLOCKED_FOR_CLOSURE", (
        closure_verdict.as_dict()
    )
    assert not closure_verdict.generated_findings, closure_verdict.as_dict()
    assert "SHADOW-001-RUNTIME-CONTRACT" in (
        closure_verdict.open_declared_findings
    )
    assert "SHADOW-013-PROFILE-CONTRACTS" in (
        closure_verdict.open_declared_findings
    )

    print(
        "PASS preflight=ADMIT_FOR_REVIEW "
        "closure=BLOCKED_FOR_CLOSURE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
