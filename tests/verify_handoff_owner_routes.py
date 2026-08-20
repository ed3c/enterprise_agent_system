#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "handoff/local-handoff-queue.json"
PREFIX = "https://github.com/ed3c/enterprise_agent_system/issues/"

EXPECTED_OWNER_ISSUES = {
    "LH-P7-01-ROOT-D-V3-LOCAL-READBACK": 14,
    "LH-P7-02-A2R-CONTEXT-TOKENIZER": 7,
    "LH-P7-03-A1-PHYSICAL-DURABILITY": 5,
    "LH-P7-04-A2-ISOLATION-PROVIDER": 7,
    "LH-P7-05-A3-INDEPENDENT-SEMANTIC": 15,
    "LH-P7-06-A4-TERMS-TELEMETRY": 16,
    "LH-P7-07-A5-EXTERNAL-BENCHMARK": 17,
    "LH-P7-08-A6-PROVIDER-EFFECT": 18,
    "LH-P7-09-VERTICAL-CANARY": 14,
    "LH-P7-10-FINAL-TRUTH-VERIFY": 15,
    "LH-P7-11-HUMAN-ADMISSION": 14,
}


def main() -> None:
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    items = queue.get("items", [])
    actual = {item.get("item_id"): item.get("owner_issue") for item in items}
    expected = {item_id: f"{PREFIX}{issue}" for item_id, issue in EXPECTED_OWNER_ISSUES.items()}

    if actual != expected:
        missing = {k: v for k, v in expected.items() if actual.get(k) != v}
        raise SystemExit(f"OWNER_ROUTE_DRIFT:{missing}")

    stale_p5 = f"{PREFIX}22"
    if stale_p5 in actual.values():
        raise SystemExit("CLOSED_P5_ISSUE_HAS_EXECUTION_AUTHORITY")

    if queue.get("queue_execution") != "NOT_PERFORMED":
        raise SystemExit("QUEUE_EXECUTION_PROMOTED")
    if queue.get("closure_projection", {}).get("vertical_canary") != "PLAN_ONLY":
        raise SystemExit("VERTICAL_CANARY_PROMOTED")
    if queue.get("closure_projection", {}).get("requirements_closure_credit") != 0:
        raise SystemExit("CLOSURE_CREDIT_PROMOTED")

    print("PASS handoff owner routes=11 closed_p5_execution_authority=0 execution=NOT_PERFORMED canary=PLAN_ONLY credit=0")


if __name__ == "__main__":
    main()
