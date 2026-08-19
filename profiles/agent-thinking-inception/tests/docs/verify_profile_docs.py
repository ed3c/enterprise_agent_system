#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLANS = ROOT / "plans"
DOCS = ROOT / "docs" / "README.md"
PROMPTS = ROOT / "prompts" / "README.md"
CLOSURE = PLANS / "closure-record.json"
CANARY = PLANS / "vertical-canary.json"
STACK = PLANS / "molecular-stack-index.json"
DIRECTORIES = PLANS / "directory-state-machine-index.json"
FLOW = PLANS / "data-flow.json"

EXPECTED_PARENT = {
    "commit": "a27aa552f1c258e09f515b4a5d117ba37f4d6615",
    "tree": "71eaa3f4acafd0b004ccdff16e4aa14bc2599649",
}
EXPECTED_CANARY_DIGEST = "sha256:2146c02c23bbf87b6797900141c491a53f6936714b0b620a23016a2b20eaab79"
REQUIRED_ATOMS = {"INCEPTION-C0", "INCEPTION-C1", "INCEPTION-K", "A1", "A2R", "A2", "A3", "A4", "A5", "A6", "INCEPTION-E", "INCEPTION-X", "INCEPTION-D"}


class DocsError(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise DocsError(reason)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"NOT_OBJECT:{path}")
    return value


def validate(stack: dict, directories: dict, flow: dict, closure: dict, canary: dict, docs: str, prompts: str) -> None:
    require(stack.get("state") == "P6_PROFILE_DOCUMENTATION_CANDIDATE", "STACK_STATE")
    parent = stack.get("true_git_parent", {})
    require(parent.get("commit") == EXPECTED_PARENT["commit"] and parent.get("tree") == EXPECTED_PARENT["tree"], "PROFILE_X_PARENT_DRIFT")
    atoms = stack.get("atoms")
    require(isinstance(atoms, list), "STACK_ATOMS")
    indexed = {item.get("atom"): item for item in atoms if isinstance(item, dict)}
    require(set(indexed) == REQUIRED_ATOMS, "STACK_DENOMINATOR")
    require(indexed["INCEPTION-X"].get("shadow_review") == 4973663047, "PROFILE_X_SHADOW")
    require(indexed["INCEPTION-D"].get("state") in {"IN_PROGRESS", "P6_PROFILE_DOCS_CANDIDATE"}, "PROFILE_D_FALSE_COMPLETION")
    require(indexed["INCEPTION-D"].get("subject") is None, "PROFILE_D_SELF_RECEIPT")
    require(indexed["INCEPTION-E"].get("class") == "review-only", "SHADOW_CLASS")
    require(indexed["A2"].get("consumed_runtime_pin", {}).get("commit") == "cdfe74ac993cb0b4795fa80df237e8bb542409d2", "A2_RUNTIME_PIN")
    require(indexed["A2R"].get("subject", {}).get("commit") == "2ff4efe7bee3d12fb3063fed93631f8d323cd64a", "A2R_OWNER_HEAD")

    entries = directories.get("entries")
    require(isinstance(entries, list) and len(entries) >= 9, "DIRECTORY_DENOMINATOR")
    for entry in entries:
        for key in ("directory", "owner_interface", "state_machine", "dag_owner", "inputs", "outputs", "required_evidence_lane", "receipt_evidence_lane", "gates", "blockers", "next_transition", "claims_not_proven"):
            require(key in entry, f"DIRECTORY_FIELD:{key}")
        require(entry["blockers"], f"DIRECTORY_BLOCKER:{entry.get('directory')}")
        require(entry["gates"], f"DIRECTORY_GATE:{entry.get('directory')}")
        require(entry["next_transition"], f"DIRECTORY_NEXT:{entry.get('directory')}")

    projection = flow.get("closure_projection", {})
    require(projection == {
        "requirements_total": 15,
        "requirements_required_lane_satisfied": 1,
        "requirements_closure_credit": 0,
        "contradictions_total": 14,
        "contradictions_preserved": 14,
        "vertical_canary": "PLAN_ONLY",
        "profile_shadow": "BLOCKED_FOR_CLOSURE",
        "profile_release": "NOT_ADMITTED",
    }, "FLOW_CLOSURE_PROMOTION")
    require(isinstance(flow.get("forbidden_flows"), list) and len(flow["forbidden_flows"]) >= 7, "FORBIDDEN_FLOW_DENOMINATOR")
    for edge in flow.get("edges", []):
        require(edge.get("guard") and edge.get("evidence"), "FLOW_EDGE_GUARD")

    summary = closure.get("closure_summary", {})
    require(summary.get("requirements_total") == 15, "CLOSURE_REQUIREMENTS")
    require(summary.get("requirements_required_lane_satisfied") == 1, "CLOSURE_REQUIRED_LANES")
    require(summary.get("requirements_closure_credit") == 0, "CLOSURE_FALSE_CREDIT")
    require(summary.get("contradictions_total") == 14 and summary.get("contradictions_preserved") == 14, "CLOSURE_CONTRADICTIONS")
    require(summary.get("profile_shadow") == "BLOCKED_FOR_CLOSURE", "CLOSURE_SHADOW_PROMOTION")
    require(summary.get("profile_release_state") == "NOT_ADMITTED", "CLOSURE_RELEASE_PROMOTION")

    require(canary.get("state") == "PLAN_ONLY", "CANARY_FALSE_EXECUTION")
    require(canary.get("execution_receipt") is None, "CANARY_FALSE_RECEIPT")
    require(canary.get("contract_digest") == EXPECTED_CANARY_DIGEST, "CANARY_DIGEST")

    lower_docs = docs.lower()
    for text in ("15/15", "14/14", "blocked_for_closure", "plan_only", "advisory_only", "32268112684", "4973663047"):
        require(text in lower_docs, f"DOC_ROUTE_MISSING:{text}")
    for phase in ("P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"):
        require(phase in prompts, f"PROMPT_PHASE_MISSING:{phase}")
    require("sha256:dc4473b3195a738e55eb49c43661b6e1f4ea7f95c66749454776f2003b18ebc3" in prompts, "PROMPT_BUNDLE_DIGEST")
    require("hidden prior chat" in prompts.lower(), "PROMPT_ZERO_CONTEXT_LAW")


