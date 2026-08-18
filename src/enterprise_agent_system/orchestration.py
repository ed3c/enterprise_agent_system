"""Provider-neutral Tech Lead DAG, prompt-packet, lease and reducer primitives."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Iterable, Mapping, Sequence

SHA40 = re.compile(r"^[0-9a-f]{40}$")
HUMAN_ONLY = frozenset({
    "merge", "issue_close", "permission_change", "visibility_change",
    "semantic_conflict_resolution", "data_egress", "irreversible_effect",
    "promotion", "release", "rollback",
})


class ContractError(ValueError):
    """A named fail-closed orchestration refusal."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ContractError(reason)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _task_map(run: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    tasks = run.get("tasks")
    _require(isinstance(tasks, list) and tasks, "TASKS_EMPTY")
    result: dict[str, Mapping[str, Any]] = {}
    for task in tasks:
        task_id = task.get("id")
        _require(isinstance(task_id, str) and task_id.startswith("TASK-"), "TASK_ID")
        _require(task_id not in result, f"DUPLICATE_TASK:{task_id}")
        result[task_id] = task
    return result


def validate_exact_subject(subject: Mapping[str, Any]) -> None:
    _require(
        isinstance(subject.get("repository"), str)
        and "/" in subject["repository"],
        "SUBJECT_REPOSITORY",
    )
    _require(SHA40.fullmatch(str(subject.get("commit", ""))) is not None, "MUTABLE_COMMIT")
    _require(SHA40.fullmatch(str(subject.get("tree", ""))) is not None, "MUTABLE_TREE")


def _path_prefix(path: str) -> str:
    return path.split("*", 1)[0].rstrip("/")


def paths_overlap(left: str, right: str) -> bool:
    a, b = _path_prefix(left), _path_prefix(right)
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def validate_run(run: Mapping[str, Any]) -> None:
    """Validate the core semantic laws needed before Worker admission."""

    validate_exact_subject(run.get("request_subject", {}))
    tasks = _task_map(run)
    task_ids = set(tasks)

    for task_id, task in tasks.items():
        starts = set(task.get("start_dependencies", []))
        completes = set(task.get("completion_dependencies", []))
        _require(completes.issubset(starts), f"COMPLETION_WITHOUT_START:{task_id}")
        for dependency in starts | completes:
            _require(dependency in task_ids, f"UNKNOWN_DEPENDENCY:{task_id}:{dependency}")
            _require(dependency != task_id, f"SELF_DEPENDENCY:{task_id}")

    topological_waves(run, dependency_field="completion_dependencies")

    leases = run.get("leases")
    _require(isinstance(leases, list), "LEASES_NOT_ARRAY")
    by_task: dict[str, Mapping[str, Any]] = {}
    for lease in leases:
        task_id = lease.get("task_id")
        _require(task_id in task_ids, f"LEASE_UNKNOWN_TASK:{task_id}")
        _require(task_id not in by_task, f"DUPLICATE_LEASE:{task_id}")
        by_task[task_id] = lease
    _require(set(by_task) == task_ids, "TASK_LEASE_MISMATCH")

    active = [
        task_id
        for task_id, task in tasks.items()
        if task.get("state") in {"READY", "ACTIVE", "CANDIDATE"}
    ]
    assert_disjoint_leases(run, active)

    reducer = run.get("canonical_reducer", {})
    _require(reducer.get("may_commit") == ["TASK_STATE"], "REDUCER_AUTHORITY_WIDENED")
    shadow = run.get("shadow", {})
    _require(
        shadow.get("read_only") is True
        and shadow.get("separate_evaluation_path") is True,
        "SHADOW_NOT_INDEPENDENT",
    )
    _require(shadow.get("may_commit") == [], "SHADOW_SECOND_STATE_WRITER")

    forbidden = set(run.get("authority", {}).get("automation_forbidden", []))
    for operation in HUMAN_ONLY:
        _require(operation in forbidden, f"AUTOMATION_AUTHORITY_WIDENED:{operation}")


def topological_waves(
    run: Mapping[str, Any], *, dependency_field: str = "completion_dependencies"
) -> list[list[str]]:
    """Return deterministic parallel waves for one declared dependency edge class."""

    tasks = _task_map(run)
    remaining: dict[str, set[str]] = {}
    for task_id, task in tasks.items():
        dependencies = set(task.get(dependency_field, []))
        _require(dependencies.issubset(tasks), f"UNKNOWN_DEPENDENCY:{task_id}")
        remaining[task_id] = dependencies

    waves: list[list[str]] = []
    while remaining:
        ready = sorted(task_id for task_id, deps in remaining.items() if not deps)
        _require(bool(ready), f"CYCLIC_DAG:{dependency_field}")
        waves.append(ready)
        for task_id in ready:
            remaining.pop(task_id)
        for dependencies in remaining.values():
            dependencies.difference_update(ready)
    return waves


