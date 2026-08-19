#!/usr/bin/env python3
"""Deterministic semantic gate for the Agent Thinking Inception profile."""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import sys
from collections import Counter
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

SOURCE_KEYS = {"schema_version", "subject_id", "source_kind", "locator", "identity", "data_class", "egress_allowed", "captured_at", "content_digest", "claims_not_proven"}
SOURCE_MAP_KEYS = {"schema_version", "source_subject_id", "page_count", "sections", "private_or_ephemeral_locators_excluded"}
MANIFEST_KEYS = {"schema_version", "profile_id", "source_subject_id", "shards", "denominator"}
PROFILE_KEYS = {"schema_version", "profile_id", "source_subject_id", "source_digest", "requirement_document", "contradiction_document", "owner_repositories", "state", "evidence_ceiling", "next_issues"}
REQUIREMENT_KEYS = {"requirement_id", "title", "source_pages", "source_claim", "real_problem", "owner", "state_machine", "inputs", "outputs", "positive_controls", "mutation_controls", "required_evidence_lane", "current_state", "blockers", "next_transition", "claims_not_proven"}
CONTRADICTION_KEYS = {"id", "source_pages", "proposal", "risk", "owner_issue", "required_control"}

EXPECTED_REQUIREMENT_IDS = {
    "REQ-PDF-INCEPTION-STATE-001",
    "REQ-PDF-INCEPTION-DAG-001",
    "REQ-PDF-INCEPTION-CONTEXT-001",
    "REQ-PDF-INCEPTION-CONTEXT-002",
    "REQ-PDF-INCEPTION-CONTEXT-003",
    "REQ-PDF-INCEPTION-STEERING-001",
    "REQ-PDF-INCEPTION-SANDBOX-001",
    "REQ-PDF-INCEPTION-EVIDENCE-001",
    "REQ-PDF-INCEPTION-EVIDENCE-002",
    "REQ-PDF-INCEPTION-COMPLIANCE-001",
    "REQ-PDF-INCEPTION-TELEMETRY-001",
    "REQ-PDF-INCEPTION-CONVERGE-001",
    "REQ-PDF-INCEPTION-INGRESS-001",
    "REQ-PDF-INCEPTION-INGRESS-002",
    "REQ-PDF-INCEPTION-HITL-001",
}
EXPECTED_CONTRADICTION_IDS = {f"UNK-INCEPTION-{index:03d}" for index in range(1, 15)}
EXPECTED_OWNER_REPOSITORIES = {
    "ed3c/enterprise_agent_system",
    "ed3c/skills-shared",
    "ed3c/runtime-env",
    "ed3c/bettor-arena",
    "ed3c/agent-shield-monorepo",
    "ed3c/truth-verify-loop",
    "ed3c/openwiki-source-anchoring",
}
EXPECTED_NEXT_ISSUES = {"#4", "#5", "#7", "#15", "#16", "#17", "#18", "#19"}


class Refusal(ValueError):
    pass


def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def reject_unknown(record: dict[str, Any], allowed: set[str], label: str, errors: list[str]) -> None:
    unknown = sorted(set(record) - allowed)
    if unknown:
        errors.append(f"{label}: unknown fields {unknown}")


