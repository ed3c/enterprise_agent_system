"""Provider-neutral Tech Lead DAG, prompt-packet, lease and reducer primitives."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Mapping, Sequence

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REPOSITORY = re.compile(r"^[^/\s]+/[^/\s]+$")
ISSUE_URL = re.compile(r"^https://github\.com/[^/]+/[^/]+/issues/[0-9]+$")

HUMAN_ONLY = frozenset(
    {
        "merge",
        "issue_close",
        "permission_change",
        "visibility_change",
        "semantic_conflict_resolution",
        "data_egress",
        "irreversible_effect",
        "promotion",
        "release",
        "rollback",
    }
)
TASK_STATES = frozenset(
    {"PLANNED", "READY", "ACTIVE", "BLOCKED", "CANDIDATE", "VERIFIED", "COMPLETE"}
)
REQUIRED_LANES = frozenset({"CLOUD", "LOCAL", "PRIVATE", "HUMAN"})
RUN_STATES = frozenset(
    {
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
)
GATE_STATES = frozenset({"PASS", "FAIL", "ABSENT", "NOT_EXERCISED", "BLOCKED"})


class ContractError(ValueError):
    """A named fail-closed orchestration refusal."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ContractError(reason)


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


def _validate_lease_path(path: str, name: str) -> None:
    _require(bool(path), f"{name}_EMPTY")
    _require(not path.startswith(("/", "\\")), f"{name}_ABSOLUTE")
    parts = path.replace("\\", "/").split("/")
    _require(".." not in parts, f"{name}_TRAVERSAL")
    _require("\x00" not in path, f"{name}_NUL")


