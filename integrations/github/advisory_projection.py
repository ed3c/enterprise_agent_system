from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Any

SHA40 = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
SECRET = re.compile(
    r"(?i)(authorization\s*:\s*bearer|access[_-]?token\s*[:=]|password\s*[:=]|secret\s*[:=]|cookie\s*[:=])"
)

PROVIDERS = {"GITHUB", "GOOGLE_DOCS", "GOOGLE_SHEETS"}
CLASSIFICATIONS = {"PUBLIC", "INTERNAL_METADATA_ONLY", "RESTRICTED_REFERENCE_ONLY"}
EGRESS_POLICIES = {"PUBLIC_ONLY", "METADATA_ONLY", "NO_CONTENT_EGRESS"}
READ_CAPABILITIES = {"EXERCISED", "DECLARED", "REFUSED", "ABSENT"}
WRITE_CAPABILITIES = {"NOT_REQUESTED", "DECLARED", "REFUSED"}
FRESHNESS_STATES = {"CURRENT", "STALE", "REFUSED", "ABSENT", "PARTIAL"}


class ProjectionError(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ProjectionError(reason)


def digest_bytes(value: bytes) -> str:
    return "sha256:" + sha256(value).hexdigest()


def _validate_time(value: str) -> None:
    require(isinstance(value, str) and value, "RETRIEVED_AT")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProjectionError("RETRIEVED_AT") from exc
    require(parsed.tzinfo is not None, "RETRIEVED_AT_TZ")


def _scan_secret_surface(value: Any) -> None:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    require(SECRET.search(text) is None, "SECRET_OR_SESSION_MATERIAL")


@dataclass(frozen=True)
class ProjectionRecord:
    provider: str
    identity: str
    navigation_url: str
    revision: str | None
    commit: str | None
    tree: str | None
    retrieved_at: str
    content_digest: str | None
    classification: str
    egress_policy: str
    read_capability: str
    write_capability: str
    authority: str
    freshness_state: str
    error_state: str | None
    claims_not_proven: tuple[str, ...]

    def validate(self) -> "ProjectionRecord":
        require(self.provider in PROVIDERS, "PROVIDER")
        require(isinstance(self.identity, str) and self.identity and not self.identity.startswith(("http://", "https://")), "IMMUTABLE_IDENTITY_NOT_URL")
        require(isinstance(self.navigation_url, str) and self.navigation_url.startswith("https://"), "NAVIGATION_URL")
        require(self.classification in CLASSIFICATIONS, "CLASSIFICATION")
        require(self.egress_policy in EGRESS_POLICIES, "EGRESS_POLICY")
        require(self.read_capability in READ_CAPABILITIES, "READ_CAPABILITY")
        require(self.write_capability in WRITE_CAPABILITIES, "WRITE_CAPABILITY")
        require(self.authority == "ADVISORY_ONLY", "AUTHORITY_WIDENING")
        require(self.freshness_state in FRESHNESS_STATES, "FRESHNESS_STATE")
        require(isinstance(self.claims_not_proven, tuple) and bool(self.claims_not_proven), "CLAIMS_NOT_PROVEN")
        _validate_time(self.retrieved_at)

        if self.content_digest is not None:
            require(DIGEST.fullmatch(self.content_digest) is not None, "CONTENT_DIGEST")

        if self.provider == "GITHUB":
            require(isinstance(self.commit, str) and SHA40.fullmatch(self.commit) is not None, "GITHUB_COMMIT")
            require(isinstance(self.tree, str) and SHA40.fullmatch(self.tree) is not None, "GITHUB_TREE")
            require(self.revision == self.commit, "GITHUB_REVISION")
        else:
            require(self.commit is None and self.tree is None, "GOOGLE_CANNOT_PROXY_GIT_SUBJECT")
            if self.freshness_state not in {"REFUSED", "ABSENT"}:
                require(isinstance(self.revision, str) and bool(self.revision), "GOOGLE_REVISION")

        if self.freshness_state == "CURRENT":
            require(self.read_capability == "EXERCISED", "CURRENT_WITHOUT_READBACK")
            require(self.content_digest is not None, "CURRENT_WITHOUT_DIGEST")
            require(self.error_state is None, "CURRENT_WITH_ERROR")
        elif self.freshness_state == "REFUSED":
            require(self.read_capability == "REFUSED" and self.content_digest is None, "REFUSED_ACCESS_SHAPE")
        elif self.freshness_state == "ABSENT":
            require(self.read_capability == "ABSENT" and self.content_digest is None, "ABSENT_ACCESS_SHAPE")
        elif self.freshness_state == "STALE":
            require(self.read_capability == "EXERCISED" and self.content_digest is not None, "STALE_WITHOUT_READBACK")

        _scan_secret_surface(asdict(self))
        return self

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        value = asdict(self)
        value["claims_not_proven"] = list(self.claims_not_proven)
        return value


def reconcile_freshness(record: ProjectionRecord, expected_revision: str) -> ProjectionRecord:
    record.validate()
    require(isinstance(expected_revision, str) and bool(expected_revision), "EXPECTED_REVISION")
    state = "CURRENT" if record.revision == expected_revision else "STALE"
    return replace(record, freshness_state=state).validate()


def require_current(record: ProjectionRecord) -> ProjectionRecord:
    record.validate()
    require(record.freshness_state == "CURRENT", "STALE_OR_NONCURRENT_PROJECTION")
    return record


def render_advisory_projection(record: ProjectionRecord, *, observed_state: str | None = None) -> dict[str, Any]:
    record.validate()
    return {
        "provider": record.provider,
        "identity": record.identity,
        "navigation_url": record.navigation_url,
        "revision": record.revision,
        "commit": record.commit,
        "tree": record.tree,
        "content_digest": record.content_digest,
        "retrieved_at": record.retrieved_at,
        "freshness_state": record.freshness_state,
        "projection_authority": "ADVISORY_ONLY",
        "canonical_state_mutation": False,
        "observed_state": observed_state,
        "claims_not_proven": list(record.claims_not_proven),
    }


def validate_rendered_projection(view: dict[str, Any]) -> dict[str, Any]:
    require(isinstance(view, dict), "VIEW_SHAPE")
    require(view.get("projection_authority") == "ADVISORY_ONLY", "VIEW_AUTHORITY")
    require(view.get("canonical_state_mutation") is False, "CANONICAL_STATE_MUTATION")
    forbidden = {"closure_credit", "task_state", "workflow_state", "effect_state", "human_state", "release_state"}
    require(not (forbidden & set(view)), "CANONICAL_STATE_LAUNDERING")
    _scan_secret_surface(view)
    return view
