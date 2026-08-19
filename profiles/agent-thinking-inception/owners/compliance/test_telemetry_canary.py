from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from telemetry_canary import (  # noqa: E402
    TelemetryCanaryError,
    assert_no_planted_leak,
    run_telemetry_leak_canary,
    sanitize_event,
)


ROOT = Path(__file__).resolve().parents[2]
FLOW = ROOT / "evidence" / "compliance" / "telemetry-flow.example.json"


class TelemetryCanaryTests(unittest.TestCase):
    def flow(self) -> dict:
        return json.loads(FLOW.read_text(encoding="utf-8"))

    def test_synthetic_leak_canary_sanitizes_before_local_sink(self) -> None:
        receipt = run_telemetry_leak_canary(self.flow())
        self.assertEqual(receipt["state"], "DETERMINISTIC_CANARY_PASS")
        self.assertRegex(receipt["input_digest"], r"^sha256:[0-9a-f]{64}$")
        self.assertRegex(receipt["sanitized_digest"], r"^sha256:[0-9a-f]{64}$")
        self.assertRegex(receipt["sink_readback_digest"], r"^sha256:[0-9a-f]{64}$")
        self.assertIn("authorization", receipt["redacted_fields"])
        self.assertIn("raw_secret", receipt["dropped_fields"])
        self.assertTrue(receipt["claims_not_proven"])

    def test_non_allowlisted_destination_is_refused(self) -> None:
        with self.assertRaisesRegex(TelemetryCanaryError, "not allowlisted"):
            sanitize_event(
                {"event_name": "fixture"},
                self.flow(),
                destination="untrusted-collector",
            )

    def test_planted_leak_detector_turns_red(self) -> None:
        with self.assertRaisesRegex(TelemetryCanaryError, "leak detected"):
            assert_no_planted_leak(
                b'{"authorization":"fixture-secret-token-001"}',
                ["fixture-secret-token-001"],
            )

    def test_removing_required_redaction_fails_closed_before_export(self) -> None:
        flow = deepcopy(self.flow())
        flow["redacted_fields"].remove("authorization")
        event = {
            "authorization": "Bearer fixture-secret-token-001",
            "cookie": "fixture-session-cookie-002",
            "user_email": "fixture.user@example.invalid",
            "prompt_fragment": "PROPRIETARY_PROMPT_FIXTURE_003",
            "raw_secret": "RAW_SECRET_FIXTURE_004",
            "raw_source_blob": "PROPRIETARY_SOURCE_FIXTURE_005",
        }
        sanitized = sanitize_event(
            event,
            flow,
            destination=flow["exporter"]["allowlisted_destination"],
        )
        with self.assertRaisesRegex(TelemetryCanaryError, "leak detected"):
            assert_no_planted_leak(
                json.dumps(sanitized, sort_keys=True).encode(),
                [str(event["authorization"])],
            )


if __name__ == "__main__":
    unittest.main()
