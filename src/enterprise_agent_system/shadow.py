"""Independent, read-only Shadow closure controls for exact public subjects."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Mapping, Sequence

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
ISSUE = re.compile(r"^https://github\.com/[^/]+/[^/]+/issues/[1-9][0-9]*$")

PASS_STATES = frozenset({"PASS", "RELEASED"})
NO_CREDIT_STATES = frozenset(
    {
        "ABSENT",
        "NOT_IMPLEMENTED",
        "NOT_EXERCISED",
        "SKIPPED_BY_POLICY",
        "STALE",
        "BLOCKED",
        "PARTIAL",
        "HUMAN_ADMIT_REQUIRED",
    }
)
CANONICAL_AUTHORITIES = frozenset(
    {"TASK_STATE", "WORKFLOW_STATE", "EFFECT_STATE", "HUMAN_STATE", "RELEASE_STATE"}
)
HUMAN_TERMINAL_STATES = frozenset({"HUMAN_ADMITTED", "MERGED", "PROMOTED", "RELEASED"})


class ShadowContractError(ValueError):
    """A malformed or authority-widening Shadow input."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ShadowContractError(reason)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _exact_subject(subject: Mapping[str, Any], *, prefix: str = "SUBJECT") -> None:
    _require(
        isinstance(subject.get("repository"), str) and "/" in subject["repository"],
        f"{prefix}_REPOSITORY",
    )
    _require(SHA40.fullmatch(str(subject.get("commit", ""))) is not None, f"{prefix}_COMMIT")
    _require(SHA40.fullmatch(str(subject.get("tree", ""))) is not None, f"{prefix}_TREE")


@dataclass(frozen=True)
class ShadowFinding:
    id: str
    severity: str
    reason: str
    owner_issue: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "severity": self.severity,
            "reason": self.reason,
            "owner_issue": self.owner_issue,
        }


@dataclass(frozen=True)
class ShadowVerdict:
    state: str
    generated_findings: tuple[ShadowFinding, ...]
    open_declared_findings: tuple[str, ...]
    claims_not_proven: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "generated_findings": [item.as_dict() for item in self.generated_findings],
            "open_declared_findings": list(self.open_declared_findings),
            "claims_not_proven": list(self.claims_not_proven),
        }


def _finding(
    findings: list[ShadowFinding],
    *,
    control: str,
    reason: str,
    owner_issue: str,
    severity: str = "CRITICAL",
) -> None:
    findings.append(ShadowFinding(control, severity, reason, owner_issue))


def validate_shadow_snapshot(snapshot: Mapping[str, Any]) -> None:
    """Validate the immutable Shadow input and its own authority boundary."""

    _require(
        snapshot.get("schema_version") == "enterprise-agent-system/shadow-snapshot/v1",
        "SHADOW_SCHEMA_VERSION",
    )
    _exact_subject(snapshot.get("subject", {}))
    _require(
        snapshot.get("source_kind") in {"SOURCE_PROPOSAL", "CURRENT_FACT"},
        "SOURCE_KIND",
    )
    _require(bool(snapshot.get("frozen_objective")), "FROZEN_OBJECTIVE_EMPTY")
    _require(bool(snapshot.get("claims_not_proven")), "CLAIMS_NOT_PROVEN_EMPTY")

    shadow = snapshot.get("shadow", {})
    _require(shadow.get("read_only") is True, "SHADOW_NOT_READ_ONLY")
    _require(shadow.get("separate_evaluation_path") is True, "SHADOW_NOT_SEPARATE")
    _require(shadow.get("may_commit") == [], "SHADOW_SECOND_STATE_WRITER")

    projections = snapshot.get("projections", [])
    _require(isinstance(projections, list), "PROJECTIONS_NOT_ARRAY")
    for projection in projections:
        _require(
            projection.get("authority") == "ADVISORY_ONLY",
            f"SHARED_PROJECTION_BECAME_AUTHORITY:{projection.get('provider', 'UNKNOWN')}",
        )

    attempts = snapshot.get("attempts", [])
    _require(isinstance(attempts, list), "ATTEMPTS_NOT_ARRAY")
    _require(
        snapshot.get("attempt_denominator") == len(attempts),
        "ATTEMPT_DENOMINATOR_DROPPED",
    )

    cleanup = snapshot.get("cleanup", {})
    _require(cleanup.get("state") in {"PASS", "NOT_EXERCISED", "BLOCKED"}, "CLEANUP_STATE")

    digest = snapshot.get("snapshot_digest")
    _require(isinstance(digest, str) and SHA256.fullmatch(digest) is not None, "SNAPSHOT_DIGEST")
    unsigned = dict(snapshot)
    unsigned.pop("snapshot_digest", None)
    expected = "sha256:" + hashlib.sha256(_canonical_json(unsigned)).hexdigest()
    _require(digest == expected, "SNAPSHOT_DIGEST_MISMATCH")


