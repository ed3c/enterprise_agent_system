#!/usr/bin/env python3
"""Authoritative planted mutation suite for the profile Tech Lead DAG."""

from __future__ import annotations

import copy
import hashlib
import sys
from collections.abc import Callable
from typing import Any

import verify_profile_dag as gate


def expect_refusal(expected: str, action: Callable[[], None]) -> None:
    try:
        action()
    except (gate.Refusal, ValueError, KeyError, StopIteration) as exc:
        gate.req(expected in str(exc), f"WRONG_REFUSAL:{expected}:{exc}")
    else:
        raise gate.Refusal(f"MUTATION_DID_NOT_FAIL:{expected}")


def mutate_data(
    source: dict[str, dict[str, Any]],
    mutate: Callable[[dict[str, dict[str, Any]]], None],
) -> dict[str, dict[str, Any]]:
    candidate = copy.deepcopy(source)
    mutate(candidate)
    return candidate


def run_data_mutations(data: dict[str, dict[str, Any]]) -> int:
    mutations: list[
        tuple[str, Callable[[dict[str, dict[str, Any]]], None]]
    ] = [
        (
            "INPUT_SUBJECT_DRIFT",
            lambda value: value["inputs"]["inputs"]["eas_k"].update(
                commit="0" * 40
            ),
        ),
        (
            "INPUT_SOURCE_DIGEST",
            lambda value: value["inputs"]["inputs"]["profile_c0"].update(
                source_digest="sha256:" + "0" * 64
            ),
        ),
        (
            "INPUT_CONTRACT_DIGEST",
            lambda value: value["inputs"]["inputs"]["profile_c1"].update(
                bundle_digest="sha256:" + "0" * 64
            ),
        ),
        (
            "DUPLICATE_TASK",
            lambda value: value["run"]["tasks"].append(
                copy.deepcopy(value["run"]["tasks"][0])
            ),
        ),
        (
            "COMPLETION_WITHOUT_START",
            lambda value: next(
                task
                for task in value["run"]["tasks"]
                if task["id"] == "TASK-INCEPTION-A1"
            ).update(start_dependencies=[]),
        ),
        (
            "CYCLIC_DAG:start_dependencies",
            lambda value: next(
                task
                for task in value["run"]["tasks"]
                if task["id"] == gate.TASK_K
            ).update(start_dependencies=["TASK-INCEPTION-H"]),
        ),
        (
            "TASK_LEASE_PATH_MISMATCH",
            lambda value: next(
                lease
                for lease in value["run"]["leases"]
                if lease["task_id"] == "TASK-INCEPTION-A2"
            )["paths"].__setitem__(
                0,
                "profiles/agent-thinking-inception/owners/compaction/**",
            ),
        ),
        (
            "RESOURCE_LEASE_COLLISION",
            lambda value: next(
                lease
                for lease in value["run"]["leases"]
                if lease["task_id"] == "TASK-INCEPTION-A2"
            )["resources"].append(
                "local-storage-namespace:inception-compaction"
            ),
        ),
        (
            "SHADOW_SECOND_STATE_WRITER",
            lambda value: value["run"]["shadow"].update(
                may_commit=["TASK_STATE"]
            ),
        ),
        (
            "HUMAN_AUTHORITY_MISSING",
            lambda value: value["run"]["authority"]["human_owned"].remove(
                "merge"
            ),
        ),
        (
            "CAPABILITY_CYCLE",
            lambda value: next(
                item
                for item in value["capability"]["transitions"]
                if item["transition_id"] == "CAP-INPUT-READBACK"
            )["predecessors"].append("CAP-PROFILE-HANDOFF"),
        ),
        (
            "CAPABILITY_FALSE_EXECUTION",
            lambda value: next(
                item
                for item in value["capability"]["transitions"]
                if item["transition_id"] == "CAP-A1-COMPACTION-OWNER"
            ).update(current_state="CANDIDATE"),
        ),
        (
            "CAPABILITY_SHADOW_AUTHORITY",
            lambda value: next(
                item
                for item in value["capability"]["transitions"]
                if item["transition_id"] == "CAP-PROFILE-SHADOW"
            ).update(authority_ceiling="TASK_STATE_ONLY"),
        ),
        (
            "PACKET_SPEC_DENOMINATOR",
            lambda value: value["specs"]["specs"].pop(),
        ),
        (
            "PACKET_OWNER_SUBSTITUTION",
            lambda value: next(
                item
                for item in value["specs"]["specs"]
                if item["task_id"] == "TASK-INCEPTION-A1"
            ).update(target_repository="ed3c/enterprise_agent_system"),
        ),
        (
            "PACKET_DEFAULT_AUTHORITY",
            lambda value: value["specs"]["defaults"][
                "forbidden_actions"
            ].remove("merge"),
        ),
        (
            "STACK_PLANNED_AS_OBSERVED",
            lambda value: next(
                item
                for item in value["stack"]["atoms"]
                if item["atom_id"] == "INCEPTION-A1"
            ).update(subject=copy.deepcopy(gate.EXACT["profile_k_base"])),
        ),
        (
            "STACK_TRUE_CHILD_WITHOUT_PARENT",
            lambda value: next(
                item
                for item in value["stack"]["atoms"]
                if item["atom_id"] == "INCEPTION-C1"
            ).update(git_parents=[]),
        ),
        (
            "DUPLICATE_ATOM",
            lambda value: value["stack"]["atoms"].append(
                copy.deepcopy(value["stack"]["atoms"][0])
            ),
        ),
        (
            "SECRET_SESSION_OR_LOCAL_PATH",
            lambda value: value["specs"]["claims_not_proven"].append(
                "/mnt/data/private.pdf"
            ),
        ),
    ]

    for expected, mutate in mutations:
        candidate = mutate_data(data, mutate)
        expect_refusal(expected, lambda: gate.validate_all(candidate))
    return len(mutations)


