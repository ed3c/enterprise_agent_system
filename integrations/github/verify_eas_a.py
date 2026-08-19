#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import replace
import importlib.util
from pathlib import Path
import sys
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from integrations.github.advisory_projection import (  # noqa: E402
    ProjectionError,
    ProjectionRecord,
    require_current,
    validate_rendered_projection,
)
from integrations.github.adapter import capture_github_projection, render_github_view  # noqa: E402

GOOGLE_PATH = ROOT / "integrations/google-drive/adapter.py"
spec = importlib.util.spec_from_file_location("eas_a_google_adapter", GOOGLE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("GOOGLE_ADAPTER_LOAD")
google = importlib.util.module_from_spec(spec)
spec.loader.exec_module(google)

NOW = "2026-08-20T00:00:00+00:00"
GIT_COMMIT = "a" * 40
GIT_TREE = "b" * 40


def github_record(*, expected_revision: str | None = None) -> ProjectionRecord:
    return capture_github_projection(
        identity="ed3c/enterprise_agent_system:PR-59",
        navigation_url="https://github.com/ed3c/enterprise_agent_system/pull/59",
        commit=GIT_COMMIT,
        tree=GIT_TREE,
        content_bytes=b"public github projection fixture",
        retrieved_at=NOW,
        expected_revision=expected_revision,
    )


def google_doc() -> ProjectionRecord:
    return google.capture_google_projection(
        provider="GOOGLE_DOCS",
        document_id="doc-fixture",
        revision="rev-7",
        content_bytes=b"advisory narrative fixture",
        retrieved_at=NOW,
    )


def positives() -> None:
    gh = github_record()
    assert gh.freshness_state == "CURRENT"
    gh_view = render_github_view(gh, observed_state="closed")
    assert gh_view["projection_authority"] == "ADVISORY_ONLY"
    assert gh_view["canonical_state_mutation"] is False
    assert "closure_credit" not in gh_view

    doc = google_doc()
    doc_view = google.render_google_view(
        doc,
        target_class="NARRATIVE",
        github_linkbacks=[{
            "repository": "ed3c/enterprise_agent_system",
            "commit": GIT_COMMIT,
            "tree": GIT_TREE,
            "reference": "issue#10",
        }],
    )
    assert doc_view["write_action_available"] is False
    assert doc_view["projection_authority"] == "ADVISORY_ONLY"

    sheet_refused = google.capture_google_projection(
        provider="GOOGLE_SHEETS",
        document_id="sheet-fixture",
        revision=None,
        content_bytes=None,
        retrieved_at=NOW,
        access_state="REFUSED",
    )
    assert sheet_refused.freshness_state == "REFUSED"
    assert sheet_refused.content_digest is None

    print("PASS EAS-A positives github=1 google_docs=1 google_sheets_refused=1 authority=ADVISORY_ONLY")


def must_refuse(label: str, fn: Callable[[], object]) -> None:
    try:
        fn()
    except (ProjectionError, AssertionError, ValueError):
        return
    raise AssertionError(f"mutation accepted: {label}")


def selftest() -> None:
    gh = github_record()
    doc = google_doc()

    tests: list[tuple[str, Callable[[], object]]] = [
        ("url as immutable identity", lambda: replace(gh, identity=gh.navigation_url).validate()),
        ("authority widening", lambda: replace(gh, authority="CANONICAL").validate()),
        ("bad github commit", lambda: replace(gh, commit="bad", revision="bad").validate()),
        ("current without digest", lambda: replace(gh, content_digest=None).validate()),
        ("current without readback", lambda: replace(doc, read_capability="ABSENT", freshness_state="CURRENT").validate()),
        ("write exercised in advisory record", lambda: replace(doc, write_capability="EXERCISED").validate()),
        ("secret persisted", lambda: replace(gh, identity="repo:access_token=abcd1234").validate()),
        ("github receipt proxies google", lambda: replace(gh, provider="GOOGLE_DOCS", revision="rev-1").validate()),
        ("egress widened", lambda: replace(gh, egress_policy="UNRESTRICTED").validate()),
        ("stale accepted as current", lambda: require_current(github_record(expected_revision="f" * 40))),
        (
            "absent access represented as content",
            lambda: google.capture_google_projection(
                provider="GOOGLE_SHEETS",
                document_id="sheet",
                revision=None,
                content_bytes=b"",
                retrieved_at=NOW,
                access_state="ABSENT",
            ),
        ),
        (
            "google silently rewrites canonical prompt",
            lambda: google.render_google_view(
                doc,
                target_class="CANONICAL_PROMPT_PACKET",
                github_linkbacks=[{
                    "repository": "ed3c/enterprise_agent_system",
                    "commit": GIT_COMMIT,
                    "tree": GIT_TREE,
                    "reference": "prompt",
                }],
            ),
        ),
        (
            "malformed github linkback",
            lambda: google.render_google_view(
                doc,
                target_class="DASHBOARD",
                github_linkbacks=[{
                    "repository": "ed3c/enterprise_agent_system",
                    "commit": "short",
                    "tree": GIT_TREE,
                    "reference": "issue#10",
                }],
            ),
        ),
        ("google write without authority", lambda: google.request_write(doc)),
        (
            "closed github issue becomes closure credit",
            lambda: validate_rendered_projection({**render_github_view(gh, observed_state="closed"), "closure_credit": 1}),
        ),
        ("google receipt carries git subject", lambda: replace(doc, commit=GIT_COMMIT, tree=GIT_TREE).validate()),
        ("current carries error", lambda: replace(gh, error_state="provider-error").validate()),
        ("non-https navigation", lambda: replace(gh, navigation_url="git://example.invalid/repo").validate()),
    ]

    for label, fn in tests:
        must_refuse(label, fn)
    print(f"PASS EAS-A planted refusals={len(tests)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    selftest() if args.selftest else positives()


if __name__ == "__main__":
    main()
