from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from enterprise_agent_system.shadow import (  # noqa: E402
    ShadowContractError,
    evaluate_shadow_snapshot,
    validate_shadow_snapshot,
)

SUBJECT = {
    "repository": "ed3c/enterprise_agent_system",
    "commit": "3a0e182f49da1fad624a14b624224dcbe866f402",
    "tree": "2b9c374f9cbe58717c0bab313764f488634ca601",
}
DEFAULT_ISSUE = "https://github.com/ed3c/enterprise_agent_system/issues/11"


def sign(snapshot: dict) -> dict:
    value = copy.deepcopy(snapshot)
    value.pop("snapshot_digest", None)
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    value["snapshot_digest"] = "sha256:" + hashlib.sha256(raw).hexdigest()
    return value


def make_snapshot() -> dict:
    return sign(
        {
            "schema_version": "enterprise-agent-system/shadow-snapshot/v1",
            "snapshot_id": "SHADOW-EAS-E-TEST",
            "subject": dict(SUBJECT),
            "source_kind": "SOURCE_PROPOSAL",
            "source_claims_current_fact": False,
            "frozen_objective": [
                "durable typed local-cloud offload",
                "reconnect reconciliation",
                "API-first bounded browser fallback",
                "authority-safe shared knowledge projections",
            ],
            "candidate_state": "DETERMINISTIC_CANDIDATE",
            "human_decision": None,
            "shadow": {
                "read_only": True,
                "separate_evaluation_path": True,
                "may_commit": [],
            },
            "projections": [
                {"provider": "GITHUB", "authority": "ADVISORY_ONLY", "commits": []},
                {"provider": "GOOGLE_DOC", "authority": "ADVISORY_ONLY", "commits": []},
                {"provider": "GOOGLE_SHEET", "authority": "ADVISORY_ONLY", "commits": []},
            ],
            "evidence": [
                {
                    "lane": "CONTROL_PLANE",
                    "required_lane": "CONTROL_PLANE",
                    "state": "PASS",
                    "closure_credit": 1,
                    "subject": dict(SUBJECT),
                    "owner_issue": "https://github.com/ed3c/enterprise_agent_system/issues/9",
                },
                {
                    "lane": "TRANSPORT",
                    "required_lane": "TRANSPORT",
                    "state": "NOT_IMPLEMENTED",
                    "closure_credit": 0,
                    "subject": None,
                    "owner_issue": "https://github.com/ed3c/runtime-env/issues/58",
                },
                {
                    "lane": "USER_OUTCOME",
                    "required_lane": "USER_OUTCOME",
                    "state": "NOT_EXERCISED",
                    "closure_credit": 0,
                    "subject": None,
                    "owner_issue": "https://github.com/ed3c/bettor-arena/issues/186",
                },
            ],
            "declared_findings": [],
            "attempts": [
                {"id": "C-local-gate", "state": "PASS"},
                {"id": "K-local-gate", "state": "PASS"},
                {"id": "github-actions", "state": "NOT_EXERCISED"},
            ],
            "attempt_denominator": 3,
            "cleanup": {"state": "NOT_EXERCISED", "residue": "no physical runtime started"},
            "claims_not_proven": [
                "runtime wire compatibility",
                "physical reconnect",
                "provider isolation",
                "useful user result",
                "Human admission",
                "release readiness",
            ],
        }
    )


