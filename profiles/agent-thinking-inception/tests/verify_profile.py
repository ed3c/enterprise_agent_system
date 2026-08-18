#!/usr/bin/env python3
"""Deterministic semantic gate for the Agent Thinking Inception profile."""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import sys
from collections.abc import Callable
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
REQ_PATH = ROOT / "requirements" / "requirements.json"
CONTRA_PATH = ROOT / "requirements" / "contradictions.json"
SOURCE_PATH = ROOT / "source" / "source-subject.json"
MAP_PATH = ROOT / "source" / "source-map.json"
PROFILE_PATH = ROOT / "examples" / "inception-profile.example.json"

ALLOWED_STATES = {"SOURCE_PROPOSAL", "OWNER_PROPOSED", "CONTRACT_BOUND", "NOT_IMPLEMENTED", "NOT_EXERCISED", "BLOCKED"}
REQUIRED_OWNER_PREFIX = "ed3c/"
FORBIDDEN_LOCATOR_FRAGMENTS = ("gemini.google.com/app/", "/mnt/data/", "file_000000", "session=")
ABSOLUTE_CLAIMS = ("zero hallucination", "zero-hallucination", "zero leakage", "100% safe", "commercially safe", "production ready")


class Refusal(ValueError):
    pass


def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(source: dict[str, Any], source_map: dict[str, Any], requirements: dict[str, Any],
                    contradictions: dict[str, Any], profile: dict[str, Any]) -> None:
    errors: list[str] = []

    digest = source.get("content_digest", "")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        errors.append("source digest is absent or invalid")
    locator_text = json.dumps(source.get("locator", {}), sort_keys=True).lower()
    if any(fragment in locator_text for fragment in FORBIDDEN_LOCATOR_FRAGMENTS):
        errors.append("private/session/local locator leaked")
    if source.get("source_kind") != "SOURCE_PROPOSAL":
        errors.append("PDF source must remain SOURCE_PROPOSAL")
    if source.get("subject_id") != "SRC-PDF-INCEPTION-001":
        errors.append("source subject identity drift")
    if source.get("data_class") != "LOCAL_ONLY" or source.get("egress_allowed") is not False:
        errors.append("user-supplied source bytes must remain LOCAL_ONLY with egress disabled")
    if source_map.get("page_count") != 26 or not source_map.get("sections"):
        errors.append("page map is incomplete")

    items = requirements.get("requirements", [])
    if not items:
        errors.append("requirement denominator is empty")
    ids = [item.get("requirement_id") for item in items]
    if len(ids) != len(set(ids)):
        errors.append("duplicate requirement ID")
    for item in items:
        rid = item.get("requirement_id", "<missing>")
        if not re.fullmatch(r"REQ-PDF-INCEPTION-[A-Z]+-[0-9]{3}", rid):
            errors.append(f"{rid}: invalid requirement ID")
        pages = item.get("source_pages")
        if not isinstance(pages, list) or not pages or any(not isinstance(p, int) or p < 1 or p > 26 for p in pages):
            errors.append(f"{rid}: missing or invalid page locator")
        owner = item.get("owner", {})
        if not str(owner.get("repository", "")).startswith(REQUIRED_OWNER_PREFIX):
            errors.append(f"{rid}: missing canonical owner repository")
        if not owner.get("directory") or not re.fullmatch(r"https://github\.com/ed3c/enterprise_agent_system/issues/[0-9]+", str(owner.get("issue", ""))):
            errors.append(f"{rid}: missing owner directory or issue")
        if "→" not in str(item.get("state_machine", "")):
            errors.append(f"{rid}: State Machine is absent")
        for field in ("inputs", "outputs", "positive_controls", "mutation_controls", "blockers", "claims_not_proven"):
            value = item.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{rid}: {field} must be non-empty")
        if item.get("current_state") not in ALLOWED_STATES:
            errors.append(f"{rid}: invalid or falsely promoted current_state")
        if not item.get("required_evidence_lane") or not item.get("next_transition"):
            errors.append(f"{rid}: evidence lane or next transition is absent")
        combined = " ".join([str(item.get("source_claim", "")), str(item.get("real_problem", ""))]).lower()
        if any(term in combined for term in ABSOLUTE_CLAIMS) and "cannot guarantee" not in combined and "does not prove" not in combined:
            errors.append(f"{rid}: unsupported absolute claim")

    declared_total = requirements.get("denominator", {}).get("total")
    if declared_total != len(items):
        errors.append("requirement denominator count mismatch")

    citems = contradictions.get("items", [])
    if len(citems) < 12:
        errors.append("contradiction denominator is incomplete")
    cids = [item.get("id") for item in citems]
    if len(cids) != len(set(cids)):
        errors.append("duplicate contradiction ID")
    for item in citems:
        if not item.get("source_pages") or not item.get("risk") or not item.get("owner_issue") or not item.get("required_control"):
            errors.append(f"{item.get('id', '<missing>')}: incomplete contradiction route")

    if profile.get("source_digest") != digest:
        errors.append("profile/source digest mismatch")
    if profile.get("evidence_ceiling") != "SOURCE_AND_CONTRACT_CANDIDATE_ONLY":
        errors.append("profile evidence ceiling widened")
    owners = profile.get("owner_repositories", [])
    if len(set(owners)) != len(owners) or len(owners) < 6:
        errors.append("owner repository set is duplicate or incomplete")

    if errors:
        raise Refusal("; ".join(errors))


