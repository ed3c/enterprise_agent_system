#!/usr/bin/env python3
"""Render content-addressed zero-context packets for the profile owner waves."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from enterprise_agent_system.orchestration import (  # noqa: E402
    compile_prompt_packet,
    packet_as_markdown,
    validate_prompt_packet,
    validate_run,
)

HERE = pathlib.Path(__file__).resolve().parent
RUN_PATH = HERE / "profile-run.json"
SPECS_PATH = HERE / "profile-worker-packet-specs.json"
INPUT_PATH = HERE / "profile-input-binding.json"


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"root is not an object: {path}")
    return value


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def compile_packets() -> dict[str, Any]:
    run = load(RUN_PATH)
    specs = load(SPECS_PATH)
    inputs = load(INPUT_PATH)
    validate_run(run)

    defaults = specs["defaults"]
    packets: list[dict[str, Any]] = []
    for spec in specs["specs"]:
        input_contract = {
            "input_binding": {
                "path": specs["input_binding"]["path"],
                "profile_k_base_commit": specs["input_binding"][
                    "profile_k_base_commit"
                ],
                "profile_k_base_tree": specs["input_binding"][
                    "profile_k_base_tree"
                ],
                "source_digest": specs["input_binding"]["source_digest"],
                "contract_bundle_digest": specs["input_binding"][
                    "contract_bundle_digest"
                ],
            },
            "exact_inputs": inputs["inputs"],
            "owner_contract": {
                "role": spec["role"],
                "owner_issue": spec["owner_issue"],
                "target_repository": spec["target_repository"],
                "target_interface": spec["target_interface"],
                "packet_state": spec["packet_state"],
                "claims_not_proven": spec["claims_not_proven"],
            },
        }
        packet = compile_prompt_packet(
            run,
            spec["task_id"],
            objective=spec["objective"],
            invariants=defaults["invariants"],
            required_gates=spec["required_gates"],
            evidence_ceiling=spec["evidence_ceiling"],
            non_goals=defaults["non_goals"],
            unknowns=defaults["unknowns"],
            read_only_paths=defaults["read_only_paths"],
            input_contract=input_contract,
            acceptance_criteria=defaults["acceptance_criteria"],
            positive_controls=spec["positive_controls"],
            negative_controls=defaults["negative_controls"],
            runtime_requirements=spec["runtime_requirements"],
            capability_requirements=spec["capability_requirements"],
            cleanup_requirements=defaults["cleanup_requirements"],
            forbidden_actions=defaults["forbidden_actions"],
            receipt_fields=defaults["receipt_fields"],
            retry_budget=spec["retry_budget"],
            timeout_seconds=spec["timeout_seconds"],
            next_authority=spec["next_authority"],
        )
        validate_prompt_packet(packet)
        packets.append(packet)

    body: dict[str, Any] = {
        "schema_version": "enterprise-agent-system/inception-packet-bundle/v1",
        "bundle_id": "PACKET-BUNDLE-INCEPTION-K-2026-08-18",
        "request_subject": run["request_subject"],
        "packet_count": len(packets),
        "packets": packets,
        "evidence_ceiling": "ZERO_CONTEXT_PACKET_BUNDLE_CANDIDATE_ONLY",
        "claims_not_proven": [
            "Packet generation is not Worker execution.",
            "Owner repository subjects must be rebound before mutation.",
            "Local provider effect user Human release and rollback lanes remain open.",
        ],
    }
    body["bundle_digest"] = "sha256:" + hashlib.sha256(canonical(body)).hexdigest()
    return body


def write_bundle(bundle: dict[str, Any], output: pathlib.Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": bundle["schema_version"],
        "bundle_id": bundle["bundle_id"],
        "request_subject": bundle["request_subject"],
        "packet_count": bundle["packet_count"],
        "packet_digests": {
            packet["task_id"]: packet["packet_digest"]
            for packet in bundle["packets"]
        },
        "bundle_digest": bundle["bundle_digest"],
        "evidence_ceiling": bundle["evidence_ceiling"],
        "claims_not_proven": bundle["claims_not_proven"],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    for packet in bundle["packets"]:
        stem = packet["task_id"].lower()
        (output / f"{stem}.json").write_text(
            json.dumps(packet, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / f"{stem}.system.md").write_text(
            packet_as_markdown(packet), encoding="utf-8"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()
    try:
        bundle = compile_packets()
        if args.output:
            write_bundle(bundle, args.output)
        print(
            json.dumps(
                {
                    "packet_count": bundle["packet_count"],
                    "packet_digests": {
                        packet["task_id"]: packet["packet_digest"]
                        for packet in bundle["packets"]
                    },
                    "bundle_digest": bundle["bundle_digest"],
                    "evidence_ceiling": bundle["evidence_ceiling"],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    except (OSError, ValueError, KeyError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