def evaluate_shadow_snapshot(
    snapshot: Mapping[str, Any],
    *,
    expected_subject: Mapping[str, Any],
    default_owner_issue: str,
) -> ShadowVerdict:
    """Evaluate contradictions without mutating Builder or canonical state."""

    validate_shadow_snapshot(snapshot)
    _exact_subject(expected_subject, prefix="EXPECTED_SUBJECT")
    _require(ISSUE.fullmatch(default_owner_issue) is not None, "DEFAULT_OWNER_ISSUE")

    findings: list[ShadowFinding] = []
    subject = snapshot["subject"]
    if subject.get("commit") != expected_subject.get("commit") or subject.get("tree") != expected_subject.get("tree"):
        _finding(
            findings,
            control="SHADOW-STALE-SUBJECT",
            reason="Shadow snapshot does not bind the expected immutable Builder subject",
            owner_issue=default_owner_issue,
        )

    if snapshot["source_kind"] == "SOURCE_PROPOSAL" and snapshot.get("source_claims_current_fact") is True:
        _finding(
            findings,
            control="SHADOW-SOURCE-PROMOTION",
            reason="SOURCE_PROPOSAL was promoted to CURRENT_FACT without an independent evidence lane",
            owner_issue=default_owner_issue,
        )

    seen_lanes: set[str] = set()
    for evidence in snapshot.get("evidence", []):
        lane = str(evidence.get("lane", "UNKNOWN"))
        required_lane = str(evidence.get("required_lane", "UNKNOWN"))
        state = str(evidence.get("state", "UNKNOWN"))
        owner_issue = str(evidence.get("owner_issue") or default_owner_issue)
        if ISSUE.fullmatch(owner_issue) is None:
            owner_issue = default_owner_issue
            _finding(
                findings,
                control=f"SHADOW-EVIDENCE-OWNER-{lane}",
                reason=f"Evidence lane {lane} has no valid owner issue",
                owner_issue=owner_issue,
            )
        if lane in seen_lanes:
            _finding(
                findings,
                control=f"SHADOW-DUPLICATE-LANE-{lane}",
                reason=f"Evidence lane {lane} appears more than once",
                owner_issue=owner_issue,
            )
        seen_lanes.add(lane)
        if lane != required_lane:
            _finding(
                findings,
                control=f"SHADOW-LANE-SUBSTITUTION-{lane}",
                reason=f"Receipt lane {lane} substituted for required lane {required_lane}",
                owner_issue=owner_issue,
            )
        credit = int(evidence.get("closure_credit", 0))
        if state in NO_CREDIT_STATES and credit != 0:
            _finding(
                findings,
                control=f"SHADOW-FALSE-CREDIT-{lane}",
                reason=f"{state} evidence in {lane} received closure credit",
                owner_issue=owner_issue,
            )
        receipt_subject = evidence.get("subject")
        if state in PASS_STATES:
            if not isinstance(receipt_subject, Mapping):
                _finding(
                    findings,
                    control=f"SHADOW-PASS-WITHOUT-SUBJECT-{lane}",
                    reason=f"{state} evidence in {lane} has no exact receipt subject",
                    owner_issue=owner_issue,
                )
            elif "repository" in receipt_subject:
                try:
                    _exact_subject(receipt_subject, prefix=f"EVIDENCE_{lane}")
                except ShadowContractError as exc:
                    _finding(
                        findings,
                        control=f"SHADOW-MUTABLE-EVIDENCE-{lane}",
                        reason=str(exc),
                        owner_issue=owner_issue,
                    )
            elif SHA256.fullmatch(str(receipt_subject.get("digest", ""))) is None:
                _finding(
                    findings,
                    control=f"SHADOW-EVIDENCE-DIGEST-{lane}",
                    reason=f"{state} evidence in {lane} lacks an immutable digest",
                    owner_issue=owner_issue,
                )

    for projection in snapshot.get("projections", []):
        committed = set(projection.get("commits", []))
        illegal = committed & CANONICAL_AUTHORITIES
        if illegal:
            _finding(
                findings,
                control=f"SHADOW-PROJECTION-AUTHORITY-{projection.get('provider', 'UNKNOWN')}",
                reason=f"Advisory projection attempted to commit {sorted(illegal)}",
                owner_issue=default_owner_issue,
            )

    current_state = str(snapshot.get("candidate_state", "UNKNOWN"))
    if current_state in HUMAN_TERMINAL_STATES and snapshot.get("human_decision") is None:
        _finding(
            findings,
            control="SHADOW-HUMAN-PROMOTION",
            reason=f"Candidate claimed {current_state} without a Human decision subject",
            owner_issue=default_owner_issue,
        )

    if current_state in {"COMPLETE", *HUMAN_TERMINAL_STATES} and snapshot.get("cleanup", {}).get("state") != "PASS":
        _finding(
            findings,
            control="SHADOW-CLEANUP-NOT-PASS",
            reason="Terminal candidate state was claimed without successful cleanup/readback",
            owner_issue=default_owner_issue,
        )

    open_declared: list[str] = []
    for declared in snapshot.get("declared_findings", []):
        if declared.get("severity") == "CRITICAL" and declared.get("state") != "RESOLVED":
            owner_issue = str(declared.get("owner_issue", ""))
            _require(ISSUE.fullmatch(owner_issue) is not None, f"CRITICAL_FINDING_WITHOUT_OWNER:{declared.get('id')}")
            open_declared.append(str(declared.get("id")))

    if findings or open_declared:
        state = "BLOCKED_FOR_CLOSURE"
    elif current_state in HUMAN_TERMINAL_STATES:
        state = "HUMAN_ADMIT_REQUIRED"
    else:
        state = "ADMIT_FOR_REVIEW"

    return ShadowVerdict(
        state=state,
        generated_findings=tuple(findings),
        open_declared_findings=tuple(sorted(open_declared)),
        claims_not_proven=tuple(sorted(set(snapshot.get("claims_not_proven", [])))),
    )