def validate_bundle(source: dict[str, Any], source_map: dict[str, Any], requirements: dict[str, Any],
                    contradictions: dict[str, Any], profile: dict[str, Any]) -> None:
    errors: list[str] = []

    reject_unknown(source, SOURCE_KEYS, "source", errors)
    reject_unknown(source_map, SOURCE_MAP_KEYS, "source map", errors)
    reject_unknown(requirements, MANIFEST_KEYS | {"requirements"}, "requirement manifest", errors)
    reject_unknown(profile, PROFILE_KEYS, "profile", errors)

    digest = source.get("content_digest", "")
    if source.get("schema_version") != "enterprise-agent-system/source-subject/v1":
        errors.append("source schema version drift")
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
    if not isinstance(source.get("claims_not_proven"), list) or not source.get("claims_not_proven"):
        errors.append("source claims_not_proven is absent")

    if source_map.get("schema_version") != "enterprise-agent-system/inception-source-map/v1":
        errors.append("source map schema version drift")
    if source_map.get("source_subject_id") != source.get("subject_id"):
        errors.append("source map subject mismatch")
    if source_map.get("page_count") != 26 or not source_map.get("sections"):
        errors.append("page map is incomplete")
    covered_pages: list[int] = []
    for index, section in enumerate(source_map.get("sections", [])):
        if set(section) != {"pages", "topic", "requirement_families"}:
            errors.append(f"source map section {index}: invalid fields")
            continue
        pages = section.get("pages", [])
        if not pages or any(not isinstance(page, int) or page < 1 or page > 26 for page in pages):
            errors.append(f"source map section {index}: invalid pages")
        if not section.get("topic") or not section.get("requirement_families"):
            errors.append(f"source map section {index}: topic/family absent")
        covered_pages.extend(pages)
    if sorted(covered_pages) != list(range(1, 27)):
        errors.append("source map must cover each page exactly once")

    if requirements.get("schema_version") != "enterprise-agent-system/inception-requirements-manifest/v1":
        errors.append("requirement manifest schema version drift")
    if requirements.get("profile_id") != "PROFILE-AGENT-THINKING-INCEPTION-001":
        errors.append("requirement manifest profile mismatch")
    if requirements.get("source_subject_id") != source.get("subject_id"):
        errors.append("requirement manifest source mismatch")

    items = requirements.get("requirements", [])
    if not items:
        errors.append("requirement denominator is empty")
    ids = [item.get("requirement_id") for item in items]
    if len(ids) != len(set(ids)):
        errors.append("duplicate requirement ID")
    if set(ids) != EXPECTED_REQUIREMENT_IDS:
        errors.append("requirement denominator IDs drifted")
    actual_state_counts: Counter[str] = Counter()
    for item in items:
        rid = item.get("requirement_id", "<missing>")
        reject_unknown(item, REQUIREMENT_KEYS, rid, errors)
        if not re.fullmatch(r"REQ-PDF-INCEPTION-[A-Z]+-[0-9]{3}", rid):
            errors.append(f"{rid}: invalid requirement ID")
        pages = item.get("source_pages")
        if not isinstance(pages, list) or not pages or any(not isinstance(p, int) or p < 1 or p > 26 for p in pages):
            errors.append(f"{rid}: missing or invalid page locator")
        owner = item.get("owner", {})
        if set(owner) != {"repository", "directory", "issue"}:
            errors.append(f"{rid}: owner shape is invalid")
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
        current_state = item.get("current_state")
        if current_state not in ALLOWED_STATES:
            errors.append(f"{rid}: invalid or falsely promoted current_state")
        else:
            actual_state_counts[current_state] += 1
        if not item.get("required_evidence_lane") or not item.get("next_transition"):
            errors.append(f"{rid}: evidence lane or next transition is absent")
        combined = " ".join([str(item.get("source_claim", "")), str(item.get("real_problem", ""))]).lower()
        if any(term in combined for term in ABSOLUTE_CLAIMS) and "cannot guarantee" not in combined and "does not prove" not in combined:
            errors.append(f"{rid}: unsupported absolute claim")

    denominator = requirements.get("denominator", {})
    declared_total = denominator.get("total")
    if declared_total != len(items) or declared_total != len(EXPECTED_REQUIREMENT_IDS):
        errors.append("requirement denominator count mismatch")
    state_counts = denominator.get("states", {})
    if state_counts != dict(actual_state_counts):
        errors.append("requirement state denominator mismatch")
    if denominator.get("closure_credit") != 0:
        errors.append("source/profile candidate must have zero closure credit")

    if contradictions.get("schema_version") != "enterprise-agent-system/inception-contradictions/v1":
        errors.append("contradiction schema version drift")
    if contradictions.get("profile_id") != requirements.get("profile_id"):
        errors.append("contradiction profile mismatch")
    citems = contradictions.get("items", [])
    cids = [item.get("id") for item in citems]
    if len(cids) != len(set(cids)):
        errors.append("duplicate contradiction ID")
    if set(cids) != EXPECTED_CONTRADICTION_IDS:
        errors.append("contradiction denominator IDs drifted")
    for item in citems:
        cid = item.get("id", "<missing>")
        reject_unknown(item, CONTRADICTION_KEYS, cid, errors)
        pages = item.get("source_pages", [])
        if not re.fullmatch(r"UNK-INCEPTION-[0-9]{3}", cid):
            errors.append(f"{cid}: invalid contradiction ID")
        if not pages or any(not isinstance(page, int) or page < 1 or page > 26 for page in pages):
            errors.append(f"{cid}: invalid source pages")
        if not item.get("proposal") or not item.get("risk") or not item.get("owner_issue") or not item.get("required_control"):
            errors.append(f"{cid}: incomplete contradiction route")

    if profile.get("schema_version") != "enterprise-agent-system/inception-profile/v1":
        errors.append("profile schema version drift")
    if profile.get("profile_id") != requirements.get("profile_id"):
        errors.append("profile ID mismatch")
    if profile.get("source_subject_id") != source.get("subject_id"):
        errors.append("profile source subject mismatch")
    if profile.get("source_digest") != digest:
        errors.append("profile/source digest mismatch")
    if profile.get("requirement_document") != "profiles/agent-thinking-inception/requirements/requirements.json":
        errors.append("profile requirement document drift")
    if profile.get("contradiction_document") != "profiles/agent-thinking-inception/requirements/contradictions.json":
        errors.append("profile contradiction document drift")
    if profile.get("state") != "PROFILE_CONTRACT_READY":
        errors.append("profile state is not PROFILE_CONTRACT_READY")
    if profile.get("evidence_ceiling") != "SOURCE_AND_CONTRACT_CANDIDATE_ONLY":
        errors.append("profile evidence ceiling widened")
    owners = profile.get("owner_repositories", [])
    if set(owners) != EXPECTED_OWNER_REPOSITORIES or len(owners) != len(EXPECTED_OWNER_REPOSITORIES):
        errors.append("owner repository set drifted")
    next_issues = profile.get("next_issues", [])
    if set(next_issues) != EXPECTED_NEXT_ISSUES or len(next_issues) != len(EXPECTED_NEXT_ISSUES):
        errors.append("profile next issue routes drifted")

    if errors:
        raise Refusal("; ".join(errors))


