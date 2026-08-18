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
    "commit": "b1362f48b6edc0b4cd6d301da2a5d0e94d970f8c",
    "tree": "19353937e8d642a0bd731e20b3f61ffa3af2b913",
}
DEFAULT_ISSUE = "https://github.com/ed3c/enterprise_agent_system/issues/11"


def sign(snapshot: dict) -> dict:
    value = copy.deepcopy(snapshot)
    value.pop("snapshot_digest", None)
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    value["snapshot_digest"] = (
        "sha256:" + hashlib.sha256(raw).hexdigest()
    )
    return value


def make_snapshot() -> dict:
    return sign(
        {
            "schema_version": "enterprise-agent-system/shadow-snapshot/v2",
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
                {
                    "provider": "GITHUB",
                    "authority": "ADVISORY_ONLY",
                    "commits": [],
                },
                {
                    "provider": "GOOGLE_DOC",
                    "authority": "ADVISORY_ONLY",
                    "commits": [],
                },
                {
                    "provider": "GOOGLE_SHEET",
                    "authority": "ADVISORY_ONLY",
                    "commits": [],
                },
            ],
            "evidence": [
                {
                    "lane": "CONTROL_PLANE",
                    "required_lane": "CONTROL_PLANE",
                    "state": "PASS",
                    "closure_credit": 1,
                    "subject": dict(SUBJECT),
                    "owner_issue": (
                        "https://github.com/ed3c/"
                        "enterprise_agent_system/issues/9"
                    ),
                },
                {
                    "lane": "TRANSPORT",
                    "required_lane": "TRANSPORT",
                    "state": "NOT_IMPLEMENTED",
                    "closure_credit": 0,
                    "subject": None,
                    "owner_issue": (
                        "https://github.com/ed3c/runtime-env/issues/58"
                    ),
                },
                {
                    "lane": "USER_OUTCOME",
                    "required_lane": "USER_OUTCOME",
                    "state": "NOT_EXERCISED",
                    "closure_credit": 0,
                    "subject": None,
                    "owner_issue": (
                        "https://github.com/ed3c/bettor-arena/issues/186"
                    ),
                },
            ],
            "declared_findings": [],
            "attempts": [
                {
                    "id": "EAS-C-actions",
                    "state": "PASS",
                    "subject": {
                        "repository": "ed3c/enterprise_agent_system",
                        "commit": "ad5c3057f461d559faec52d7345fd5db86051e56",
                        "tree": "51c94cb43ed1e4a3a3ac05e42838532c3ec2e598",
                    },
                },
                {
                    "id": "EAS-K-actions",
                    "state": "PASS",
                    "subject": {
                        "repository": "ed3c/enterprise_agent_system",
                        "commit": "bc9dee35a67cbb42766d9ef4a662ed185cbcba2e",
                        "tree": "19353937e8d642a0bd731e20b3f61ffa3af2b913",
                    },
                },
                {
                    "id": "physical-canary",
                    "state": "NOT_EXERCISED",
                },
            ],
            "attempt_denominator": 3,
            "cleanup": {
                "state": "NOT_EXERCISED",
                "residue": "no physical runtime started",
            },
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
    def test_honest_candidate_is_admitted_for_review_only(self) -> None:
        snapshot = make_snapshot()
        validate_shadow_snapshot(snapshot)
        verdict = evaluate_shadow_snapshot(
            snapshot,
            expected_subject=SUBJECT,
            default_owner_issue=DEFAULT_ISSUE,
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
                "owner_issue": (
                    "https://github.com/ed3c/runtime-env/issues/61"
                ),
            }
        ]
        verdict = evaluate_shadow_snapshot(
            sign(snapshot),
            expected_subject=SUBJECT,
            default_owner_issue=DEFAULT_ISSUE,
        )
        self.assertEqual(verdict.state, "BLOCKED_FOR_CLOSURE")
        self.assertEqual(
            verdict.open_declared_findings,
            ("SHADOW-RUNTIME-ABSENT",),
        )

    def test_source_proposal_cannot_self_promote_to_fact(self) -> None:
        snapshot = make_snapshot()
        snapshot["source_claims_current_fact"] = True
        verdict = evaluate_shadow_snapshot(
            sign(snapshot),
            expected_subject=SUBJECT,
            default_owner_issue=DEFAULT_ISSUE,
        )
        self.assertIn(
            "SHADOW-SOURCE-PROMOTION",
            [item.id for item in verdict.generated_findings],
        )

    def test_repository_commit_or_tree_drift_blocks(self) -> None:
        for field, value in (
            ("repository", "ed3c/other"),
            ("commit", "0" * 40),
            ("tree", "1" * 40),
        ):
            expected = dict(SUBJECT)
            expected[field] = value
            verdict = evaluate_shadow_snapshot(
                make_snapshot(),
                expected_subject=expected,
                default_owner_issue=DEFAULT_ISSUE,
            )
            self.assertIn(
                "SHADOW-STALE-SUBJECT",
                [item.id for item in verdict.generated_findings],
            )

    def test_lane_substitution_and_duplicate_lane_are_visible(self) -> None:
        snapshot = make_snapshot()
        snapshot["evidence"][1]["required_lane"] = "TASK"
        snapshot["evidence"].append(
            copy.deepcopy(snapshot["evidence"][1])
        )
        verdict = evaluate_shadow_snapshot(
            sign(snapshot),
            expected_subject=SUBJECT,
            default_owner_issue=DEFAULT_ISSUE,
        )
        ids = [item.id for item in verdict.generated_findings]
        self.assertIn("SHADOW-LANE-SUBSTITUTION-TRANSPORT", ids)
        self.assertIn("SHADOW-DUPLICATE-LANE-TRANSPORT", ids)

    def test_no_credit_state_cannot_receive_credit(self) -> None:
        snapshot = make_snapshot()
        snapshot["evidence"][2]["closure_credit"] = 1
        verdict = evaluate_shadow_snapshot(
            sign(snapshot),
            expected_subject=SUBJECT,
            default_owner_issue=DEFAULT_ISSUE,
        )
        self.assertIn(
            "SHADOW-FALSE-CREDIT-USER_OUTCOME",
            [item.id for item in verdict.generated_findings],
        )

    def test_pass_requires_exact_subject_or_digest(self) -> None:
        snapshot = make_snapshot()
        snapshot["evidence"][1].update(
            state="PASS",
            closure_credit=1,
            subject=None,
        )
        with self.assertRaisesRegex(
            ShadowContractError, "EVIDENCE_SUBJECT_1_ABSENT"
        ):
            validate_shadow_snapshot(sign(snapshot))

        snapshot = make_snapshot()
        snapshot["evidence"][1].update(
            state="PASS",
            closure_credit=1,
            subject={"digest": "sha256:" + "a" * 64},
        )
        validate_shadow_snapshot(sign(snapshot))

    def test_projection_cannot_write_canonical_state(self) -> None:
        snapshot = make_snapshot()
        snapshot["projections"][2]["commits"] = ["TASK_STATE"]
        verdict = evaluate_shadow_snapshot(
            sign(snapshot),
            expected_subject=SUBJECT,
            default_owner_issue=DEFAULT_ISSUE,
        )
        self.assertIn(
            "SHADOW-PROJECTION-AUTHORITY-GOOGLE_SHEET",
            [item.id for item in verdict.generated_findings],
        )

        snapshot = make_snapshot()
        snapshot["projections"][2]["authority"] = "CANONICAL"
        with self.assertRaisesRegex(
            ShadowContractError,
            "SHARED_PROJECTION_BECAME_AUTHORITY",
        ):
            validate_shadow_snapshot(sign(snapshot))

    def test_shadow_cannot_write_state(self) -> None:
        snapshot = make_snapshot()
        snapshot["shadow"]["may_commit"] = ["TASK_STATE"]
        with self.assertRaisesRegex(
            ShadowContractError, "SHADOW_SECOND_STATE_WRITER"
        ):
            validate_shadow_snapshot(sign(snapshot))

    def test_attempt_denominator_and_exact_pass_subject_are_required(self) -> None:
        snapshot = make_snapshot()
        snapshot["attempt_denominator"] = 2
        with self.assertRaisesRegex(
            ShadowContractError, "ATTEMPT_DENOMINATOR_DROPPED"
        ):
            validate_shadow_snapshot(sign(snapshot))

        snapshot = make_snapshot()
        snapshot["attempts"][0]["subject"] = None
        with self.assertRaisesRegex(
            ShadowContractError, "ATTEMPT_SUBJECT_0_ABSENT"
        ):
            validate_shadow_snapshot(sign(snapshot))

    def test_terminal_state_requires_human_decision_and_cleanup(self) -> None:
        snapshot = make_snapshot()
        snapshot["candidate_state"] = "RELEASED"
        verdict = evaluate_shadow_snapshot(
            sign(snapshot),
            expected_subject=SUBJECT,
            default_owner_issue=DEFAULT_ISSUE,
        )
        ids = [item.id for item in verdict.generated_findings]
        self.assertIn("SHADOW-HUMAN-PROMOTION", ids)
        self.assertIn("SHADOW-CLEANUP-NOT-PASS", ids)

    def test_declared_finding_requires_valid_owner(self) -> None:
        snapshot = make_snapshot()
        snapshot["declared_findings"] = [
            {
                "id": "SHADOW-OWNER",
                "severity": "CRITICAL",
                "state": "OPEN",
                "owner_issue": "missing",
            }
        ]
        with self.assertRaisesRegex(
            ShadowContractError, "CRITICAL_FINDING_WITHOUT_OWNER"
        ):
            validate_shadow_snapshot(sign(snapshot))

    def test_unknown_nested_field_fails_closed(self) -> None:
        snapshot = make_snapshot()
        snapshot["shadow"]["canonical_state"] = True
        with self.assertRaisesRegex(
            ShadowContractError, "SHADOW_AUTHORITY_FIELDS"
        ):
            validate_shadow_snapshot(sign(snapshot))

        snapshot = make_snapshot()
        snapshot["evidence"][0]["extra"] = "not allowed"
        with self.assertRaisesRegex(
            ShadowContractError, "EVIDENCE_0_FIELDS"
        ):
            validate_shadow_snapshot(sign(snapshot))

    def test_silent_edit_breaks_digest(self) -> None:
        snapshot = make_snapshot()
        snapshot["candidate_state"] = "COMPLETE"
        with self.assertRaisesRegex(
            ShadowContractError, "SNAPSHOT_DIGEST_MISMATCH"
        ):
            validate_shadow_snapshot(snapshot)


if __name__ == "__main__":
    unittest.main()
