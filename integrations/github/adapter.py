from __future__ import annotations

from .advisory_projection import (
    ProjectionRecord,
    digest_bytes,
    reconcile_freshness,
    render_advisory_projection,
    validate_rendered_projection,
)


def capture_github_projection(
    *,
    identity: str,
    navigation_url: str,
    commit: str,
    tree: str,
    content_bytes: bytes,
    retrieved_at: str,
    expected_revision: str | None = None,
    classification: str = "PUBLIC",
    egress_policy: str = "PUBLIC_ONLY",
) -> ProjectionRecord:
    record = ProjectionRecord(
        provider="GITHUB",
        identity=identity,
        navigation_url=navigation_url,
        revision=commit,
        commit=commit,
        tree=tree,
        retrieved_at=retrieved_at,
        content_digest=digest_bytes(content_bytes),
        classification=classification,
        egress_policy=egress_policy,
        read_capability="EXERCISED",
        write_capability="NOT_REQUESTED",
        authority="ADVISORY_ONLY",
        freshness_state="CURRENT",
        error_state=None,
        claims_not_proven=(
            "GitHub metadata does not prove implementation, runtime, effect, user, Human, merge, release, or rollback closure.",
            "A navigation URL is not immutable identity without the bound commit/tree and digest.",
        ),
    ).validate()
    if expected_revision is not None:
        record = reconcile_freshness(record, expected_revision)
    return record


def render_github_view(record: ProjectionRecord, *, observed_state: str | None = None) -> dict[str, object]:
    view = render_advisory_projection(record, observed_state=observed_state)
    return validate_rendered_projection(view)
