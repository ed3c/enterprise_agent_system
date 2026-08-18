"""Independent, read-only Shadow controls for exact public subjects."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Mapping, Sequence

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REPOSITORY = re.compile(r"^[^/\s]+/[^/\s]+$")
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
EVIDENCE_STATES = PASS_STATES | NO_CREDIT_STATES | {"FAIL"}
CANONICAL_AUTHORITIES = frozenset(
    {"TASK_STATE", "WORKFLOW_STATE", "EFFECT_STATE", "HUMAN_STATE", "RELEASE_STATE"}
)
HUMAN_TERMINAL_STATES = frozenset(
    {"HUMAN_ADMITTED", "MERGED", "PROMOTED", "RELEASED"}
)
CANDIDATE_STATES = frozenset(
    {
        "DETERMINISTIC_CANDIDATE",
        "ADMIT_FOR_REVIEW",
        "BLOCKED",
        "COMPLETE",
        *HUMAN_TERMINAL_STATES,
    }
)
ATTEMPT_STATES = frozenset(
    {"PASS", "FAIL", "BLOCKED", "NOT_EXERCISED", "SKIPPED_BY_POLICY"}
)


class ShadowContractError(ValueError):
    """A malformed or authority-widening Shadow input."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ShadowContractError(reason)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _strict_mapping(
    value: Any,
    *,
    required: set[str],
    optional: set[str] | None = None,
    name: str,
) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), f"{name}_NOT_OBJECT")
    optional = optional or set()
    missing = required - set(value)
    unknown = set(value) - required - optional
    _require(
        not missing and not unknown,
        f"{name}_FIELDS:missing={sorted(missing)}:unknown={sorted(unknown)}",
    )
    return value


def _unique_strings(
    value: Any,
    name: str,
    *,
    nonempty: bool = True,
) -> list[str]:
    _require(isinstance(value, list), f"{name}_NOT_ARRAY")
    if nonempty:
        _require(bool(value), f"{name}_EMPTY")
    _require(
        all(isinstance(item, str) and bool(item.strip()) for item in value),
        f"{name}_ITEM",
    )
    _require(len(value) == len(set(value)), f"{name}_DUPLICATE")
    return value


def _exact_subject(subject: Mapping[str, Any], *, prefix: str = "SUBJECT") -> None:
    subject = _strict_mapping(
        subject,
        required={"repository", "commit", "tree"},
        name=prefix,
    )
    _require(
        REPOSITORY.fullmatch(str(subject["repository"])) is not None,
        f"{prefix}_REPOSITORY",
    )
    _require(
        SHA40.fullmatch(str(subject["commit"])) is not None,
        f"{prefix}_COMMIT",
    )
    _require(
        SHA40.fullmatch(str(subject["tree"])) is not None,
        f"{prefix}_TREE",
    )


def _receipt_subject(
    subject: Any,
    *,
    prefix: str,
    required: bool,
) -> None:
    if subject is None:
        _require(not required, f"{prefix}_ABSENT")
        return
    _require(isinstance(subject, Mapping), f"{prefix}_NOT_OBJECT")
    if "repository" in subject:
        _exact_subject(subject, prefix=prefix)
        return
    digest_subject = _strict_mapping(
        subject,
        required={"digest"},
        name=prefix,
    )
    _require(
        SHA256.fullmatch(str(digest_subject["digest"])) is not None,
        f"{prefix}_DIGEST",
    )


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
            "generated_findings": [
                item.as_dict() for item in self.generated_findings
            ],
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
    findings.append(
        ShadowFinding(control, severity, reason, owner_issue)
    )


