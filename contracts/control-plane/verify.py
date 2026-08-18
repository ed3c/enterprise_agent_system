#!/usr/bin/env python3
"""Zero-dependency semantic gate for enterprise_agent_system control-plane JSON."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REPO = re.compile(r"^[^/\s]+/[^/\s]+$")
ISSUE = re.compile(r"^https://github\.com/[^/]+/[^/]+/issues/[0-9]+$")
DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
SECRET = re.compile(r"(?i)(PRIVATE KEY|(?:password|secret|token|cookie|session)\s*[:=]\s*\S{6,}|/Users/|/home/|/mnt/data/|gemini\.google\.com/app/)")

VERSIONS = {
    "enterprise-agent-system/source-subject/v1",
    "enterprise-agent-system/cross-repo-binding/v1",
    "enterprise-agent-system/closure-record/v1",
    "enterprise-agent-system/orchestration-run/v1",
}
SOURCE_KINDS = {"SOURCE_PROPOSAL", "CURRENT_FACT", "CONTRACT", "RECEIPT"}
PROVIDERS = {"GITHUB", "GOOGLE_DOC", "GOOGLE_SHEET", "FILE", "OTHER"}
DATA_CLASSES = {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "LOCAL_ONLY"}
OWNER_PLANES = {
    "CONTROL_PLANE",
    "INSTRUCTION_METHOD_PLANE",
    "RUNTIME_CONTRACT_PLANE",
    "WORKFLOW_EFFECT_PLANE",
    "PROVIDER_ADAPTER_PLANE",
    "INDEPENDENT_VERIFICATION_PLANE",
    "HUMAN_RELEASE_PLANE",
}
BINDING_STATES = {
    "UNBOUND",
    "SOURCE_SUBJECT_BOUND",
    "OWNER_PLANE_BOUND",
    "CONTRACT_IDS_BOUND",
    "EVIDENCE_LANES_DECLARED",
    "CLOSURE_RECORD_VALIDATED",
    "CONSUMER_READY",
    "BLOCKED",
}
IMPLEMENTATION_STATES = {"ABSENT", "NOT_IMPLEMENTED", "IMPLEMENTED", "PARTIAL", "PASS"}
LANES = {
    "SOURCE",
    "CONTROL_PLANE",
    "METHOD",
    "RUNTIME_CONTRACT",
    "TRANSPORT",
    "IDENTITY",
    "WORKFLOW",
    "TASK",
    "GATE",
    "EFFECT",
    "ARTIFACT",
    "USER_OUTCOME",
    "SHADOW",
    "HUMAN_ADMIT",
    "RELEASE",
}
EVIDENCE_STATES = {
    "PASS",
    "FAIL",
    "ABSENT",
    "NOT_IMPLEMENTED",
    "NOT_EXERCISED",
    "SKIPPED_BY_POLICY",
    "STALE",
    "BLOCKED",
    "PARTIAL",
    "HUMAN_ADMIT_REQUIRED",
    "RELEASED",
}
BLOCKER_STATES = {"OPEN", "BLOCKED_BY_PREDECESSOR", "HUMAN_ADMIT_REQUIRED"}
TASK_STATES = {"PLANNED", "READY", "ACTIVE", "BLOCKED", "CANDIDATE", "VERIFIED", "COMPLETE"}
REQUIRED_LANES = {"CLOUD", "LOCAL", "PRIVATE", "HUMAN"}
RUN_STATES = {
    "REQUEST_BOUND",
    "SYSTEM_CONTRACT_EXTRACTED",
    "CAPABILITY_DAG_COMPILED",
    "TASK_DAG_COMPILED",
    "PROMPT_PACKETS_EMITTED",
    "WORKERS_ADMITTED",
    "CANDIDATES_RECEIVED",
    "CANONICAL_REDUCTION",
    "GLOBAL_OBJECTIVE_ASSERTED",
    "DELIVERY_HANDOFF",
    "LOCAL_HANDOFF_REQUIRED",
    "BLOCKED",
}


class Refusal(ValueError):
    pass


def req(ok: bool, reason: str) -> None:
    if not ok:
        raise Refusal(reason)


def strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from strings(item)


def shape(value: Any, required: set[str], optional: set[str], name: str) -> dict[str, Any]:
    req(isinstance(value, dict), f"{name}_NOT_OBJECT")
    missing = required - set(value)
    unknown = set(value) - required - optional
    req(not missing and not unknown, f"{name}_FIELDS:missing={sorted(missing)}:unknown={sorted(unknown)}")
    return value


def nonempty_unique_strings(value: Any, name: str) -> list[str]:
    req(isinstance(value, list) and bool(value), f"{name}_EMPTY")
    req(all(isinstance(item, str) and bool(item) for item in value), f"{name}_ITEM")
    req(len(value) == len(set(value)), f"{name}_DUPLICATE")
    return value


def optional_unique_strings(value: Any, name: str) -> list[str]:
    req(isinstance(value, list), f"{name}_NOT_ARRAY")
    req(all(isinstance(item, str) and bool(item) for item in value), f"{name}_ITEM")
    req(len(value) == len(set(value)), f"{name}_DUPLICATE")
    return value


def exact_subject(value: Any, name: str) -> dict[str, Any]:
    subject = shape(value, set(), {"repository", "commit", "tree", "digest"}, name)
    has_git = any(field in subject for field in ("repository", "commit", "tree"))
    has_digest = "digest" in subject
    if has_git:
        req(set(subject) >= {"repository", "commit", "tree"}, f"{name}_INCOMPLETE_GIT")
        req(REPO.fullmatch(str(subject["repository"])) is not None, f"{name}_REPOSITORY")
        req(SHA40.fullmatch(str(subject["commit"])) is not None, f"{name}_COMMIT")
        req(SHA40.fullmatch(str(subject["tree"])) is not None, f"{name}_TREE")
    if has_digest:
        req(SHA256.fullmatch(str(subject["digest"])) is not None, f"{name}_DIGEST")
    req(has_git or has_digest, f"{name}_EMPTY")
    return subject


def source(value: dict[str, Any]) -> None:
    shape(
        value,
        {
            "schema_version",
            "subject_id",
            "source_kind",
            "locator",
            "identity",
            "data_class",
            "egress_allowed",
            "captured_at",
            "content_digest",
            "claims_not_proven",
        },
        set(),
        "SOURCE",
    )
    req(re.fullmatch(r"SRC-[A-Z0-9][A-Z0-9._-]*", str(value["subject_id"])) is not None, "SOURCE_ID")
    req(value["source_kind"] in SOURCE_KINDS, "SOURCE_KIND")
    locator = shape(value["locator"], {"provider", "url"}, {"navigation_ref"}, "SOURCE_LOCATOR")
    req(locator["provider"] in PROVIDERS, "SOURCE_PROVIDER")
    req(isinstance(locator["url"], str) and bool(locator["url"]), "SOURCE_URL")
    if "navigation_ref" in locator:
        req(isinstance(locator["navigation_ref"], str), "SOURCE_NAVIGATION_REF")

    identity = shape(
        value["identity"],
        {"identity_kind"},
        {"repository", "commit", "tree", "revision"},
        "SOURCE_IDENTITY",
    )
    kind = identity["identity_kind"]
    req(kind in {"GIT", "REVISION", "CONTENT_ONLY"}, "IDENTITY_KIND")
    if kind == "GIT":
        req(set(identity) == {"identity_kind", "repository", "commit", "tree"}, "GIT_IDENTITY_FIELDS")
        req(REPO.fullmatch(str(identity["repository"])) is not None, "GIT_REPOSITORY")
        req(SHA40.fullmatch(str(identity["commit"])) is not None, "MUTABLE_SUBJECT")
        req(SHA40.fullmatch(str(identity["tree"])) is not None, "MUTABLE_SUBJECT")
    elif kind == "REVISION":
        req(set(identity) in ({"identity_kind", "revision"}, {"identity_kind", "repository", "revision"}), "REVISION_IDENTITY_FIELDS")
        req(isinstance(identity["revision"], str) and bool(identity["revision"]), "REVISION_ABSENT")
        if "repository" in identity:
            req(REPO.fullmatch(str(identity["repository"])) is not None, "REVISION_REPOSITORY")
    else:
        req(set(identity) == {"identity_kind"}, "CONTENT_ONLY_IDENTITY_FIELDS")

    req(value["data_class"] in DATA_CLASSES, "DATA_CLASS")
    req(isinstance(value["egress_allowed"], bool), "EGRESS_ALLOWED_TYPE")
    if value["data_class"] == "LOCAL_ONLY":
        req(value["egress_allowed"] is False, "LOCAL_ONLY_REMOTE_EGRESS")
    req(DATETIME.fullmatch(str(value["captured_at"])) is not None, "CAPTURED_AT")
    req(SHA256.fullmatch(str(value["content_digest"])) is not None, "CONTENT_DIGEST")
    nonempty_unique_strings(value["claims_not_proven"], "CLAIMS_NOT_PROVEN")


def binding(value: dict[str, Any]) -> None:
    shape(
        value,
        {"schema_version", "binding_id", "source_subject_id", "owner", "interfaces", "consumers", "state", "claims_not_proven"},
        set(),
        "BINDING",
    )
    req(re.fullmatch(r"BIND-[A-Z0-9][A-Z0-9._-]*", str(value["binding_id"])) is not None, "BINDING_ID")
    req(str(value["source_subject_id"]).startswith("SRC-"), "BINDING_SOURCE_ID")
    owner = shape(value["owner"], {"plane", "repository"}, {"directory"}, "BINDING_OWNER")
    req(owner["plane"] in OWNER_PLANES, "OWNER_PLANE")
    req(REPO.fullmatch(str(owner["repository"])) is not None, "OWNER_REPOSITORY")
    if "directory" in owner:
        req(isinstance(owner["directory"], str) and bool(owner["directory"]), "OWNER_DIRECTORY")

    interfaces = value["interfaces"]
    req(isinstance(interfaces, list) and bool(interfaces), "INTERFACES_EMPTY")
    seen: set[str] = set()
    for index, raw in enumerate(interfaces):
        item = shape(raw, {"interface_id", "owner_repository", "implementation_state", "digest"}, set(), f"INTERFACE_{index}")
        interface_id = str(item["interface_id"])
        req(bool(interface_id), f"INTERFACE_ID:{index}")
        req(interface_id not in seen, f"DUPLICATE_INTERFACE:{interface_id}")
        seen.add(interface_id)
        repository = str(item["owner_repository"])
        req(REPO.fullmatch(repository) is not None, f"INTERFACE_OWNER:{interface_id}")
        state = item["implementation_state"]
        req(state in IMPLEMENTATION_STATES, f"IMPLEMENTATION_STATE:{interface_id}")
        digest = item["digest"]
        if state in {"IMPLEMENTED", "PASS"}:
            req(isinstance(digest, str) and SHA256.fullmatch(digest) is not None, f"IMPLEMENTED_WITHOUT_DIGEST:{interface_id}")
        else:
            req(digest is None or (isinstance(digest, str) and SHA256.fullmatch(digest) is not None), f"INTERFACE_DIGEST:{interface_id}")
        if interface_id.startswith("runtime-env/dual-agent/"):
            req(repository == "ed3c/runtime-env", f"DUPLICATE_RUNTIME_SCHEMA_AUTHORITY:{interface_id}")

    consumers = nonempty_unique_strings(value["consumers"], "CONSUMERS")
    req(all(REPO.fullmatch(item) is not None for item in consumers), "CONSUMER_REPOSITORY")
    req(value["state"] in BINDING_STATES, "BINDING_STATE")
    nonempty_unique_strings(value["claims_not_proven"], "CLAIMS_NOT_PROVEN")


def closure(value: dict[str, Any]) -> None:
    shape(
        value,
        {
            "schema_version",
            "problem_id",
            "source_subject_id",
            "owner",
            "state_machine",
            "evidence",
            "blockers",
            "next_transition",
            "human_owned",
            "claims_not_proven",
        },
        set(),
        "CLOSURE",
    )
    req(re.fullmatch(r"PROB-[A-Z0-9][A-Z0-9._-]*", str(value["problem_id"])) is not None, "PROBLEM_ID")
    req(str(value["source_subject_id"]).startswith("SRC-"), "CLOSURE_SOURCE_ID")
    owner = shape(value["owner"], {"repository", "directory", "issue"}, set(), "CLOSURE_OWNER")
    req(REPO.fullmatch(str(owner["repository"])) is not None, "OWNER_REPOSITORY")
    req(isinstance(owner["directory"], str) and bool(owner["directory"]), "OWNER_DIRECTORY")
    req(ISSUE.fullmatch(str(owner["issue"])) is not None, "OWNER_ISSUE")
    state_machine = shape(value["state_machine"], {"current", "next"}, set(), "STATE_MACHINE")
    req(all(isinstance(state_machine[key], str) and bool(state_machine[key]) for key in ("current", "next")), "STATE_MACHINE_VALUE")

    evidence = value["evidence"]
    req(isinstance(evidence, list) and bool(evidence), "EVIDENCE_EMPTY")
    lane_records: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(evidence):
        item = shape(raw, {"lane", "required_lane", "state", "subject", "claims_not_proven"}, set(), f"EVIDENCE_{index}")
        lane = item["lane"]
        required_lane = item["required_lane"]
        state = item["state"]
        req(lane in LANES and required_lane in LANES, f"INVALID_EVIDENCE_LANE:{lane}:{required_lane}")
        req(lane == required_lane, f"LANE_SUBSTITUTION:{lane}->{required_lane}")
        req(lane not in lane_records, f"DUPLICATE_EVIDENCE_LANE:{lane}")
        req(state in EVIDENCE_STATES, f"INVALID_EVIDENCE_STATE:{state}")
        subject = item["subject"]
        if state in {"PASS", "RELEASED"}:
            exact_subject(subject, f"PASS_SUBJECT:{lane}")
        elif subject is not None:
            exact_subject(subject, f"EVIDENCE_SUBJECT:{lane}")
        nonempty_unique_strings(item["claims_not_proven"], f"EVIDENCE_CLAIMS:{lane}")
        lane_records[lane] = item

    release = lane_records.get("RELEASE")
    if release and release["state"] in {"PASS", "RELEASED"}:
        human = lane_records.get("HUMAN_ADMIT")
        req(human is not None and human["state"] in {"PASS", "RELEASED"}, "RELEASE_WITHOUT_HUMAN_ADMIT")
        exact_subject(human["subject"], "HUMAN_ADMIT_SUBJECT")

    blockers = value["blockers"]
    req(isinstance(blockers, list), "BLOCKERS_NOT_ARRAY")
    blocker_ids: set[str] = set()
    for index, raw in enumerate(blockers):
        item = shape(raw, {"id", "owner_issue", "state"}, set(), f"BLOCKER_{index}")
        blocker_id = str(item["id"])
        req(bool(blocker_id) and blocker_id not in blocker_ids, f"DUPLICATE_OR_EMPTY_BLOCKER:{blocker_id}")
        blocker_ids.add(blocker_id)
        req(ISSUE.fullmatch(str(item["owner_issue"])) is not None, f"BLOCKER_WITHOUT_OWNER:{blocker_id}")
        req(item["state"] in BLOCKER_STATES, f"BLOCKER_STATE:{blocker_id}")
    req(isinstance(value["next_transition"], str) and bool(value["next_transition"]), "NEXT_TRANSITION_EMPTY")
    human_owned = nonempty_unique_strings(value["human_owned"], "HUMAN_BOUNDARY")
    for operation in {"merge", "release", "rollback"}:
        req(operation in human_owned, f"HUMAN_BOUNDARY_MISSING:{operation}")
    nonempty_unique_strings(value["claims_not_proven"], "CLAIMS_NOT_PROVEN")


def prefix(path: str) -> str:
    return path.split("*", 1)[0].rstrip("/")


def overlap(left: str, right: str) -> bool:
    a, b = prefix(left), prefix(right)
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def assert_acyclic(ids: set[str], graph: dict[str, set[str]], label: str) -> None:
    remaining = {task_id: set(dependencies) for task_id, dependencies in graph.items()}
    req(set(remaining) == ids, f"{label}_TASK_SET")
    while remaining:
        ready = {task_id for task_id, dependencies in remaining.items() if not dependencies}
        req(bool(ready), f"CYCLIC_{label}")
        for task_id in ready:
            remaining.pop(task_id)
        for dependencies in remaining.values():
            dependencies.difference_update(ready)


def orchestration(value: dict[str, Any]) -> None:
    shape(
        value,
        {"schema_version", "run_id", "request_subject", "tasks", "leases", "canonical_reducer", "shadow", "authority", "state"},
        set(),
        "ORCHESTRATION",
    )
    req(re.fullmatch(r"RUN-[A-Z0-9][A-Z0-9._-]*", str(value["run_id"])) is not None, "RUN_ID")
    request_subject = shape(value["request_subject"], {"repository", "commit", "tree"}, set(), "REQUEST_SUBJECT")
    req(REPO.fullmatch(str(request_subject["repository"])) is not None, "REQUEST_REPOSITORY")
    req(SHA40.fullmatch(str(request_subject["commit"])) is not None, "MUTABLE_SUBJECT")
    req(SHA40.fullmatch(str(request_subject["tree"])) is not None, "MUTABLE_SUBJECT")

    tasks = value["tasks"]
    req(isinstance(tasks, list) and bool(tasks), "TASKS_EMPTY")
    ids = [str(item.get("id", "")) if isinstance(item, dict) else "" for item in tasks]
    idset = set(ids)
    req(len(ids) == len(idset), "DUPLICATE_TASK")
    start_graph: dict[str, set[str]] = {}
    completion_graph: dict[str, set[str]] = {}
    task_records: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(tasks):
        task = shape(
            raw,
            {"id", "start_dependencies", "completion_dependencies", "owns_paths", "required_lane", "output_contract", "state"},
            set(),
            f"TASK_{index}",
        )
        task_id = str(task["id"])
        req(re.fullmatch(r"TASK-[A-Z0-9][A-Z0-9._-]*", task_id) is not None, f"TASK_ID:{task_id}")
        start = set(optional_unique_strings(task["start_dependencies"], f"START_DEPENDENCIES:{task_id}"))
        completion = set(optional_unique_strings(task["completion_dependencies"], f"COMPLETION_DEPENDENCIES:{task_id}"))
        req(completion.issubset(start), f"COMPLETION_EDGE_WITHOUT_START_EDGE:{task_id}")
        for dependency in start | completion:
            req(dependency in idset and dependency != task_id, f"UNKNOWN_OR_SELF_DEPENDENCY:{task_id}:{dependency}")
        nonempty_unique_strings(task["owns_paths"], f"OWNS_PATHS:{task_id}")
        req(task["required_lane"] in REQUIRED_LANES, f"REQUIRED_LANE:{task_id}")
        req(isinstance(task["output_contract"], str) and bool(task["output_contract"]), f"OUTPUT_CONTRACT:{task_id}")
        req(task["state"] in TASK_STATES, f"TASK_STATE:{task_id}")
        start_graph[task_id] = start
        completion_graph[task_id] = completion
        task_records[task_id] = task
    assert_acyclic(idset, start_graph, "START_DAG")
    assert_acyclic(idset, completion_graph, "COMPLETION_DAG")

    raw_leases = value["leases"]
    req(isinstance(raw_leases, list) and bool(raw_leases), "LEASES_EMPTY")
    leases: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(raw_leases):
        lease = shape(raw, {"task_id", "writer_id", "paths", "resources"}, set(), f"LEASE_{index}")
        task_id = str(lease["task_id"])
        req(task_id in idset and task_id not in leases, f"DUPLICATE_OR_UNKNOWN_LEASE:{task_id}")
        req(isinstance(lease["writer_id"], str) and bool(lease["writer_id"]), f"WRITER_ID:{task_id}")
        paths = nonempty_unique_strings(lease["paths"], f"LEASE_PATHS:{task_id}")
        optional_unique_strings(lease["resources"], f"LEASE_RESOURCES:{task_id}")
        req(set(paths) == set(task_records[task_id]["owns_paths"]), f"TASK_LEASE_PATH_MISMATCH:{task_id}")
        leases[task_id] = lease
    req(set(leases) == idset, "TASK_LEASE_MISMATCH")

    active = [task for task in tasks if task["state"] in {"READY", "ACTIVE", "CANDIDATE"}]
    for index, left in enumerate(active):
        for right in active[index + 1 :]:
            for left_path in leases[left["id"]]["paths"]:
                for right_path in leases[right["id"]]["paths"]:
                    req(not overlap(left_path, right_path), f"OVERLAPPING_PATH_LEASE:{left['id']}:{right['id']}")
            req(
                set(leases[left["id"]]["resources"]).isdisjoint(leases[right["id"]]["resources"]),
                f"OVERLAPPING_RESOURCE_LEASE:{left['id']}:{right['id']}",
            )

    reducer = shape(value["canonical_reducer"], {"owner", "may_commit"}, set(), "CANONICAL_REDUCER")
    req(isinstance(reducer["owner"], str) and bool(reducer["owner"]), "REDUCER_OWNER")
    req(reducer["may_commit"] == ["TASK_STATE"], "REDUCER_AUTHORITY_WIDENED")
    shadow = shape(value["shadow"], {"read_only", "separate_evaluation_path", "may_commit"}, set(), "SHADOW")
    req(shadow["read_only"] is True and shadow["separate_evaluation_path"] is True, "SHADOW_NOT_INDEPENDENT")
    req(shadow["may_commit"] == [], "SHADOW_SECOND_STATE_WRITER")
    authority = shape(value["authority"], {"automation_forbidden", "human_owned"}, set(), "AUTHORITY")
    forbidden = set(nonempty_unique_strings(authority["automation_forbidden"], "AUTOMATION_FORBIDDEN"))
    human_owned = set(nonempty_unique_strings(authority["human_owned"], "AUTHORITY_HUMAN_OWNED"))
    for operation in {"merge", "permission_change", "semantic_conflict_resolution", "release", "rollback"}:
        req(operation in forbidden, f"AUTOMATION_AUTHORITY_WIDENED:{operation}")
    for operation in {"merge", "release", "rollback"}:
        req(operation in human_owned, f"HUMAN_AUTHORITY_MISSING:{operation}")
    req(value["state"] in RUN_STATES, "RUN_STATE")


def validate(value: dict[str, Any]) -> None:
    req(not any(SECRET.search(item) for item in strings(value)), "SECRET_SESSION_OR_HOST_PATH")
    version = value.get("schema_version")
    req(version in VERSIONS, f"UNKNOWN_SCHEMA_VERSION:{version}")
    validators: dict[str, Callable[[dict[str, Any]], None]] = {
        "enterprise-agent-system/source-subject/v1": source,
        "enterprise-agent-system/cross-repo-binding/v1": binding,
        "enterprise-agent-system/closure-record/v1": closure,
        "enterprise-agent-system/orchestration-run/v1": orchestration,
    }
    validators[version](value)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    req(isinstance(value, dict), f"ROOT_NOT_OBJECT:{path}")
    return value


def selftest(directory: Path) -> None:
    names = [
        "source-subject.example.json",
        "cross-repo-binding.example.json",
        "closure-record.example.json",
        "orchestration-run.example.json",
    ]
    values = {name: load(directory / name) for name in names}
    for value in values.values():
        validate(value)

    mutations: list[tuple[str, str, Callable[[dict[str, Any]], Any]]] = [
        ("LOCAL_ONLY_REMOTE_EGRESS", "source-subject.example.json", lambda value: value.update(data_class="LOCAL_ONLY", egress_allowed=True)),
        ("SOURCE_LOCATOR_FIELDS", "source-subject.example.json", lambda value: value["locator"].update(session_id="private")),
        ("CONTENT_ONLY_IDENTITY_FIELDS", "source-subject.example.json", lambda value: value["identity"].update(repository="ed3c/example")),
        ("DUPLICATE_RUNTIME_SCHEMA_AUTHORITY", "cross-repo-binding.example.json", lambda value: value["interfaces"][2].update(owner_repository="ed3c/enterprise_agent_system")),
        ("IMPLEMENTED_WITHOUT_DIGEST", "cross-repo-binding.example.json", lambda value: value["interfaces"][0].update(implementation_state="IMPLEMENTED", digest=None)),
        ("INTERFACE_0_FIELDS", "cross-repo-binding.example.json", lambda value: value["interfaces"][0].update(extra="no")),
        ("LANE_SUBSTITUTION", "closure-record.example.json", lambda value: value["evidence"][3].update(required_lane="TASK")),
        ("PASS_SUBJECT:SOURCE_EMPTY", "closure-record.example.json", lambda value: value["evidence"][0].update(subject={})),
        ("EVIDENCE_0_FIELDS", "closure-record.example.json", lambda value: value["evidence"][0].update(extra="no")),
        ("EVIDENCE_CLAIMS:SOURCE_EMPTY", "closure-record.example.json", lambda value: value["evidence"][0].update(claims_not_proven=[])),
        ("BLOCKER_WITHOUT_OWNER", "closure-record.example.json", lambda value: value["blockers"][0].update(owner_issue="missing")),
        ("RELEASE_WITHOUT_HUMAN_ADMIT", "closure-record.example.json", lambda value: value["evidence"].append({"lane": "RELEASE", "required_lane": "RELEASE", "state": "RELEASED", "subject": {"digest": "sha256:" + "a" * 64}, "claims_not_proven": ["rollback"]})),
        ("MUTABLE_SUBJECT", "orchestration-run.example.json", lambda value: value["request_subject"].update(commit="main")),
        ("REQUEST_SUBJECT_FIELDS", "orchestration-run.example.json", lambda value: value["request_subject"].update(branch="main")),
        ("COMPLETION_EDGE_WITHOUT_START_EDGE", "orchestration-run.example.json", lambda value: value["tasks"][1].update(start_dependencies=[])),
        ("CYCLIC_START_DAG", "orchestration-run.example.json", lambda value: (value["tasks"][0].update(start_dependencies=[value["tasks"][1]["id"]]), value["tasks"][1].update(start_dependencies=[value["tasks"][0]["id"]], completion_dependencies=[]))),
        ("TASK_0_FIELDS", "orchestration-run.example.json", lambda value: value["tasks"][0].update(extra="no")),
        ("LEASE_0_FIELDS", "orchestration-run.example.json", lambda value: value["leases"][0].update(extra="no")),
        ("TASK_LEASE_PATH_MISMATCH", "orchestration-run.example.json", lambda value: value["leases"][0].update(paths=["wrong/**"])),
        ("OVERLAPPING_PATH_LEASE", "orchestration-run.example.json", lambda value: (value["tasks"][1].update(state="ACTIVE"), value["leases"][1].update(paths=value["tasks"][1]["owns_paths"] := ["contracts/control-plane/new/**"]))),
        ("CANONICAL_REDUCER_FIELDS", "orchestration-run.example.json", lambda value: value["canonical_reducer"].update(extra="no")),
        ("SHADOW_SECOND_STATE_WRITER", "orchestration-run.example.json", lambda value: value["shadow"].update(may_commit=["TASK_STATE"])),
        ("AUTHORITY_FIELDS", "orchestration-run.example.json", lambda value: value["authority"].update(extra="no")),
        ("SECRET_SESSION_OR_HOST_PATH", "source-subject.example.json", lambda value: value["locator"].update(navigation_ref="token=abcdef123456")),
    ]
    for expected, name, mutate in mutations:
        value = copy.deepcopy(values[name])
        mutate(value)
        try:
            validate(value)
        except Refusal as exc:
            req(expected in str(exc), f"WRONG_REFUSAL:{expected}:{exc}")
        else:
            raise Refusal(f"MUTATION_DID_NOT_FAIL:{expected}")
    print(f"PASS positives={len(values)} mutations={len(mutations)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--selftest", type=Path)
    args = parser.parse_args()
    try:
        if args.selftest:
            selftest(args.selftest)
        for path in args.paths:
            validate(load(path))
    except (OSError, json.JSONDecodeError, Refusal, TypeError, KeyError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2
    if args.paths:
        print(f"PASS validated={len(args.paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