def selftest(bundle: tuple[dict[str, Any], ...]) -> None:
    mutations: list[tuple[str, Callable[[list[dict[str, Any]]], None]]] = [
        ("duplicate requirement", lambda b: b[2]["requirements"].append(copy.deepcopy(b[2]["requirements"][0]))),
        ("missing denominator item", lambda b: b[2]["requirements"].pop()),
        ("missing page", lambda b: b[2]["requirements"][0].update(source_pages=[])),
        ("missing owner", lambda b: b[2]["requirements"][0]["owner"].update(repository="")),
        ("private locator", lambda b: b[0]["locator"].update(url="https://gemini.google.com/app/private")),
        ("source promoted", lambda b: b[0].update(source_kind="CURRENT_FACT")),
        ("source egress widened", lambda b: b[0].update(data_class="PUBLIC", egress_allowed=True)),
        ("source map gap", lambda b: b[1]["sections"][0].update(pages=[1, 2])),
        ("unknown profile field", lambda b: b[4].update(authority="WIDENED")),
        ("owner repository substitution", lambda b: b[4]["owner_repositories"].__setitem__(0, "ed3c/unbound-owner")),
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
        if set(shard) != {"schema_version", "profile_id", "requirements"}:
            print(f"REFUSED: invalid shard shape in {shard_name}", file=sys.stderr)
            return 2
        if shard.get("schema_version") != "enterprise-agent-system/inception-requirement-shard/v1":
            print(f"REFUSED: schema version mismatch in {shard_name}", file=sys.stderr)
            return 2
        if shard.get("profile_id") != manifest.get("profile_id"):
            print(f"REFUSED: profile ID mismatch in {shard_name}", file=sys.stderr)
            return 2
        combined["requirements"].extend(shard.get("requirements", []))
    bundle = (load(SOURCE_PATH), load(MAP_PATH), combined, load(CONTRA_PATH), load(PROFILE_PATH))
    try:
        validate_bundle(*bundle)
        if args.selftest:
            selftest(bundle)
    except (OSError, json.JSONDecodeError, Refusal, TypeError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(f"PASS: {len(bundle[2]['requirements'])} requirements; {len(bundle[3]['items'])} contradictions; evidence ceiling SOURCE_AND_CONTRACT_CANDIDATE_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