def validate_shadow_snapshot(snapshot: Mapping[str, Any]) -> None:
    """Validate immutable Shadow input and its read-only authority boundary."""

    snapshot = _strict_mapping(
        snapshot,
        required={
            "schema_version",
            "snapshot_id",
            "subject",
            "source_kind",
            "source_claims_current_fact",
            "frozen_objective",
            "candidate_state",
            "human_decision",
            "shadow",
            "projections",
            "evidence",
            "declared_findings",
            "attempts",
            "attempt_denominator",
            "cleanup",
            "claims_not_proven",
            "snapshot_digest",
        },
        name="SHADOW_SNAPSHOT",
    )
    _require(
        snapshot["schema_version"]
        == "enterprise-agent-system/shadow-snapshot/v2",
        "SHADOW_SCHEMA_VERSION",
    )
    _require(
        isinstance(snapshot["snapshot_id"], str)
        and bool(snapshot["snapshot_id"].strip()),
        "SNAPSHOT_ID",
    )
    _exact_subject(snapshot["subject"])
    _require(
        snapshot["source_kind"] in {"SOURCE_PROPOSAL", "CURRENT_FACT"},
        "SOURCE_KIND",
    )
    _require(
        isinstance(snapshot["source_claims_current_fact"], bool),
        "SOURCE_CLAIMS_CURRENT_FACT_TYPE",
    )
    _unique_strings(snapshot["frozen_objective"], "FROZEN_OBJECTIVE")
    _require(
        snapshot["candidate_state"] in CANDIDATE_STATES,
        "CANDIDATE_STATE",
    )
    _receipt_subject(
        snapshot["human_decision"],
        prefix="HUMAN_DECISION",
        required=False,
    )

    shadow = _strict_mapping(
        snapshot["shadow"],
        required={"read_only", "separate_evaluation_path", "may_commit"},
        name="SHADOW_AUTHORITY",
    )
    _require(shadow["read_only"] is True, "SHADOW_NOT_READ_ONLY")
    _require(
        shadow["separate_evaluation_path"] is True,
        "SHADOW_NOT_SEPARATE",
    )
    _require(
        shadow["may_commit"] == [],
        "SHADOW_SECOND_STATE_WRITER",
    )

    projections = snapshot["projections"]
    _require(isinstance(projections, list), "PROJECTIONS_NOT_ARRAY")
    providers: set[str] = set()
    for index, raw in enumerate(projections):
        projection = _strict_mapping(
            raw,
            required={"provider", "authority", "commits"},
            name=f"PROJECTION_{index}",
        )
        provider = projection["provider"]
        _require(
            isinstance(provider, str)
            and bool(provider.strip())
            and provider not in providers,
            f"PROJECTION_PROVIDER:{provider}",
        )
        providers.add(provider)
        _require(
            projection["authority"] == "ADVISORY_ONLY",
            f"SHARED_PROJECTION_BECAME_AUTHORITY:{provider}",
        )
        _unique_strings(
            projection["commits"],
            f"PROJECTION_COMMITS:{provider}",
            nonempty=False,
        )

    evidence = snapshot["evidence"]
    _require(isinstance(evidence, list), "EVIDENCE_NOT_ARRAY")
    for index, raw in enumerate(evidence):
        item = _strict_mapping(
            raw,
            required={
                "lane",
                "required_lane",
                "state",
                "closure_credit",
                "subject",
                "owner_issue",
            },
            name=f"EVIDENCE_{index}",
        )
        _require(
            isinstance(item["lane"], str) and bool(item["lane"].strip()),
            f"EVIDENCE_LANE:{index}",
        )
        _require(
            isinstance(item["required_lane"], str)
            and bool(item["required_lane"].strip()),
            f"EVIDENCE_REQUIRED_LANE:{index}",
        )
        _require(
            item["state"] in EVIDENCE_STATES,
            f"EVIDENCE_STATE:{index}",
        )
        _require(
            isinstance(item["closure_credit"], int)
            and item["closure_credit"] >= 0,
            f"EVIDENCE_CREDIT:{index}",
        )
        _require(
            isinstance(item["owner_issue"], str)
            and ISSUE.fullmatch(item["owner_issue"]) is not None,
            f"EVIDENCE_OWNER:{index}",
        )
        _receipt_subject(
            item["subject"],
            prefix=f"EVIDENCE_SUBJECT_{index}",
            required=item["state"] in PASS_STATES,
        )

    findings = snapshot["declared_findings"]
    _require(isinstance(findings, list), "DECLARED_FINDINGS_NOT_ARRAY")
    finding_ids: set[str] = set()
    for index, raw in enumerate(findings):
        finding = _strict_mapping(
            raw,
            required={"id", "severity", "state", "owner_issue"},
            name=f"DECLARED_FINDING_{index}",
        )
        finding_id = finding["id"]
        _require(
            isinstance(finding_id, str)
            and bool(finding_id.strip())
            and finding_id not in finding_ids,
            f"DECLARED_FINDING_ID:{finding_id}",
        )
        finding_ids.add(finding_id)
        _require(
            finding["severity"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"},
            f"DECLARED_FINDING_SEVERITY:{finding_id}",
        )
        _require(
            finding["state"] in {"OPEN", "RESOLVED", "SUPERSEDED"},
            f"DECLARED_FINDING_STATE:{finding_id}",
        )
        _require(
            isinstance(finding["owner_issue"], str)
            and ISSUE.fullmatch(finding["owner_issue"]) is not None,
            f"CRITICAL_FINDING_WITHOUT_OWNER:{finding_id}",
        )

    attempts = snapshot["attempts"]
    _require(isinstance(attempts, list), "ATTEMPTS_NOT_ARRAY")
    attempt_ids: set[str] = set()
    for index, raw in enumerate(attempts):
        attempt = _strict_mapping(
            raw,
            required={"id", "state"},
            optional={"subject", "evidence"},
            name=f"ATTEMPT_{index}",
        )
        attempt_id = attempt["id"]
        _require(
            isinstance(attempt_id, str)
            and bool(attempt_id.strip())
            and attempt_id not in attempt_ids,
            f"ATTEMPT_ID:{attempt_id}",
        )
        attempt_ids.add(attempt_id)
        _require(
            attempt["state"] in ATTEMPT_STATES,
            f"ATTEMPT_STATE:{attempt_id}",
        )
        if "subject" in attempt:
            _receipt_subject(
                attempt["subject"],
                prefix=f"ATTEMPT_SUBJECT_{index}",
                required=attempt["state"] == "PASS",
            )

    _require(
        isinstance(snapshot["attempt_denominator"], int)
        and snapshot["attempt_denominator"] == len(attempts),
        "ATTEMPT_DENOMINATOR_DROPPED",
    )

    cleanup = _strict_mapping(
        snapshot["cleanup"],
        required={"state", "residue"},
        name="CLEANUP",
    )
    _require(
        cleanup["state"] in {"PASS", "NOT_EXERCISED", "BLOCKED"},
        "CLEANUP_STATE",
    )
    _require(
        isinstance(cleanup["residue"], str)
        and bool(cleanup["residue"].strip()),
        "CLEANUP_RESIDUE",
    )
    _unique_strings(snapshot["claims_not_proven"], "CLAIMS_NOT_PROVEN")

    digest = snapshot["snapshot_digest"]
    _require(
        isinstance(digest, str)
        and SHA256.fullmatch(digest) is not None,
        "SNAPSHOT_DIGEST",
    )
    unsigned = dict(snapshot)
    unsigned.pop("snapshot_digest")
    expected = (
        "sha256:" + hashlib.sha256(_canonical_json(unsigned)).hexdigest()
    )
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
    _require(
        ISSUE.fullmatch(default_owner_issue) is not None,
        "DEFAULT_OWNER_ISSUE",
    )

    findings: list[ShadowFinding] = []
    if dict(snapshot["subject"]) != dict(expected_subject):
        _finding(
            findings,
            control="SHADOW-STALE-SUBJECT",
            reason=(
                "Shadow snapshot does not bind the expected immutable "
                "repository/commit/tree"
            ),
            owner_issue=default_owner_issue,
        )

    if (
        snapshot["source_kind"] == "SOURCE_PROPOSAL"
        and snapshot["source_claims_current_fact"] is True
    ):
        _finding(
            findings,
            control="SHADOW-SOURCE-PROMOTION",
            reason=(
                "SOURCE_PROPOSAL was promoted to CURRENT_FACT without an "
                "independent evidence lane"
            ),
            owner_issue=default_owner_issue,
        )

    seen_lanes: set[str] = set()
    for evidence in snapshot["evidence"]:
        lane = evidence["lane"]
        required_lane = evidence["required_lane"]
        state = evidence["state"]
        owner_issue = evidence["owner_issue"]

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
                reason=(
                    f"Receipt lane {lane} substituted for required lane "
                    f"{required_lane}"
                ),
                owner_issue=owner_issue,
            )

        credit = evidence["closure_credit"]
        if state in NO_CREDIT_STATES and credit != 0:
            _finding(
                findings,
                control=f"SHADOW-FALSE-CREDIT-{lane}",
                reason=f"{state} evidence in {lane} received closure credit",
                owner_issue=owner_issue,
            )

    for projection in snapshot["projections"]:
        illegal = set(projection["commits"]) & CANONICAL_AUTHORITIES
        if illegal:
            _finding(
                findings,
                control=(
                    "SHADOW-PROJECTION-AUTHORITY-"
                    f"{projection['provider']}"
                ),
                reason=(
                    "Advisory projection attempted to commit "
                    f"{sorted(illegal)}"
                ),
                owner_issue=default_owner_issue,
            )

    current_state = snapshot["candidate_state"]
    if (
        current_state in HUMAN_TERMINAL_STATES
        and snapshot["human_decision"] is None
    ):
        _finding(
            findings,
            control="SHADOW-HUMAN-PROMOTION",
            reason=(
                f"Candidate claimed {current_state} without a Human "
                "decision subject"
            ),
            owner_issue=default_owner_issue,
        )

    if (
        current_state in {"COMPLETE", *HUMAN_TERMINAL_STATES}
        and snapshot["cleanup"]["state"] != "PASS"
    ):
        _finding(
            findings,
            control="SHADOW-CLEANUP-NOT-PASS",
            reason=(
                "Terminal candidate state was claimed without successful "
                "cleanup/readback"
            ),
            owner_issue=default_owner_issue,
        )

    open_declared = sorted(
        finding["id"]
        for finding in snapshot["declared_findings"]
        if finding["severity"] == "CRITICAL"
        and finding["state"] == "OPEN"
    )

    if findings or open_declared:
        state = "BLOCKED_FOR_CLOSURE"
    elif current_state in HUMAN_TERMINAL_STATES:
        state = "HUMAN_ADMIT_REQUIRED"
    else:
        state = "ADMIT_FOR_REVIEW"

    return ShadowVerdict(
        state=state,
        generated_findings=tuple(findings),
        open_declared_findings=tuple(open_declared),
        claims_not_proven=tuple(
            sorted(set(snapshot["claims_not_proven"]))
        ),
    )