class ShadowControlTests(unittest.TestCase):
    def test_honest_deterministic_candidate_is_admitted_for_review_only(self) -> None:
        snapshot = make_snapshot()
        validate_shadow_snapshot(snapshot)
        verdict = evaluate_shadow_snapshot(
            snapshot, expected_subject=SUBJECT, default_owner_issue=DEFAULT_ISSUE
        )
        self.assertEqual(verdict.state, "ADMIT_FOR_REVIEW")
        self.assertEqual(verdict.generated_findings, ())

    def test_declared_open_critical_finding_blocks_closure(self) -> None:
        snapshot = make_snapshot()
        snapshot["declared_findings"] = [
            {
                "id": "SHADOW-RUNTIME-ABSENT",
                "severity": "CRITICAL",
                "state": "OPEN",
                "owner_issue": "https://github.com/ed3c/runtime-env/issues/61",
            }
        ]
        snapshot = sign(snapshot)
        verdict = evaluate_shadow_snapshot(
            snapshot, expected_subject=SUBJECT, default_owner_issue=DEFAULT_ISSUE
        )
        self.assertEqual(verdict.state, "BLOCKED_FOR_CLOSURE")
        self.assertEqual(verdict.open_declared_findings, ("SHADOW-RUNTIME-ABSENT",))

    def test_source_proposal_cannot_self_promote_to_fact(self) -> None:
        snapshot = make_snapshot()
        snapshot["source_claims_current_fact"] = True
        verdict = evaluate_shadow_snapshot(
            sign(snapshot), expected_subject=SUBJECT, default_owner_issue=DEFAULT_ISSUE
        )
        self.assertIn("SHADOW-SOURCE-PROMOTION", [x.id for x in verdict.generated_findings])

    def test_stale_subject_blocks(self) -> None:
        snapshot = make_snapshot()
        expected = dict(SUBJECT)
        expected["commit"] = "0" * 40
        verdict = evaluate_shadow_snapshot(
            snapshot, expected_subject=expected, default_owner_issue=DEFAULT_ISSUE
        )
        self.assertIn("SHADOW-STALE-SUBJECT", [x.id for x in verdict.generated_findings])

    def test_lane_substitution_is_visible(self) -> None:
        snapshot = make_snapshot()
        snapshot["evidence"][1]["required_lane"] = "TASK"
        verdict = evaluate_shadow_snapshot(
            sign(snapshot), expected_subject=SUBJECT, default_owner_issue=DEFAULT_ISSUE
        )
        self.assertIn(
            "SHADOW-LANE-SUBSTITUTION-TRANSPORT",
            [x.id for x in verdict.generated_findings],
        )

    def test_not_exercised_cannot_receive_credit(self) -> None:
        snapshot = make_snapshot()
        snapshot["evidence"][2]["closure_credit"] = 1
        verdict = evaluate_shadow_snapshot(
            sign(snapshot), expected_subject=SUBJECT, default_owner_issue=DEFAULT_ISSUE
        )
        self.assertIn(
            "SHADOW-FALSE-CREDIT-USER_OUTCOME",
            [x.id for x in verdict.generated_findings],
        )

    def test_pass_requires_exact_subject_or_digest(self) -> None:
        snapshot = make_snapshot()
        snapshot["evidence"][1].update(state="PASS", closure_credit=1, subject=None)
        verdict = evaluate_shadow_snapshot(
            sign(snapshot), expected_subject=SUBJECT, default_owner_issue=DEFAULT_ISSUE
        )
        self.assertIn(
            "SHADOW-PASS-WITHOUT-SUBJECT-TRANSPORT",
            [x.id for x in verdict.generated_findings],
        )

    def test_projection_cannot_become_canonical_state_writer(self) -> None:
        snapshot = make_snapshot()
        snapshot["projections"][2]["commits"] = ["TASK_STATE"]
        verdict = evaluate_shadow_snapshot(
            sign(snapshot), expected_subject=SUBJECT, default_owner_issue=DEFAULT_ISSUE
        )
        self.assertIn(
            "SHADOW-PROJECTION-AUTHORITY-GOOGLE_SHEET",
            [x.id for x in verdict.generated_findings],
        )

        snapshot = make_snapshot()
        snapshot["projections"][2]["authority"] = "CANONICAL"
        with self.assertRaisesRegex(ShadowContractError, "SHARED_PROJECTION_BECAME_AUTHORITY"):
            validate_shadow_snapshot(sign(snapshot))

    def test_shadow_cannot_write_state(self) -> None:
        snapshot = make_snapshot()
        snapshot["shadow"]["may_commit"] = ["TASK_STATE"]
        with self.assertRaisesRegex(ShadowContractError, "SHADOW_SECOND_STATE_WRITER"):
            validate_shadow_snapshot(sign(snapshot))

    def test_failed_attempt_cannot_disappear_from_denominator(self) -> None:
        snapshot = make_snapshot()
        snapshot["attempt_denominator"] = 2
        with self.assertRaisesRegex(ShadowContractError, "ATTEMPT_DENOMINATOR_DROPPED"):
            validate_shadow_snapshot(sign(snapshot))

    def test_terminal_state_requires_human_decision_and_cleanup(self) -> None:
        snapshot = make_snapshot()
        snapshot["candidate_state"] = "RELEASED"
        verdict = evaluate_shadow_snapshot(
            sign(snapshot), expected_subject=SUBJECT, default_owner_issue=DEFAULT_ISSUE
        )
        ids = [x.id for x in verdict.generated_findings]
        self.assertIn("SHADOW-HUMAN-PROMOTION", ids)
        self.assertIn("SHADOW-CLEANUP-NOT-PASS", ids)

    def test_critical_declared_finding_requires_owner_issue(self) -> None:
        snapshot = make_snapshot()
        snapshot["declared_findings"] = [
            {"id": "SHADOW-OWNER", "severity": "CRITICAL", "state": "OPEN", "owner_issue": "missing"}
        ]
        with self.assertRaisesRegex(ShadowContractError, "CRITICAL_FINDING_WITHOUT_OWNER"):
            evaluate_shadow_snapshot(
                sign(snapshot), expected_subject=SUBJECT, default_owner_issue=DEFAULT_ISSUE
            )

    def test_silent_snapshot_edit_breaks_digest(self) -> None:
        snapshot = make_snapshot()
        snapshot["candidate_state"] = "COMPLETE"
        with self.assertRaisesRegex(ShadowContractError, "SNAPSHOT_DIGEST_MISMATCH"):
            validate_shadow_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