def assert_disjoint_leases(run: Mapping[str, Any], task_ids: Sequence[str]) -> None:
    """Refuse concurrent Writer admission when paths or resources overlap."""

    leases = {lease["task_id"]: lease for lease in run.get("leases", [])}
    for task_id in task_ids:
        _require(task_id in leases, f"LEASE_ABSENT:{task_id}")

    for index, left_id in enumerate(task_ids):
        left = leases[left_id]
        for right_id in task_ids[index + 1 :]:
            right = leases[right_id]
            for left_path in left.get("paths", []):
                for right_path in right.get("paths", []):
                    _require(
                        not paths_overlap(left_path, right_path),
                        f"PATH_LEASE_COLLISION:{left_id}:{right_id}:{left_path}:{right_path}",
                    )
            _require(
                set(left.get("resources", [])).isdisjoint(right.get("resources", [])),
                f"RESOURCE_LEASE_COLLISION:{left_id}:{right_id}",
            )


def compile_prompt_packet(
    run: Mapping[str, Any],
    task_id: str,
    *,
    objective: str,
    invariants: Sequence[str],
    read_only_paths: Sequence[str] = (),
    forbidden_actions: Sequence[str] = tuple(sorted(HUMAN_ONLY)),
    required_gates: Sequence[str],
    evidence_ceiling: str,
    retry_budget: int = 1,
) -> dict[str, Any]:
    """Compile a zero-context packet for a fresh Worker conversation."""

    validate_run(run)
    tasks = _task_map(run)
    _require(task_id in tasks, f"UNKNOWN_TASK:{task_id}")
    _require(bool(objective.strip()), "OBJECTIVE_EMPTY")
    _require(bool(invariants), "INVARIANTS_EMPTY")
    _require(bool(required_gates), "GATES_EMPTY")
    _require(retry_budget >= 0, "RETRY_BUDGET")

    task = tasks[task_id]
    lease = next(item for item in run["leases"] if item["task_id"] == task_id)
    forbidden = sorted(set(forbidden_actions) | HUMAN_ONLY)

    body: dict[str, Any] = {
        "schema_version": "enterprise-agent-system/prompt-packet/v1",
        "run_id": run["run_id"],
        "task_id": task_id,
        "subject": dict(run["request_subject"]),
        "objective": objective,
        "non_goals": ["widen authority", "invent evidence", "modify outside leases"],
        "invariants": list(invariants),
        "dependencies": {
            "start": list(task["start_dependencies"]),
            "completion": list(task["completion_dependencies"]),
        },
        "leases": {
            "writer_id": lease["writer_id"],
            "write_paths": list(lease["paths"]),
            "read_only_paths": list(read_only_paths),
            "resources": list(lease["resources"]),
        },
        "output_contract": task["output_contract"],
        "required_lane": task["required_lane"],
        "required_gates": list(required_gates),
        "evidence_ceiling": evidence_ceiling,
        "retry_budget": retry_budget,
        "forbidden_actions": forbidden,
        "handoff": {
            "on_unavailable_capability": "LOCAL_HANDOFF_REQUIRED",
            "on_semantic_conflict": "HUMAN_ADMIT_REQUIRED",
            "receipt_required": True,
        },
    }
    body["packet_digest"] = "sha256:" + hashlib.sha256(_canonical_json(body)).hexdigest()
    return body


def validate_prompt_packet(packet: Mapping[str, Any]) -> None:
    """Validate a persisted fresh-session packet and its content digest."""

    _require(
        packet.get("schema_version") == "enterprise-agent-system/prompt-packet/v1",
        "PROMPT_PACKET_VERSION",
    )
    validate_exact_subject(packet.get("subject", {}))
    _require(isinstance(packet.get("run_id"), str) and packet["run_id"], "RUN_ID")
    _require(
        isinstance(packet.get("task_id"), str) and packet["task_id"].startswith("TASK-"),
        "TASK_ID",
    )
    _require(bool(str(packet.get("objective", "")).strip()), "OBJECTIVE_EMPTY")
    _require(bool(packet.get("invariants")), "INVARIANTS_EMPTY")
    _require(bool(packet.get("required_gates")), "GATES_EMPTY")
    _require(bool(str(packet.get("evidence_ceiling", "")).strip()), "EVIDENCE_CEILING_EMPTY")

    dependencies = packet.get("dependencies", {})
    starts = set(dependencies.get("start", []))
    completes = set(dependencies.get("completion", []))
    _require(completes.issubset(starts), "PROMPT_COMPLETION_WITHOUT_START")

    leases = packet.get("leases", {})
    writes = leases.get("write_paths", [])
    reads = leases.get("read_only_paths", [])
    _require(isinstance(writes, list) and writes, "PROMPT_WRITE_LEASE_EMPTY")
    for write_path in writes:
        for read_path in reads:
            _require(
                not paths_overlap(str(write_path), str(read_path)),
                f"PROMPT_READ_WRITE_LEASE_COLLISION:{write_path}:{read_path}",
            )

    forbidden = set(packet.get("forbidden_actions", []))
    for operation in HUMAN_ONLY:
        _require(operation in forbidden, f"PROMPT_AUTHORITY_WIDENED:{operation}")

    handoff = packet.get("handoff", {})
    _require(
        handoff.get("on_unavailable_capability") == "LOCAL_HANDOFF_REQUIRED",
        "LOCAL_HANDOFF_ROUTE_ABSENT",
    )
    _require(
        handoff.get("on_semantic_conflict") == "HUMAN_ADMIT_REQUIRED",
        "HUMAN_ADMIT_ROUTE_ABSENT",
    )
    _require(handoff.get("receipt_required") is True, "RECEIPT_NOT_REQUIRED")

    claimed_digest = packet.get("packet_digest")
    _require(
        isinstance(claimed_digest, str) and claimed_digest.startswith("sha256:"),
        "PACKET_DIGEST_ABSENT",
    )
    unsigned = dict(packet)
    unsigned.pop("packet_digest", None)
    expected = "sha256:" + hashlib.sha256(_canonical_json(unsigned)).hexdigest()
    _require(claimed_digest == expected, "PACKET_DIGEST_MISMATCH")