def selftest(bundle: tuple[dict[str, Any], ...]) -> None:
    mutations: list[tuple[str, Callable[[list[dict[str, Any]]], None]]] = [
        ("duplicate requirement", lambda b: b[2]["requirements"].append(copy.deepcopy(b[2]["requirements"][0]))),
        ("missing page", lambda b: b[2]["requirements"][0].update(source_pages=[])),
        ("missing owner", lambda b: b[2]["requirements"][0]["owner"].update(repository="")),
        ("private locator", lambda b: b[0]["locator"].update(url="https://gemini.google.com/app/private")),
        ("source promoted", lambda b: b[0].update(source_kind="CURRENT_FACT")),
        ("source egress widened", lambda b: b[0].update(data_class="PUBLIC", egress_allowed=True)),
        ("false evidence state", lambda b: b[2]["requirements"][0].update(current_state="PASS")),
        ("missing mutation control", lambda b: b[2]["requirements"][0].update(mutation_controls=[])),
        ("missing blocker", lambda b: b[2]["requirements"][0].update(blockers=[])),
        ("digest drift", lambda b: b[4].update(source_digest="sha256:" + "0" * 64)),
        ("contradiction owner absent", lambda b: b[3]["items"][0].update(owner_issue="")),
    ]
    for name, mutate in mutations:
        candidate = [copy.deepcopy(x) for x in bundle]
        mutate(candidate)
        try:
            validate_bundle(*candidate)
        except Refusal:
            continue
        raise Refusal(f"selftest mutation was not refused: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    manifest = load(REQ_PATH)
    combined = dict(manifest)
    combined["requirements"] = []
    for shard_name in manifest.get("shards", []):
        shard_path = ROOT / "requirements" / shard_name
        shard = load(shard_path)
        if shard.get("profile_id") != manifest.get("profile_id"):
            print(f"REFUSED: profile ID mismatch in {shard_name}", file=sys.stderr)
            return 2
        combined["requirements"].extend(shard.get("requirements", []))
    bundle = (load(SOURCE_PATH), load(MAP_PATH), combined, load(CONTRA_PATH), load(PROFILE_PATH))
    try:
        validate_bundle(*bundle)
        if args.selftest:
            selftest(bundle)
    except (OSError, json.JSONDecodeError, Refusal) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(f"PASS: {len(bundle[2]['requirements'])} requirements; {len(bundle[3]['items'])} contradictions; evidence ceiling SOURCE_AND_CONTRACT_CANDIDATE_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
