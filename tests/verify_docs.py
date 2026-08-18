#!/usr/bin/env python3
"""Deterministic consistency gate for the EAS-D architecture and traceability packet."""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLANS = ROOT / "plans"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
ISSUE = re.compile(r"^#[0-9]+(?:/#[0-9]+)?$")
SECRET = re.compile(r"(?i)(PRIVATE KEY|(?:password|secret|token|cookie|session)\s*[:=]\s*\S{6,}|/Users/|/home/|/mnt/data/|gemini\.google\.com/app/)")
TASK_STATES = {"PLANNED", "BLOCKED", "CANDIDATE", "NOT_IMPLEMENTED", "NOT_EXECUTED"}
CLOSURE_STATES = {"CANDIDATE", "BLOCKED", "BLOCKED_FOR_CLOSURE", "NOT_IMPLEMENTED", "NOT_EXECUTED", "NOT_EXERCISED", "NOT_PERFORMED"}


class Refusal(ValueError):
    pass


def req(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    req(isinstance(value, dict), f"ROOT_NOT_OBJECT:{path}")
    return value


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


def prefix(path: str) -> str:
    return path.split("*", 1)[0].rstrip("/")


def overlap(left: str, right: str) -> bool:
    a, b = prefix(left), prefix(right)
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def assert_acyclic(ids: set[str], dependencies: dict[str, set[str]], label: str) -> None:
    remaining = {key: set(value) for key, value in dependencies.items()}
    while remaining:
        ready = {key for key, deps in remaining.items() if not deps}
        req(bool(ready), f"CYCLIC_{label}")
        for key in ready:
            remaining.pop(key)
        for deps in remaining.values():
            deps.difference_update(ready)
    req(set(dependencies) == ids, f"{label}_TASK_SET_MISMATCH")


def validate_task_dag(value: dict[str, Any]) -> None:
    req(value.get("schema_version") == "enterprise-agent-system/task-dag/v1", "TASK_DAG_SCHEMA")
    req(value.get("plan_id") == "PLAN-EAS-INCEPTION-2026-08-18", "TASK_DAG_ID")
    subjects = value.get("source_subjects", [])
    req({item.get("id") for item in subjects} == {"EAS-C", "EAS-K", "EAS-E", "INCEPTION-C0-C1"}, "TASK_DAG_SOURCE_SUBJECTS")
    for item in subjects:
        if item.get("commit") is not None:
            req(SHA40.fullmatch(item["commit"]) is not None, f"TASK_DAG_MUTABLE_COMMIT:{item.get('id')}")
        if item.get("tree") is not None:
            req(SHA40.fullmatch(item["tree"]) is not None, f"TASK_DAG_MUTABLE_TREE:{item.get('id')}")
        if item.get("source_digest") is not None:
            req(SHA256.fullmatch(item["source_digest"]) is not None, f"TASK_DAG_BAD_DIGEST:{item.get('id')}")

    tasks = value.get("tasks", [])
    ids = [task.get("id") for task in tasks]
    idset = set(ids)
    req(len(ids) == len(idset) and len(ids) >= 18, "TASK_DAG_DUPLICATE_OR_INCOMPLETE")
    phase_text = " ".join(str(task.get("phase", "")) for task in tasks)
    for phase in ("P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"):
        req(phase in phase_text, f"MISSING_PHASE:{phase}")
    start_graph: dict[str, set[str]] = {}
    completion_graph: dict[str, set[str]] = {}
    active = []
    for task in tasks:
        task_id = task.get("id", "")
        req(re.fullmatch(r"TASK-[A-Z0-9-]+", task_id) is not None, f"TASK_ID:{task_id}")
        req(ISSUE.fullmatch(str(task.get("issue", ""))) is not None, f"TASK_ISSUE:{task_id}")
        req(task.get("state") in TASK_STATES, f"TASK_STATE:{task_id}")
        req(task.get("required_lane") in {"CLOUD", "LOCAL", "HUMAN"}, f"TASK_LANE:{task_id}")
        req(task.get("owns_paths") and len(task["owns_paths"]) == len(set(task["owns_paths"])), f"TASK_PATHS:{task_id}")
        req(bool(task.get("next_transition")), f"TASK_NEXT:{task_id}")
        start = set(task.get("start_dependencies", []))
        completion = set(task.get("completion_dependencies", []))
        req(completion.issubset(start), f"COMPLETION_WITHOUT_START:{task_id}")
        for dependency in start | completion:
            req(dependency in idset and dependency != task_id, f"UNKNOWN_OR_SELF_DEPENDENCY:{task_id}:{dependency}")
        start_graph[task_id] = start
        completion_graph[task_id] = completion
        if task["state"] == "CANDIDATE":
            active.append(task)
    assert_acyclic(idset, start_graph, "START_DAG")
    assert_acyclic(idset, completion_graph, "COMPLETION_DAG")
    for index, left in enumerate(active):
        for right in active[index + 1 :]:
            for left_path in left["owns_paths"]:
                for right_path in right["owns_paths"]:
                    req(not overlap(left_path, right_path), f"ACTIVE_PATH_OVERLAP:{left['id']}:{right['id']}")
    req(value.get("evidence_ceiling") == "PROGRAM_PLAN_CANDIDATE_ONLY", "TASK_DAG_EVIDENCE_WIDENED")
    req(value.get("claims_not_proven"), "TASK_DAG_CLAIMS_EMPTY")


def validate_stack(value: dict[str, Any]) -> None:
    req(value.get("schema_version") == "enterprise-agent-system/molecular-stack-index/v1", "STACK_SCHEMA")
    req(set(value.get("required_atom_classes", [])) == {"C", "K", "A", "E", "X", "D"}, "STACK_REQUIRED_CLASSES")
    atoms = value.get("atoms", [])
    ids = [atom.get("atom_id") for atom in atoms]
    idset = set(ids)
    req(len(ids) == len(idset) and len(ids) >= 17, "STACK_DUPLICATE_OR_INCOMPLETE")
    req({atom.get("class") for atom in atoms} >= {"C", "K", "A", "E", "X", "D"}, "STACK_CLASS_COVERAGE")
    for atom in atoms:
        atom_id = atom.get("atom_id", "")
        req(atom.get("owns_paths") and atom.get("oracle") and atom.get("next_authority"), f"CEREMONIAL_ATOM:{atom_id}")
        req(ISSUE.fullmatch(str(atom.get("issue", ""))) is not None, f"STACK_ISSUE:{atom_id}")
        for dependency in atom.get("git_parents", []) + atom.get("process_dependencies", []):
            req(dependency in idset and dependency != atom_id, f"STACK_DEPENDENCY:{atom_id}:{dependency}")
        if atom.get("kind") in {"true-child", "read-only-child"}:
            req(atom.get("git_parents"), f"TRUE_CHILD_WITHOUT_PARENT:{atom_id}")
        subject = atom.get("subject")
        if subject:
            if "commit" in subject:
                req(SHA40.fullmatch(subject["commit"]) is not None, f"STACK_MUTABLE_COMMIT:{atom_id}")
            if "tree" in subject:
                req(SHA40.fullmatch(subject["tree"]) is not None, f"STACK_MUTABLE_TREE:{atom_id}")
            if "digest" in subject:
                req(SHA256.fullmatch(subject["digest"]) is not None, f"STACK_BAD_DIGEST:{atom_id}")
        if atom.get("pull_request") is not None:
            req(isinstance(atom["pull_request"], int) and atom["pull_request"] > 0, f"STACK_PR:{atom_id}")
        if atom.get("class") == "E":
            req("INDEPENDENT" in atom.get("required_lane", "") or "EVALUATOR" in atom.get("oracle", "").upper(), f"SHADOW_NOT_INDEPENDENT:{atom_id}")
    req(value.get("evidence_ceiling") == "STACK_TOPOLOGY_CANDIDATE_ONLY", "STACK_EVIDENCE_WIDENED")


def validate_directory_index(value: dict[str, Any]) -> None:
    req(value.get("schema_version") == "enterprise-agent-system/directory-state-machine-index/v1", "DIRECTORY_SCHEMA")
    entries = value.get("directories", [])
    paths = [entry.get("path") for entry in entries]
    req(len(paths) == len(set(paths)) and len(paths) >= 18, "DIRECTORY_DUPLICATE_OR_INCOMPLETE")
    expected = {
        "contracts/control-plane/**",
        "src/enterprise_agent_system/**",
        "integrations/**",
        "profiles/agent-thinking-inception/source/**",
        "profiles/agent-thinking-inception/requirements/**",
        "profiles/agent-thinking-inception/contracts/**",
        "profiles/agent-thinking-inception/orchestration/**",
        "profiles/agent-thinking-inception/owners/compaction/**",
        "profiles/agent-thinking-inception/owners/runtime/**",
        "profiles/agent-thinking-inception/owners/evidence/**",
        "profiles/agent-thinking-inception/owners/compliance/**",
        "profiles/agent-thinking-inception/owners/discovery/**",
        "profiles/agent-thinking-inception/owners/ingress/**",
        "handoff/**",
    }
    req(expected.issubset(set(paths)), "DIRECTORY_EXPECTED_ROUTES")
    for entry in entries:
        label = entry.get("path", "")
        req(entry.get("owner_atom"), f"DIRECTORY_OWNER:{label}")
        req("→" in str(entry.get("state_machine", "")), f"DIRECTORY_STATE_MACHINE:{label}")
        req(entry.get("inputs") and entry.get("outputs"), f"DIRECTORY_IO:{label}")
        req(entry.get("positive_gate") and entry.get("mutation_gate"), f"DIRECTORY_GATES:{label}")
        req(entry.get("next_owner") and entry.get("evidence_ceiling"), f"DIRECTORY_NEXT_OR_CEILING:{label}")
    req(value.get("evidence_ceiling") == "DIRECTORY_ROUTING_CANDIDATE_ONLY", "DIRECTORY_EVIDENCE_WIDENED")


def validate_data_flow(value: dict[str, Any]) -> None:
    req(value.get("schema_version") == "enterprise-agent-system/data-flow/v1", "FLOW_SCHEMA")
    nodes = value.get("nodes", [])
    ids = [node.get("id") for node in nodes]
    idset = set(ids)
    req(len(ids) == len(idset) and len(ids) >= 25, "FLOW_DUPLICATE_OR_INCOMPLETE")
    required = {"SOURCE", "SOURCE_REGISTRY", "TECH_LEAD", "OWNER_WORKERS", "SHADOW_VERIFY", "CLOSURE_REDUCER", "LOCAL_HANDOFF", "HUMAN_POLICY", "DURABLE_INBOX", "DOMAIN_STATE", "MACRO_DAG", "SANDBOX_AGENT", "EFFECT_LEDGER", "REMOTE_READBACK", "TELEMETRY_SANITIZER"}
    req(required.issubset(idset), "FLOW_REQUIRED_NODES")
    for node in nodes:
        req(node.get("owner") and node.get("authority") and node.get("data_classes"), f"FLOW_NODE:{node.get('id')}")
    edges = value.get("edges", [])
    req(len(edges) >= 25, "FLOW_EDGE_DENOMINATOR")
    for edge in edges:
        req(edge.get("from") in idset and edge.get("to") in idset, f"FLOW_UNKNOWN_NODE:{edge}")
        req(edge.get("payload") and edge.get("guard"), f"FLOW_UNGUARDED_EDGE:{edge}")
    forbidden = value.get("forbidden_flows", [])
    req(len(forbidden) >= 7 and any("unknown external effect" in item for item in forbidden), "FLOW_FORBIDDEN_DENOMINATOR")
    req(value.get("evidence_ceiling") == "DATA_FLOW_CONTRACT_CANDIDATE_ONLY", "FLOW_EVIDENCE_WIDENED")


def validate_closure(value: dict[str, Any]) -> None:
    req(value.get("schema_version") == "enterprise-agent-system/architecture-closure/v1", "CLOSURE_SCHEMA")
    req(value.get("denominator") == {"requirements": 15, "contradictions": 14, "closure_credit": 0}, "CLOSURE_DENOMINATOR")
    planes = value.get("planes", [])
    names = [plane.get("plane") for plane in planes]
    req(len(names) == len(set(names)) and len(names) >= 20, "CLOSURE_PLANES")
    for plane in planes:
        req(plane.get("state") in CLOSURE_STATES, f"CLOSURE_STATE:{plane.get('plane')}")
        req(plane.get("blockers") and plane.get("next_transition"), f"CLOSURE_ROUTE:{plane.get('plane')}")
    by_name = {plane["plane"]: plane for plane in planes}
    req(by_name["HUMAN_ADMIT"]["state"] == "NOT_PERFORMED", "HUMAN_FALSE_PROMOTION")
    req(by_name["RELEASE"]["state"] == "NOT_PERFORMED", "RELEASE_FALSE_PROMOTION")
    req(by_name["OPERATED_WITH_ROLLBACK"]["state"] == "NOT_EXERCISED", "ROLLBACK_FALSE_PROMOTION")
    req(value.get("human_owned") and value.get("claims_not_proven"), "CLOSURE_BOUNDARY_EMPTY")
    req(value.get("evidence_ceiling") == "CLOSURE_PROJECTION_CANDIDATE_ONLY", "CLOSURE_EVIDENCE_WIDENED")


def validate_docs() -> None:
    required_paths = [
        "README.md", "AGENTS.md", "ARCHITECTURE.md", "CONTEXT.md",
        "docs/INDEX.md", "docs/architecture/STATE_MACHINES.md", "docs/architecture/DATA_FLOW.md",
        "docs/traceability/MOLECULAR_STACK_INDEX.md", "handoff/README.md", "prompts/README.md",
    ] + [f"prompts/{index:02d}-{name}.system.md" for index, name in [
        (0, "source-authority-auditor"), (1, "contract-lock-worker"), (2, "tech-lead-controller"),
        (3, "owner-wave-worker"), (4, "shadow-architect"), (5, "convergence-owner"),
        (6, "docs-stack-convergence"), (7, "local-handoff-compiler"),
    ]]
    for path in required_paths:
        req((ROOT / path).is_file(), f"DOC_PATH_ABSENT:{path}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    context = (ROOT / "CONTEXT.md").read_text(encoding="utf-8")
    stack_doc = (ROOT / "docs/traceability/MOLECULAR_STACK_INDEX.md").read_text(encoding="utf-8")
    combined = readme + context + stack_doc
    for phase in ("P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"):
        req(phase in readme, f"README_PHASE:{phase}")
    for repository in ("enterprise_agent_system", "skills-shared", "runtime-env", "bettor-arena", "agent-shield-monorepo", "truth-verify-loop", "openwiki-source-anchoring"):
        req(repository in readme, f"README_OWNER:{repository}")
    req("60f994f5f9da55168911d19fb32489775a5f4599" in context, "CURRENT_PROFILE_HEAD_ABSENT")
    req("869665f5c5fafd556fcc1289668d94ec3f804ce9" in context + stack_doc, "SYNC_COMMIT_ABSENT")
    req("STALE_PARENT_PIN" not in combined and "stale parent pin" not in combined.lower() and "stale-parent blueprint" not in combined.lower(), "STALE_DOCS_STATUS")
    req(not any(SECRET.search(text) for text in strings(combined)), "SECRET_OR_PRIVATE_LOCATOR_IN_DOCS")


def load_bundle() -> dict[str, dict[str, Any]]:
    return {
        "task": load(PLANS / "task-dag.json"),
        "stack": load(PLANS / "molecular-stack-index.json"),
        "directories": load(PLANS / "directory-state-machine-index.json"),
        "flow": load(PLANS / "data-flow.json"),
        "closure": load(PLANS / "architecture-closure.json"),
    }


def validate_bundle(bundle: dict[str, dict[str, Any]], check_files: bool = True) -> None:
    req(not any(SECRET.search(text) for text in strings(bundle)), "SECRET_SESSION_OR_HOST_PATH")
    validate_task_dag(bundle["task"])
    validate_stack(bundle["stack"])
    validate_directory_index(bundle["directories"])
    validate_data_flow(bundle["flow"])
    validate_closure(bundle["closure"])
    if check_files:
        validate_docs()


def selftest(bundle: dict[str, dict[str, Any]]) -> None:
    mutations = [
        ("CYCLIC_START_DAG", lambda b: b["task"]["tasks"][0].update(start_dependencies=["TASK-EAS-D"])),
        ("MISSING_PHASE", lambda b: [task.update(phase="PX") for task in b["task"]["tasks"] if "P7" in task["phase"]]),
        ("MISSING_REQUIRED_ATOM_CLASS", lambda b: b["stack"].update(required_atom_classes=["C", "K", "A", "E", "X"])),
        ("CEREMONIAL_ATOM", lambda b: b["stack"]["atoms"][0].update(oracle="")),
        ("DIRECTORY_GATES", lambda b: b["directories"]["directories"][0].update(mutation_gate="")),
        ("FLOW_UNKNOWN_NODE", lambda b: b["flow"]["edges"][0].update(to="MISSING")),
        ("RELEASE_FALSE_PROMOTION", lambda b: next(item for item in b["closure"]["planes"] if item["plane"] == "RELEASE").update(state="CANDIDATE")),
        ("CLOSURE_DENOMINATOR", lambda b: b["closure"]["denominator"].update(closure_credit=1)),
        ("SECRET_SESSION_OR_HOST_PATH", lambda b: b["flow"]["forbidden_flows"].append("token=abcdef123456")),
    ]
    for expected, mutate in mutations:
        candidate = copy.deepcopy(bundle)
        mutate(candidate)
        try:
            validate_bundle(candidate, check_files=False)
        except Refusal as exc:
            req(expected in str(exc), f"WRONG_REFUSAL:{expected}:{exc}")
        else:
            raise Refusal(f"MUTATION_DID_NOT_FAIL:{expected}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    try:
        bundle = load_bundle()
        validate_bundle(bundle)
        if args.selftest:
            selftest(bundle)
    except (OSError, json.JSONDecodeError, Refusal, TypeError, KeyError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2
    print("PASS task-dag=18+ stack=17+ directories=18+ flow=25+ closure=20+ docs=P0-P7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