def _task_map(run: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    tasks = run.get("tasks")
    _require(isinstance(tasks, list) and tasks, "TASKS_EMPTY")
    result: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(tasks):
        task = _strict_mapping(
            raw,
            required={
                "id",
                "start_dependencies",
                "completion_dependencies",
                "owns_paths",
                "required_lane",
                "output_contract",
                "state",
            },
            name=f"TASK_{index}",
        )
        task_id = task["id"]
        _require(
            isinstance(task_id, str)
            and re.fullmatch(r"TASK-[A-Z0-9][A-Z0-9._-]*", task_id) is not None,
            f"TASK_ID:{task_id}",
        )
        _require(task_id not in result, f"DUPLICATE_TASK:{task_id}")
        result[task_id] = task
    return result


def validate_exact_subject(subject: Mapping[str, Any]) -> None:
    subject = _strict_mapping(
        subject,
        required={"repository", "commit", "tree"},
        name="EXACT_SUBJECT",
    )
    _require(
        REPOSITORY.fullmatch(str(subject["repository"])) is not None,
        "SUBJECT_REPOSITORY",
    )
    _require(
        SHA40.fullmatch(str(subject["commit"])) is not None,
        "MUTABLE_COMMIT",
    )
    _require(
        SHA40.fullmatch(str(subject["tree"])) is not None,
        "MUTABLE_TREE",
    )


def _path_prefix(path: str) -> str:
    return path.split("*", 1)[0].rstrip("/")


def paths_overlap(left: str, right: str) -> bool:
    a, b = _path_prefix(left), _path_prefix(right)
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def topological_waves(
    run: Mapping[str, Any], *, dependency_field: str = "completion_dependencies"
) -> list[list[str]]:
    """Return deterministic parallel waves for one declared dependency edge class."""

    _require(
        dependency_field in {"start_dependencies", "completion_dependencies"},
        f"UNKNOWN_DEPENDENCY_FIELD:{dependency_field}",
    )
    tasks = _task_map(run)
    remaining: dict[str, set[str]] = {}
    for task_id, task in tasks.items():
        dependencies = set(
            _unique_strings(
                task[dependency_field],
                f"{dependency_field.upper()}:{task_id}",
                nonempty=False,
            )
        )
        _require(
            dependencies.issubset(tasks),
            f"UNKNOWN_DEPENDENCY:{task_id}:{sorted(dependencies - set(tasks))}",
        )
        _require(task_id not in dependencies, f"SELF_DEPENDENCY:{task_id}")
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


def _lease_map(
    run: Mapping[str, Any], tasks: Mapping[str, Mapping[str, Any]]
) -> dict[str, Mapping[str, Any]]:
    raw_leases = run.get("leases")
    _require(isinstance(raw_leases, list) and raw_leases, "LEASES_EMPTY")
    leases: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(raw_leases):
        lease = _strict_mapping(
            raw,
            required={"task_id", "writer_id", "paths", "resources"},
            name=f"LEASE_{index}",
        )
        task_id = lease["task_id"]
        _require(
            isinstance(task_id, str) and task_id in tasks,
            f"LEASE_UNKNOWN_TASK:{task_id}",
        )
        _require(task_id not in leases, f"DUPLICATE_LEASE:{task_id}")
        _require(
            isinstance(lease["writer_id"], str) and bool(lease["writer_id"].strip()),
            f"WRITER_ID:{task_id}",
        )
        paths = _unique_strings(lease["paths"], f"LEASE_PATHS:{task_id}")
        for path in paths:
            _validate_lease_path(path, f"LEASE_PATH:{task_id}")
        _unique_strings(
            lease["resources"],
            f"LEASE_RESOURCES:{task_id}",
            nonempty=False,
        )
        _require(
            set(paths) == set(tasks[task_id]["owns_paths"]),
            f"TASK_LEASE_PATH_MISMATCH:{task_id}",
        )
        leases[task_id] = lease
    _require(set(leases) == set(tasks), "TASK_LEASE_MISMATCH")
    return leases


def assert_disjoint_leases(run: Mapping[str, Any], task_ids: Sequence[str]) -> None:
    """Refuse concurrent Writer admission when paths or resources overlap."""

    tasks = _task_map(run)
    leases = _lease_map(run, tasks)
    selected = list(task_ids)
    _require(len(selected) == len(set(selected)), "DUPLICATE_ACTIVE_TASK")
    for task_id in selected:
        _require(task_id in leases, f"LEASE_ABSENT:{task_id}")

    for index, left_id in enumerate(selected):
        left = leases[left_id]
        for right_id in selected[index + 1 :]:
            right = leases[right_id]
            for left_path in left["paths"]:
                for right_path in right["paths"]:
                    _require(
                        not paths_overlap(left_path, right_path),
                        f"PATH_LEASE_COLLISION:{left_id}:{right_id}:{left_path}:{right_path}",
                    )
            _require(
                set(left["resources"]).isdisjoint(right["resources"]),
                f"RESOURCE_LEASE_COLLISION:{left_id}:{right_id}",
            )


def validate_run(run: Mapping[str, Any]) -> None:
    """Validate all deterministic laws needed before Worker admission."""

    run = _strict_mapping(
        run,
        required={
            "schema_version",
            "run_id",
            "request_subject",
            "tasks",
            "leases",
            "canonical_reducer",
            "shadow",
            "authority",
            "state",
        },
        name="ORCHESTRATION_RUN",
    )
    _require(
        run["schema_version"] == "enterprise-agent-system/orchestration-run/v1",
        "ORCHESTRATION_VERSION",
    )
    _require(
        isinstance(run["run_id"], str)
        and re.fullmatch(r"RUN-[A-Z0-9][A-Z0-9._-]*", run["run_id"]) is not None,
        "RUN_ID",
    )
    validate_exact_subject(run["request_subject"])
    tasks = _task_map(run)

    for task_id, task in tasks.items():
        starts = set(
            _unique_strings(
                task["start_dependencies"],
                f"START_DEPENDENCIES:{task_id}",
                nonempty=False,
            )
        )
        completes = set(
            _unique_strings(
                task["completion_dependencies"],
                f"COMPLETION_DEPENDENCIES:{task_id}",
                nonempty=False,
            )
        )
        _require(
            completes.issubset(starts),
            f"COMPLETION_WITHOUT_START:{task_id}",
        )
        for dependency in starts | completes:
            _require(
                dependency in tasks,
                f"UNKNOWN_DEPENDENCY:{task_id}:{dependency}",
            )
            _require(dependency != task_id, f"SELF_DEPENDENCY:{task_id}")

        owns_paths = _unique_strings(task["owns_paths"], f"OWNS_PATHS:{task_id}")
        for path in owns_paths:
            _validate_lease_path(path, f"OWNS_PATH:{task_id}")
        _require(
            task["required_lane"] in REQUIRED_LANES,
            f"REQUIRED_LANE:{task_id}",
        )
        _require(
            isinstance(task["output_contract"], str)
            and bool(task["output_contract"].strip()),
            f"OUTPUT_CONTRACT:{task_id}",
        )
        _require(task["state"] in TASK_STATES, f"TASK_STATE:{task_id}")

    topological_waves(run, dependency_field="start_dependencies")
    topological_waves(run, dependency_field="completion_dependencies")

    _lease_map(run, tasks)
    active = [
        task_id
        for task_id, task in tasks.items()
        if task["state"] in {"READY", "ACTIVE", "CANDIDATE"}
    ]
    if active:
        assert_disjoint_leases(run, active)

    reducer = _strict_mapping(
        run["canonical_reducer"],
        required={"owner", "may_commit"},
        name="CANONICAL_REDUCER",
    )
    _require(
        isinstance(reducer["owner"], str) and bool(reducer["owner"].strip()),
        "REDUCER_OWNER",
    )
    _require(
        reducer["may_commit"] == ["TASK_STATE"],
        "REDUCER_AUTHORITY_WIDENED",
    )

    shadow = _strict_mapping(
        run["shadow"],
        required={"read_only", "separate_evaluation_path", "may_commit"},
        name="SHADOW",
    )
    _require(
        shadow["read_only"] is True
        and shadow["separate_evaluation_path"] is True,
        "SHADOW_NOT_INDEPENDENT",
    )
    _require(shadow["may_commit"] == [], "SHADOW_SECOND_STATE_WRITER")

    authority = _strict_mapping(
        run["authority"],
        required={"automation_forbidden", "human_owned"},
        name="AUTHORITY",
    )
    forbidden = set(
        _unique_strings(
            authority["automation_forbidden"],
            "AUTOMATION_FORBIDDEN",
        )
    )
    human_owned = set(
        _unique_strings(authority["human_owned"], "HUMAN_OWNED")
    )
    for operation in HUMAN_ONLY:
        _require(
            operation in forbidden,
            f"AUTOMATION_AUTHORITY_WIDENED:{operation}",
        )
        _require(
            operation in human_owned,
            f"HUMAN_AUTHORITY_MISSING:{operation}",
        )

    _require(run["state"] in RUN_STATES, "RUN_STATE")


def compile_prompt_packet(
    run: Mapping[str, Any],
    task_id: str,
    *,
    objective: str,
    invariants: Sequence[str],
    required_gates: Sequence[str],
    evidence_ceiling: str,
    non_goals: Sequence[str] = (
        "widen authority",
        "invent evidence",
        "modify outside leases",
    ),
    unknowns: Sequence[str] = (
        "runtime and provider behavior remain unverified",
    ),
    read_only_paths: Sequence[str] = (),
    input_contract: Mapping[str, Any] | None = None,
    acceptance_criteria: Sequence[str] = (
        "all required gates PASS on the exact subject",
    ),
    positive_controls: Sequence[str] = (),
    negative_controls: Sequence[str] = (
        "stale subject",
        "lease overlap",
        "authority widening",
    ),
    runtime_requirements: Sequence[str] = (
        "execute only in the declared evidence lane",
    ),
    capability_requirements: Sequence[str] = (
        "exact subject readback",
        "deterministic gate execution",
    ),
    cleanup_requirements: Sequence[str] = (
        "report dirty state and residue inventory",
    ),
    forbidden_actions: Sequence[str] = tuple(sorted(HUMAN_ONLY)),
    receipt_fields: Sequence[str] = (
        "packet_digest",
        "subject_before",
        "subject_after",
        "changed_paths",
        "commands",
        "gates",
        "attempts",
        "cleanup",
        "rollback_subject",
        "claims_not_proven",
        "next_authority",
    ),
    retry_budget: int = 1,
    timeout_seconds: int = 900,
    next_authority: str = "TECH_LEAD_REDUCER",
) -> dict[str, Any]:
    """Compile a content-addressed, zero-context fresh-session Worker packet."""

    validate_run(run)
    tasks = _task_map(run)
    _require(task_id in tasks, f"UNKNOWN_TASK:{task_id}")
    _require(isinstance(objective, str) and bool(objective.strip()), "OBJECTIVE_EMPTY")
    _require(bool(str(evidence_ceiling).strip()), "EVIDENCE_CEILING_EMPTY")
    invariant_list = _unique_strings(list(invariants), "INVARIANTS")
    gate_list = _unique_strings(list(required_gates), "REQUIRED_GATES")
    non_goal_list = _unique_strings(list(non_goals), "NON_GOALS")
    unknown_list = _unique_strings(list(unknowns), "UNKNOWNS")
    acceptance_list = _unique_strings(
        list(acceptance_criteria), "ACCEPTANCE_CRITERIA"
    )
    positive_list = (
        _unique_strings(list(positive_controls), "POSITIVE_CONTROLS")
        if positive_controls
        else list(gate_list)
    )
    negative_list = _unique_strings(
        list(negative_controls), "NEGATIVE_CONTROLS"
    )
    runtime_list = _unique_strings(
        list(runtime_requirements), "RUNTIME_REQUIREMENTS"
    )
    capability_list = _unique_strings(
        list(capability_requirements), "CAPABILITY_REQUIREMENTS"
    )
    cleanup_list = _unique_strings(
        list(cleanup_requirements), "CLEANUP_REQUIREMENTS"
    )
    receipt_list = _unique_strings(list(receipt_fields), "RECEIPT_FIELDS")
    _require(retry_budget >= 0, "RETRY_BUDGET")
    _require(timeout_seconds > 0, "TIMEOUT_SECONDS")
    _require(
        isinstance(next_authority, str) and bool(next_authority.strip()),
        "NEXT_AUTHORITY_EMPTY",
    )

    task = tasks[task_id]
    leases = _lease_map(run, tasks)
    lease = leases[task_id]
    forbidden = sorted(set(forbidden_actions) | HUMAN_ONLY)
    for path in read_only_paths:
        _validate_lease_path(str(path), "READ_ONLY_PATH")
    for write_path in lease["paths"]:
        for read_path in read_only_paths:
            _require(
                not paths_overlap(write_path, str(read_path)),
                f"PROMPT_READ_WRITE_LEASE_COLLISION:{write_path}:{read_path}",
            )

    frozen_input = dict(input_contract or {})
    if not frozen_input:
        frozen_input = {
            "request_subject": dict(run["request_subject"]),
            "task_dependencies": {
                "start": list(task["start_dependencies"]),
                "completion": list(task["completion_dependencies"]),
            },
        }

    body: dict[str, Any] = {
        "schema_version": "enterprise-agent-system/prompt-packet/v2",
        "run_id": run["run_id"],
        "task_id": task_id,
        "subject": dict(run["request_subject"]),
        "objective": objective,
        "non_goals": non_goal_list,
        "invariants": invariant_list,
        "unknowns": unknown_list,
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
        "input_contract": frozen_input,
        "output_contract": task["output_contract"],
        "acceptance_criteria": acceptance_list,
        "controls": {
            "required_gates": gate_list,
            "positive": positive_list,
            "negative": negative_list,
        },
        "runtime": {
            "required_lane": task["required_lane"],
            "requirements": runtime_list,
            "capabilities": capability_list,
        },
        "budgets": {
            "retry_budget": retry_budget,
            "timeout_seconds": timeout_seconds,
        },
        "cleanup": {
            "requirements": cleanup_list,
            "residue_inventory_required": True,
        },
        "rollback_subject": dict(run["request_subject"]),
        "required_receipt": {
            "fields": receipt_list,
            "exact_subject_required": True,
            "lane_literal_required": True,
        },
        "evidence_ceiling": evidence_ceiling,
        "forbidden_actions": forbidden,
        "handoff": {
            "on_unavailable_capability": "LOCAL_HANDOFF_REQUIRED",
            "on_semantic_conflict": "HUMAN_ADMIT_REQUIRED",
            "next_authority": next_authority,
        },
    }
    body["packet_digest"] = (
        "sha256:" + hashlib.sha256(_canonical_json(body)).hexdigest()
    )
    return body


def validate_prompt_packet(packet: Mapping[str, Any]) -> None:
    """Validate a persisted fresh-session packet and its content digest."""

    packet = _strict_mapping(
        packet,
        required={
            "schema_version",
            "run_id",
            "task_id",
            "subject",
            "objective",
            "non_goals",
            "invariants",
            "unknowns",
            "dependencies",
            "leases",
            "input_contract",
            "output_contract",
            "acceptance_criteria",
            "controls",
            "runtime",
            "budgets",
            "cleanup",
            "rollback_subject",
            "required_receipt",
            "evidence_ceiling",
            "forbidden_actions",
            "handoff",
            "packet_digest",
        },
        name="PROMPT_PACKET",
    )
    _require(
        packet["schema_version"] == "enterprise-agent-system/prompt-packet/v2",
        "PROMPT_PACKET_VERSION",
    )
    validate_exact_subject(packet["subject"])
    validate_exact_subject(packet["rollback_subject"])
    _require(
        packet["rollback_subject"] == packet["subject"],
        "ROLLBACK_SUBJECT_DRIFT",
    )
    _require(
        isinstance(packet["run_id"], str) and bool(packet["run_id"].strip()),
        "RUN_ID",
    )
    _require(
        isinstance(packet["task_id"], str)
        and packet["task_id"].startswith("TASK-"),
        "TASK_ID",
    )
    _require(
        isinstance(packet["objective"], str) and bool(packet["objective"].strip()),
        "OBJECTIVE_EMPTY",
    )
    for field, label in (
        ("non_goals", "NON_GOALS"),
        ("invariants", "INVARIANTS"),
        ("unknowns", "UNKNOWNS"),
        ("acceptance_criteria", "ACCEPTANCE_CRITERIA"),
    ):
        _unique_strings(packet[field], label)
    _require(
        isinstance(packet["evidence_ceiling"], str)
        and bool(packet["evidence_ceiling"].strip()),
        "EVIDENCE_CEILING_EMPTY",
    )

    dependencies = _strict_mapping(
        packet["dependencies"],
        required={"start", "completion"},
        name="PROMPT_DEPENDENCIES",
    )
    starts = set(
        _unique_strings(
            dependencies["start"], "PROMPT_START_DEPENDENCIES", nonempty=False
        )
    )
    completes = set(
        _unique_strings(
            dependencies["completion"],
            "PROMPT_COMPLETION_DEPENDENCIES",
            nonempty=False,
        )
    )
    _require(
        completes.issubset(starts),
        "PROMPT_COMPLETION_WITHOUT_START",
    )

    leases = _strict_mapping(
        packet["leases"],
        required={"writer_id", "write_paths", "read_only_paths", "resources"},
        name="PROMPT_LEASES",
    )
    _require(
        isinstance(leases["writer_id"], str)
        and bool(leases["writer_id"].strip()),
        "PROMPT_WRITER_ID",
    )
    writes = _unique_strings(leases["write_paths"], "PROMPT_WRITE_PATHS")
    reads = _unique_strings(
        leases["read_only_paths"],
        "PROMPT_READ_ONLY_PATHS",
        nonempty=False,
    )
    _unique_strings(leases["resources"], "PROMPT_RESOURCES", nonempty=False)
    for path in [*writes, *reads]:
        _validate_lease_path(path, "PROMPT_PATH")
    for write_path in writes:
        for read_path in reads:
            _require(
                not paths_overlap(write_path, read_path),
                f"PROMPT_READ_WRITE_LEASE_COLLISION:{write_path}:{read_path}",
            )

    _require(
        isinstance(packet["input_contract"], Mapping)
        and bool(packet["input_contract"]),
        "INPUT_CONTRACT_EMPTY",
    )
    _require(
        isinstance(packet["output_contract"], str)
        and bool(packet["output_contract"].strip()),
        "OUTPUT_CONTRACT_EMPTY",
    )

    controls = _strict_mapping(
        packet["controls"],
        required={"required_gates", "positive", "negative"},
        name="PROMPT_CONTROLS",
    )
    _unique_strings(controls["required_gates"], "PROMPT_REQUIRED_GATES")
    _unique_strings(controls["positive"], "PROMPT_POSITIVE_CONTROLS")
    _unique_strings(controls["negative"], "PROMPT_NEGATIVE_CONTROLS")

    runtime = _strict_mapping(
        packet["runtime"],
        required={"required_lane", "requirements", "capabilities"},
        name="PROMPT_RUNTIME",
    )
    _require(
        runtime["required_lane"] in REQUIRED_LANES,
        "PROMPT_REQUIRED_LANE",
    )
    _unique_strings(runtime["requirements"], "PROMPT_RUNTIME_REQUIREMENTS")
    _unique_strings(runtime["capabilities"], "PROMPT_CAPABILITIES")

    budgets = _strict_mapping(
        packet["budgets"],
        required={"retry_budget", "timeout_seconds"},
        name="PROMPT_BUDGETS",
    )
    _require(
        isinstance(budgets["retry_budget"], int)
        and budgets["retry_budget"] >= 0,
        "PROMPT_RETRY_BUDGET",
    )
    _require(
        isinstance(budgets["timeout_seconds"], int)
        and budgets["timeout_seconds"] > 0,
        "PROMPT_TIMEOUT",
    )

    cleanup = _strict_mapping(
        packet["cleanup"],
        required={"requirements", "residue_inventory_required"},
        name="PROMPT_CLEANUP",
    )
    _unique_strings(cleanup["requirements"], "PROMPT_CLEANUP_REQUIREMENTS")
    _require(
        cleanup["residue_inventory_required"] is True,
        "RESIDUE_INVENTORY_NOT_REQUIRED",
    )

    receipt = _strict_mapping(
        packet["required_receipt"],
        required={
            "fields",
            "exact_subject_required",
            "lane_literal_required",
        },
        name="PROMPT_RECEIPT",
    )
    _unique_strings(receipt["fields"], "PROMPT_RECEIPT_FIELDS")
    _require(
        receipt["exact_subject_required"] is True,
        "RECEIPT_EXACT_SUBJECT_NOT_REQUIRED",
    )
    _require(
        receipt["lane_literal_required"] is True,
        "RECEIPT_LANE_NOT_LITERAL",
    )

    forbidden = set(
        _unique_strings(packet["forbidden_actions"], "PROMPT_FORBIDDEN_ACTIONS")
    )
    for operation in HUMAN_ONLY:
        _require(
            operation in forbidden,
            f"PROMPT_AUTHORITY_WIDENED:{operation}",
        )

    handoff = _strict_mapping(
        packet["handoff"],
        required={
            "on_unavailable_capability",
            "on_semantic_conflict",
            "next_authority",
        },
        name="PROMPT_HANDOFF",
    )
    _require(
        handoff["on_unavailable_capability"] == "LOCAL_HANDOFF_REQUIRED",
        "LOCAL_HANDOFF_ROUTE_ABSENT",
    )
    _require(
        handoff["on_semantic_conflict"] == "HUMAN_ADMIT_REQUIRED",
        "HUMAN_ADMIT_ROUTE_ABSENT",
    )
    _require(
        isinstance(handoff["next_authority"], str)
        and bool(handoff["next_authority"].strip()),
        "NEXT_AUTHORITY_EMPTY",
    )

    claimed_digest = packet["packet_digest"]
    _require(
        isinstance(claimed_digest, str)
        and SHA256.fullmatch(claimed_digest) is not None,
        "PACKET_DIGEST_ABSENT",
    )
    unsigned = dict(packet)
    unsigned.pop("packet_digest")
    expected = "sha256:" + hashlib.sha256(_canonical_json(unsigned)).hexdigest()
    _require(claimed_digest == expected, "PACKET_DIGEST_MISMATCH")


def packet_as_markdown(packet: Mapping[str, Any]) -> str:
    """Render a packet without changing its machine payload."""

    validate_prompt_packet(packet)
    machine = json.dumps(packet, ensure_ascii=False, sort_keys=True, indent=2)
    return (
        "# Fresh-session Worker packet\n\n"
        "Treat the JSON block as the complete task contract. Do not rely on prior "
        "chat memory. Stop on subject drift, lease overlap, unavailable required "
        "lane, semantic conflict, data-egress change, failed cleanup, or a "
        "Human-owned action.\n\n"
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
    """Admit one exact-subject candidate for convergence, never Human/release state."""

    validate_run(run)
    tasks = _task_map(run)
    _require(task_id in tasks, f"UNKNOWN_TASK:{task_id}")
    required_gate_set = set(
        _unique_strings(list(required_gates), "REDUCER_REQUIRED_GATES")
    )
    _require(required_lane in REQUIRED_LANES, "REDUCER_REQUIRED_LANE")

    critical_owners: list[str] = []
    for index, raw in enumerate(shadow_findings):
        finding = _strict_mapping(
            raw,
            required={"id", "severity", "state", "owner_issue"},
            name=f"SHADOW_FINDING_{index}",
        )
        if finding["severity"] == "CRITICAL" and finding["state"] != "RESOLVED":
            owner = finding["owner_issue"]
            if not isinstance(owner, str) or ISSUE_URL.fullmatch(owner) is None:
                owner = f"MISSING_OWNER:{finding['id']}"
            critical_owners.append(owner)
    if critical_owners:
        return CandidateVerdict(
            "BLOCKED_BY_SHADOW",
            tuple(sorted(critical_owners)),
        )

    expected = dict(run["request_subject"])
    admitted: list[Mapping[str, Any]] = []
    refusals: list[str] = []
    seen_candidate_ids: set[str] = set()

    for index, raw in enumerate(candidates):
        candidate = _strict_mapping(
            raw,
            required={
                "candidate_id",
                "task_id",
                "subject",
                "lane",
                "gates",
                "claims_human_or_release_state",
            },
            optional={"attempt_id", "evidence", "claims_not_proven"},
            name=f"CANDIDATE_{index}",
        )
        candidate_id = str(candidate["candidate_id"])
        if not candidate_id or candidate_id in seen_candidate_ids:
            refusals.append(
                f"{candidate_id or 'UNKNOWN'}:DUPLICATE_OR_EMPTY_CANDIDATE_ID"
            )
            continue
        seen_candidate_ids.add(candidate_id)

        if candidate["task_id"] != task_id:
            refusals.append(f"{candidate_id}:CANDIDATE_TASK_MISMATCH")
            continue

        try:
            validate_exact_subject(candidate["subject"])
        except ContractError:
            refusals.append(f"{candidate_id}:INVALID_SUBJECT")
            continue
        if dict(candidate["subject"]) != expected:
            refusals.append(f"{candidate_id}:STALE_SUBJECT")
            continue

        if candidate["lane"] != required_lane:
            refusals.append(f"{candidate_id}:LANE_SUBSTITUTION")
            continue

        gates = candidate["gates"]
        if not isinstance(gates, list):
            refusals.append(f"{candidate_id}:GATES_NOT_ARRAY")
            continue
        gate_states: dict[str, str] = {}
        malformed_gate = False
        for gate_index, raw_gate in enumerate(gates):
            try:
                gate = _strict_mapping(
                    raw_gate,
                    required={"id", "state"},
                    optional={"evidence"},
                    name=f"CANDIDATE_GATE_{gate_index}",
                )
            except ContractError:
                malformed_gate = True
                break
            gate_id = gate["id"]
            state = gate["state"]
            if (
                not isinstance(gate_id, str)
                or not gate_id
                or gate_id in gate_states
                or state not in GATE_STATES
            ):
                malformed_gate = True
                break
            gate_states[gate_id] = state
        if malformed_gate:
            refusals.append(f"{candidate_id}:MALFORMED_OR_DUPLICATE_GATE")
            continue

        missing = sorted(
            gate for gate in required_gate_set if gate_states.get(gate) != "PASS"
        )
        if missing:
            refusals.append(
                f"{candidate_id}:GATES_NOT_PASS:{','.join(missing)}"
            )
            continue

        if candidate["claims_human_or_release_state"] is not False:
            refusals.append(f"{candidate_id}:AUTHORITY_PROMOTION")
            continue

        admitted.append(candidate)

    if len(admitted) != 1:
        reason = (
            "NO_ADMISSIBLE_CANDIDATE"
            if not admitted
            else "MULTIPLE_ADMISSIBLE_CANDIDATES"
        )
        return CandidateVerdict(
            "BLOCKED",
            tuple([reason, *sorted(refusals)]),
        )

    return CandidateVerdict(
        "CANDIDATE_ADMITTED_FOR_CONVERGENCE",
        tuple(sorted(refusals)),
        str(admitted[0]["candidate_id"]),
    )