def verify() -> None:
    validate(load(STACK), load(DIRECTORIES), load(FLOW), load(CLOSURE), load(CANARY), DOCS.read_text(encoding="utf-8"), PROMPTS.read_text(encoding="utf-8"))
    print("PASS inception-d profile docs atoms=13 requirements=15 contradictions=14 canary=PLAN_ONLY")


def must_refuse(label: str, mutate) -> None:
    args = [load(STACK), load(DIRECTORIES), load(FLOW), load(CLOSURE), load(CANARY), DOCS.read_text(encoding="utf-8"), PROMPTS.read_text(encoding="utf-8")]
    mutate(args)
    try:
        validate(*args)
    except DocsError:
        return
    raise AssertionError(f"mutation accepted: {label}")


def selftest() -> None:
    tests = [
        ("drop stack atom", lambda a: a[0]["atoms"].pop()),
        ("false D completion", lambda a: a[0]["atoms"][-1].update({"state": "RELEASED"})),
        ("invent D self receipt", lambda a: a[0]["atoms"][-1].update({"subject": {"commit": "1" * 40, "tree": "2" * 40}})),
        ("collapse runtime pin", lambda a: a[0]["atoms"][5]["consumed_runtime_pin"].update({"commit": "2ff4efe7bee3d12fb3063fed93631f8d323cd64a"})),
        ("drop directory blocker", lambda a: a[1]["entries"][0].update({"blockers": []})),
        ("drop flow guard", lambda a: a[2]["edges"][0].update({"guard": ""})),
        ("promote closure credit", lambda a: a[2]["closure_projection"].update({"requirements_closure_credit": 1})),
        ("promote profile shadow", lambda a: a[2]["closure_projection"].update({"profile_shadow": "PASS"})),
        ("promote P5 closure", lambda a: a[3]["closure_summary"].update({"requirements_closure_credit": 15})),
        ("execute canary", lambda a: a[4].update({"state": "EXECUTED"})),
        ("invent canary receipt", lambda a: a[4].update({"execution_receipt": {"id": "fake"}})),
        ("hide prompt phase", lambda a: a.__setitem__(6, a[6].replace("P7", "Q7"))),
    ]
    for label, mutate in tests:
        must_refuse(label, mutate)
    print(f"PASS inception-d planted refusals={len(tests)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    selftest() if args.selftest else verify()
