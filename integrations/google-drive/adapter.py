from __future__ import annotations

from typing import Iterable

from integrations.github.advisory_projection import (
    ProjectionError,
    ProjectionRecord,
    digest_bytes,
    reconcile_freshness,
    render_advisory_projection,
    validate_rendered_projection,
)

ALLOWED_TARGETS = {"NARRATIVE", "DASHBOARD", "PROMPT_CATALOGUE_MIRROR"}


def capture_google_projection(
    *,
    provider: str,
    document_id: str,
    revision: str | None,
    content_bytes: bytes | None,
    retrieved_at: str,
    access_state: str = "EXERCISED",
    expected_revision: str | None = None,
    classification: str = "INTERNAL_METADATA_ONLY",
    egress_policy: str = "METADATA_ONLY",
) -> ProjectionRecord:
    if provider not in {"GOOGLE_DOCS", "GOOGLE_SHEETS"}:
        raise ProjectionError("GOOGLE_PROVIDER")
    if access_state not in {"EXERCISED", "REFUSED", "ABSENT"}:
        raise ProjectionError("GOOGLE_ACCESS_STATE")
    if access_state == "EXERCISED" and content_bytes is None:
        raise ProjectionError("GOOGLE_READBACK_REQUIRED")
    if access_state in {"REFUSED", "ABSENT"} and content_bytes is not None:
        raise ProjectionError("GOOGLE_ACCESS_CANNOT_CARRY_CONTENT")

    suffix = "document/d" if provider == "GOOGLE_DOCS" else "spreadsheets/d"
    freshness = "CURRENT" if access_state == "EXERCISED" else access_state
    record = ProjectionRecord(
        provider=provider,
        identity=f"{provider}:{document_id}",
        navigation_url=f"https://docs.google.com/{suffix}/{document_id}",
        revision=revision,
        commit=None,
        tree=None,
        retrieved_at=retrieved_at,
        content_digest=digest_bytes(content_bytes) if content_bytes is not None else None,
        classification=classification,
        egress_policy=egress_policy,
        read_capability=access_state,
        write_capability="NOT_REQUESTED",
        authority="ADVISORY_ONLY",
        freshness_state=freshness,
        error_state=None if access_state == "EXERCISED" else access_state,
        claims_not_proven=(
            "Google Docs/Sheets content is an advisory projection and cannot mutate canonical task/workflow/effect/Human/release state.",
            "A Google revision or successful read does not prove source correctness, runtime behavior, or closure.",
        ),
    ).validate()
    if expected_revision is not None and access_state == "EXERCISED":
        record = reconcile_freshness(record, expected_revision)
    return record


def render_google_view(
    record: ProjectionRecord,
    *,
    target_class: str,
    github_linkbacks: Iterable[dict[str, str]],
) -> dict[str, object]:
    if target_class not in ALLOWED_TARGETS:
        raise ProjectionError("GOOGLE_TARGET_NOT_ADVISORY")
    refs = list(github_linkbacks)
    for ref in refs:
        required = {"repository", "commit", "tree", "reference"}
        if set(ref) != required:
            raise ProjectionError("GITHUB_LINKBACK_SHAPE")
        if len(ref["commit"]) != 40 or len(ref["tree"]) != 40:
            raise ProjectionError("GITHUB_LINKBACK_SUBJECT")
    view = render_advisory_projection(record)
    view.update({
        "target_class": target_class,
        "github_linkbacks": refs,
        "write_action_available": False,
    })
    return validate_rendered_projection(view)


def request_write(*_: object, **__: object) -> None:
    raise ProjectionError("WRITE_REQUIRES_SEPARATE_EXPLICIT_AUTHORITY")