def packet_as_markdown(packet: Mapping[str, Any]) -> str:
    """Render a packet without changing its machine payload."""

    machine = json.dumps(packet, ensure_ascii=False, sort_keys=True, indent=2)
    return (
        "# Fresh-session Worker packet\n\n"
        "Treat the JSON block as the complete task contract. Do not rely on prior chat "
        "memory. Stop on subject drift, lease overlap, unavailable required lane, "
        "semantic conflict, data-egress change, or Human-owned action.\n\n"
        f"```json\n{machine}\n```\n"
    )


@dataclass(frozen=True)
class CandidateVerdict:
    state: str
    reasons: tuple[str, ...]
    admitted_candidate_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "reasons": list(self.reasons),
            "admitted_candidate_id": self.admitted_candidate_id,
        }


def reduce_candidate(
    run: Mapping[str, Any],
    *,
    task_id: str,
    candidates: Sequence[Mapping[str, Any]],
    required_gates: Sequence[str],
    required_lane: str,
    shadow_findings: Sequence[Mapping[str, Any]] = (),
) -> CandidateVerdict:
    """Admit one exact-subject candidate for convergence, never for Human/release state."""

    validate_run(run)
    tasks = _task_map(run)
    _require(task_id in tasks, f"UNKNOWN_TASK:{task_id}")

    critical = [
        finding
        for finding in shadow_findings
        if finding.get("severity") == "CRITICAL" and finding.get("state") != "RESOLVED"
    ]
    if critical:
        owners = sorted(
            str(item.get("owner_issue") or f"MISSING_OWNER:{item.get('id', 'UNKNOWN')}")
            for item in critical
        )
        return CandidateVerdict("BLOCKED_BY_SHADOW", tuple(owners))

    expected = run["request_subject"]
    admitted: list[Mapping[str, Any]] = []
    refusals: list[str] = []
    for candidate in candidates:
        candidate_id = str(candidate.get("candidate_id", "UNKNOWN"))
        if candidate.get("task_id") != task_id:
            refusals.append(f"{candidate_id}:CANDIDATE_TASK_MISMATCH")
            continue
        subject = candidate.get("subject", {})
        if subject.get("commit") != expected["commit"] or subject.get("tree") != expected["tree"]:
            refusals.append(f"{candidate_id}:STALE_SUBJECT")
            continue
        if candidate.get("lane") != required_lane:
            refusals.append(f"{candidate_id}:LANE_SUBSTITUTION")
            continue
        gate_states = {
            gate.get("id"): gate.get("state") for gate in candidate.get("gates", [])
        }
        missing = sorted(gate for gate in required_gates if gate_states.get(gate) != "PASS")
        if missing:
            refusals.append(f"{candidate_id}:GATES_NOT_PASS:{','.join(missing)}")
            continue
        if candidate.get("claims_human_or_release_state"):
            refusals.append(f"{candidate_id}:AUTHORITY_PROMOTION")
            continue
        admitted.append(candidate)

    if len(admitted) != 1:
        reason = "NO_ADMISSIBLE_CANDIDATE" if not admitted else "MULTIPLE_ADMISSIBLE_CANDIDATES"
        return CandidateVerdict("BLOCKED", tuple([reason, *sorted(refusals)]))

    return CandidateVerdict(
        "CANDIDATE_ADMITTED_FOR_CONVERGENCE",
        tuple(sorted(refusals)),
        str(admitted[0]["candidate_id"]),
    )