def resign_bundle(bundle: dict[str, Any]) -> None:
    unsigned = copy.deepcopy(bundle)
    unsigned.pop("bundle_digest", None)
    bundle["bundle_digest"] = (
        "sha256:" + hashlib.sha256(gate.canonical(unsigned)).hexdigest()
    )


def run_packet_mutations(data: dict[str, dict[str, Any]]) -> int:
    original = gate.validate_all(copy.deepcopy(data))
    mutations: list[tuple[str, Callable[[dict[str, Any]], None], bool]] = [
        (
            "PACKET_DIGEST_MISMATCH",
            lambda value: value["packets"][0].update(objective="tampered"),
            True,
        ),
        (
            "PROMPT_READ_WRITE_LEASE_COLLISION",
            lambda value: (
                value["packets"][0]["leases"]["read_only_paths"].append(
                    value["packets"][0]["leases"]["write_paths"][0]
                ),
                value["packets"].__setitem__(
                    0, gate.sign_packet(value["packets"][0])
                ),
            ),
            True,
        ),
        (
            "PROMPT_AUTHORITY_WIDENED",
            lambda value: (
                value["packets"][0]["forbidden_actions"].remove("merge"),
                value["packets"].__setitem__(
                    0, gate.sign_packet(value["packets"][0])
                ),
            ),
            True,
        ),
        (
            "MUTABLE_COMMIT",
            lambda value: (
                value["packets"][0]["subject"].update(commit="0" * 40),
                value["packets"][0]["rollback_subject"].update(
                    commit="0" * 40
                ),
                value["packets"].__setitem__(
                    0, gate.sign_packet(value["packets"][0])
                ),
            ),
            True,
        ),
        (
            "PACKET_BUNDLE_DIGEST_MISMATCH",
            lambda value: value.update(bundle_id="tampered"),
            False,
        ),
    ]

    for expected, mutate, resign in mutations:
        candidate = copy.deepcopy(original)
        mutate(candidate)
        if resign:
            resign_bundle(candidate)
        expect_refusal(
            expected,
            lambda: gate.validate_packet_bundle(
                candidate,
                data["run"],
                data["specs"],
                data["inputs"],
            ),
        )
    return len(mutations)


def main() -> int:
    try:
        data = gate.load_all()
        gate.validate_all(data)
        count = run_data_mutations(data) + run_packet_mutations(data)
    except (
        OSError,
        gate.json.JSONDecodeError,
        gate.Refusal,
        ValueError,
        KeyError,
        StopIteration,
    ) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(
        f"PASS mutations={count} "
        "evidence_ceiling=PROFILE_K_MUTATION_GATE_ONLY"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
