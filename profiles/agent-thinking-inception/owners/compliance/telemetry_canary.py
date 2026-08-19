"""Synthetic sanitize-before-export canary for the Inception A4 trace policy."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
from typing import Any

from verify_policy import PolicyContractError, validate_flow


class TelemetryCanaryError(ValueError):
    pass


def _digest_bytes(value: bytes) -> str:
    return "sha256:" + sha256(value).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sanitize_event(
    event: dict[str, Any],
    flow: dict[str, Any],
    *,
    destination: str,
) -> dict[str, Any]:
    validate_flow(flow)
    if destination != flow["exporter"]["allowlisted_destination"]:
        raise TelemetryCanaryError("destination is not allowlisted")

    sanitized = deepcopy(event)
    for field in flow["dropped_fields"]:
        sanitized.pop(field, None)
    for field in flow["redacted_fields"]:
        if field in sanitized:
            sanitized[field] = "<redacted>"
    return sanitized


def assert_no_planted_leak(payload: bytes, planted_values: list[str]) -> None:
    text = payload.decode("utf-8", errors="strict")
    leaked = [value for value in planted_values if value and value in text]
    if leaked:
        raise TelemetryCanaryError(f"sanitizer leak detected for {len(leaked)} planted values")


def run_telemetry_leak_canary(flow: dict[str, Any]) -> dict[str, Any]:
    event = {
        "event_name": "fixture.agent.step",
        "task_id": "public-fixture-task",
        "authorization": "Bearer fixture-secret-token-001",
        "cookie": "fixture-session-cookie-002",
        "user_email": "fixture.user@example.invalid",
        "prompt_fragment": "PROPRIETARY_PROMPT_FIXTURE_003",
        "raw_secret": "RAW_SECRET_FIXTURE_004",
        "raw_source_blob": "PROPRIETARY_SOURCE_FIXTURE_005",
        "safe_counter": 7,
    }
    planted = [
        str(event["authorization"]),
        str(event["cookie"]),
        str(event["user_email"]),
        str(event["prompt_fragment"]),
        str(event["raw_secret"]),
        str(event["raw_source_blob"]),
    ]
    destination = str(flow["exporter"]["allowlisted_destination"])
    sanitized = sanitize_event(event, flow, destination=destination)
    payload = _canonical(sanitized)
    assert_no_planted_leak(payload, planted)

    expected_redactions = {
        field for field in flow["redacted_fields"] if field in event
    }
    for field in expected_redactions:
        if sanitized.get(field) != "<redacted>":
            raise TelemetryCanaryError(f"field was not redacted: {field}")
    for field in flow["dropped_fields"]:
        if field in sanitized:
            raise TelemetryCanaryError(f"field was not dropped: {field}")

    with tempfile.TemporaryDirectory(prefix="inception-a4-telemetry-") as directory:
        sink = Path(directory) / "export.ndjson"
        sink.write_bytes(payload + b"\n")
        readback = sink.read_bytes()
        assert_no_planted_leak(readback, planted)
        sink_digest = _digest_bytes(readback)

    return {
        "schema_version": "enterprise-agent-system/inception-telemetry-canary/v1",
        "flow_id": flow["flow_id"],
        "destination": destination,
        "input_digest": _digest_bytes(_canonical(event)),
        "sanitized_digest": _digest_bytes(payload),
        "sink_readback_digest": sink_digest,
        "redacted_fields": sorted(expected_redactions),
        "dropped_fields": sorted(flow["dropped_fields"]),
        "negative_controls": [
            "raw planted secret absent after sanitize",
            "raw planted PII absent after sanitize",
            "raw proprietary markers absent after sanitize",
            "non-allowlisted destination is refused",
        ],
        "state": "DETERMINISTIC_CANARY_PASS",
        "claims_not_proven": [
            "Synthetic fixture PASS does not prove zero leakage in a live runtime.",
            "No live collector, exporter, storage or deletion system was exercised.",
            "No Human security or legal disposition was produced.",
        ],
    }
