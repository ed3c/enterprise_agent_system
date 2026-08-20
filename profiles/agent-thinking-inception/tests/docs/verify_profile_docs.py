#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "README.md"
FLOW = ROOT / "plans" / "data-flow.json"
STATE = ROOT / "plans" / "directory-state-machine-index.json"
STACK = ROOT / "plans" / "molecular-stack-index.json"
PROMPTS = ROOT / "prompts" / "README.md"
P6_PROMPT = ROOT / "prompts" / "12-profile-docs-convergence.system.md"
CLOSURE = ROOT / "plans" / "closure-record.json"
CANARY = ROOT / "plans" / "vertical-canary.json"
RECEIPTS = ROOT / "evidence" / "convergence" / "receipt-index.json"

PX = {
    "pull_request": 80,
    "commit": "df4cd19d9acbedcbd0b00245b6339cc9ef7e99e0",
    "tree": "9290a2822ba30309a9d44933ce0ea4d640501a39",
    "external_verification_run": 32321499909,
    "shadow_review": 4978282030,
}
EAS_A = {
    "pull_request": 68,
    "commit": "250717db1cad584d50890c0d851153fa2cd755e8",
    "tree": "fbf6a75b6e89e906f227110dc5a61e4355b8a891",
    "verification_run": 32295871632,
    "shadow_review": 4976213414,
    "authority": "ADVISORY_ONLY",
    "relationship": "PROCESS_DEPENDENCY_NOT_GIT_PARENT",
}
CANARY_DIGEST = "sha256:869842575cae80c62227699f576728f3331fa25a573a3cc27c052f23f32944c2"
STALE_PRS = {40, 44, 57, 59, 67, 71}
PROMPT_FILES = {
    "00-source-auditor.system.md",
    "01-profile-contract-worker.system.md",
    "02-tech-lead-profile-controller.system.md",
    "03-profile-worker-envelope.system.md",
    "10-shadow-architect-profile.system.md",
    "11-profile-convergence.system.md",
    "12-profile-docs-convergence.system.md",
}


class DocsError(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise DocsError(reason)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"NOT_OBJECT:{path}")
    return value


def bundle() -> dict[str, Any]:
    return {
        "doc": DOC.read_text(encoding="utf-8"),
        "flow": load_json(FLOW),
        "state": load_json(STATE),
        "stack": load_json(STACK),
        "prompts": PROMPTS.read_text(encoding="utf-8"),
        "p6_prompt": P6_PROMPT.read_text(encoding="utf-8"),
        "closure": load_json(CLOSURE),
        "canary": load_json(CANARY),
        "receipts": load_json(RECEIPTS),
    }


def verify_parent(value: dict[str, Any], label: str) -> None:
    parent = value.get("parent_profile_x")
    require(isinstance(parent, dict), f"{label}_PARENT")
    for key, expected in PX.items():
        require(parent.get(key) == expected, f"{label}_PARENT_{key.upper()}")


def verify_machine(b: dict[str, Any]) -> None:
    flow = b["flow"]
    state = b["state"]
    stack = b["stack"]
    closure = b["closure"]
    canary = b["canary"]
    receipts = b["receipts"]

    require(flow.get("schema_version") == "enterprise-agent-system/inception-profile-data-flow/v3", "FLOW_SCHEMA")
    require(state.get("schema_version") == "enterprise-agent-system/inception-directory-state-machine-index/v3", "STATE_SCHEMA")
    require(stack.get("schema_version") == "enterprise-agent-system/inception-molecular-stack-index/v5", "STACK_SCHEMA")
    verify_parent(flow, "FLOW")
    verify_parent(state, "STATE")

    flow_eas = flow.get("eas_a", {})
    for key, expected in EAS_A.items():
        require(flow_eas.get(key) == expected, f"FLOW_EAS_A_{key.upper()}")
    require(flow_eas.get("google_connectivity") == "NOT_PERFORMED", "FLOW_GOOGLE_CONNECTIVITY")
    require(flow_eas.get("google_write") == "NOT_PERFORMED", "FLOW_GOOGLE_WRITE")
    require(flow_eas.get("source_correctness") == "NOT_PROVEN", "FLOW_SOURCE_CORRECTNESS")

    p5 = next((x for x in state.get("entries", []) if x.get("phase") == "P5-PROFILE"), None)
    p6 = next((x for x in state.get("entries", []) if x.get("phase") == "P6"), None)
    p7 = next((x for x in state.get("entries", []) if x.get("phase") == "P7"), None)
    require(p5 is not None and "32321499909" in p5.get("gate", "") and "4978282030" in p5.get("gate", ""), "STATE_P5_CURRENT")
    require(p6 is not None and p6.get("canonical_owner") == "INCEPTION-D / #23", "STATE_P6_OWNER")
    require(p6.get("evidence_ceiling") == "DOCUMENTATION_AND_TRACEABILITY_ONLY", "STATE_P6_CEILING")
    require(p7 is not None and p7.get("evidence_ceiling") == "NOT_CURRENT_YET", "STATE_P7_CURRENT")

    current = {x.get("atom"): x for x in stack.get("current_atoms", [])}
    px = current.get("PROFILE-X-V4", {})
    require(px.get("pull_request") == 80 and px.get("commit") == PX["commit"] and px.get("tree") == PX["tree"], "STACK_PROFILE_X")
    require(px.get("verification_run") == 32321499909 and px.get("shadow_review") == 4978282030, "STACK_PROFILE_X_RECEIPTS")
    eas = current.get("EAS-A", {})
    require(eas.get("authority") == "ADVISORY_ONLY" and eas.get("relationship") == "PROCESS_DEPENDENCY_NOT_GIT_PARENT", "STACK_EAS_A")
    stale = stack.get("stale_or_superseded", [])
    observed_stale = {x.get("pull_request") for x in stale if isinstance(x.get("pull_request"), int) and x.get("disposition") == "STALE_PENDING_EAS_A_REBIND"}
    require(observed_stale == STALE_PRS, "STACK_STALE_DENOMINATOR")
    require(all(x.get("authority") == "NONE" for x in stale), "STACK_STALE_AUTHORITY")

    summary = closure.get("closure_summary", {})
    require(summary.get("requirements_total") == 15, "CLOSURE_REQUIREMENTS")
    require(summary.get("requirements_required_lane_satisfied") == 1, "CLOSURE_REQUIRED_LANES")
    require(summary.get("requirements_closure_credit") == 0, "CLOSURE_CREDIT")
    require(summary.get("contradictions_total") == 14, "CLOSURE_CONTRADICTIONS")
    require(summary.get("full_architecture") == "BLOCKED_FOR_CLOSURE", "FULL_CLOSURE")
    require(summary.get("profile_release_state") == "NOT_ADMITTED", "PROFILE_RELEASE")
    require(len(closure.get("stronger_lanes", [])) == 13, "STRONGER_DENOMINATOR")
    require(all(x.get("closure_credit") == 0 for x in closure.get("requirements", [])), "REQUIREMENT_CREDIT")

    inherited_eas = closure.get("eas_a_projection", {})
    for key, expected in EAS_A.items():
        require(inherited_eas.get(key) == expected, f"CLOSURE_EAS_A_{key.upper()}")
    require(inherited_eas.get("google_connectivity") == "NOT_PERFORMED", "CLOSURE_GOOGLE_CONNECTIVITY")
    require(inherited_eas.get("google_write") == "NOT_PERFORMED", "CLOSURE_GOOGLE_WRITE")
    require(inherited_eas.get("source_correctness") == "NOT_PROVEN", "CLOSURE_SOURCE_CORRECTNESS")

    require(canary.get("state") == "PLAN_ONLY" and canary.get("execution_receipt") is None, "CANARY_EXECUTION")
    require(canary.get("contract_digest") == CANARY_DIGEST, "CANARY_DIGEST")
    require(receipts.get("vertical_canary", {}).get("digest") == CANARY_DIGEST, "RECEIPT_CANARY_DIGEST")
    require(receipts.get("vertical_canary", {}).get("state") == "PLAN_ONLY", "RECEIPT_CANARY_STATE")
    require(receipts.get("closure", {}).get("closure_credit") == 0, "RECEIPT_CLOSURE_CREDIT")

    flow_projection = flow.get("closure_projection", {})
    require(flow_projection == {
        "requirements_total": 15,
        "requirements_required_lane_satisfied": 1,
        "requirements_closure_credit": 0,
        "contradictions_total": 14,
        "contradictions_preserved": 14,
        "stronger_no_credit_lanes": 13,
        "vertical_canary": "PLAN_ONLY",
        "vertical_canary_digest": CANARY_DIGEST,
        "vertical_execution_receipt": None,
        "profile_x_external_verification": "32321499909_PASS",
        "profile_x_owned_hosted_workflow": "ABSENT",
        "full_architecture": "BLOCKED_FOR_CLOSURE",
        "profile_release": "NOT_ADMITTED",
    }, "FLOW_CLOSURE_PROJECTION")


def verify_docs(b: dict[str, Any]) -> None:
    corpus = "\n".join((b["doc"], b["prompts"], b["p6_prompt"]))
    required = (
        "Profile-X v4 PR #80",
        PX["commit"], PX["tree"], "32321499909", "4978282030",
        "ADVISORY_ONLY", "PROCESS_DEPENDENCY_NOT_GIT_PARENT",
        "Google connectivity", "NOT_PERFORMED", "source correctness", "NOT_PROVEN",
        "requirements", "15", "contradictions", "14", "stronger no-credit lanes", "13",
        "closure credit", "0", "PLAN_ONLY", CANARY_DIGEST,
        "BLOCKED_FOR_CLOSURE", "authority NONE",
    )
    for token in required:
        require(token in corpus, f"DOC_TOKEN:{token}")
    require("State Machine" in b["doc"] and "Molecular Stack" in b["doc"] and "Guarded data flow" in b["doc"], "DOC_STRUCTURE")
    require("prior chat memory" in b["p6_prompt"].lower(), "PROMPT_FRESH_SESSION")
    require("Evidence ceiling" in b["p6_prompt"] and "Required receipt" in b["p6_prompt"] and "Stop conditions" in b["p6_prompt"] and "Handoff" in b["p6_prompt"], "PROMPT_FIELDS")
    require("Google Docs/Sheets" in b["prompts"] and "ADVISORY_ONLY" in b["prompts"], "PROMPT_GOOGLE_AUTHORITY")
    for name in PROMPT_FILES:
        require((ROOT / "prompts" / name).is_file(), f"PROMPT_FILE:{name}")
    require("P7" in b["prompts"] and "Local Handoff" in b["prompts"], "PROMPT_P7_ROUTE")


def validate(b: dict[str, Any]) -> None:
    verify_machine(b)
    verify_docs(b)


def verify() -> None:
    b = bundle()
    validate(b)
    print("PASS Profile-D v5 docs requirements=15 contradictions=14 stronger=13 lanes=1 credit=0 canary=PLAN_ONLY")


def must_refuse(label: str, mutate: Callable[[dict[str, Any]], None], expected: str) -> None:
    b = bundle()
    mutate(b)
    try:
        validate(b)
    except DocsError as exc:
        require(expected in str(exc), f"WRONG_REFUSAL:{label}:{exc}")
        return
    raise AssertionError(f"mutation accepted: {label}")


def selftest() -> None:
    cases: list[tuple[str, Callable[[dict[str, Any]], None], str]] = [
        ("parent commit drift", lambda b: b["flow"]["parent_profile_x"].__setitem__("commit", "0" * 40), "FLOW_PARENT_COMMIT"),
        ("parent verify drift", lambda b: b["state"]["parent_profile_x"].__setitem__("external_verification_run", 1), "STATE_PARENT_EXTERNAL_VERIFICATION_RUN"),
        ("eas-a canonical", lambda b: b["flow"]["eas_a"].__setitem__("authority", "CANONICAL"), "FLOW_EAS_A_AUTHORITY"),
        ("eas-a false parent relationship", lambda b: b["flow"]["eas_a"].__setitem__("relationship", "GIT_PARENT"), "FLOW_EAS_A_RELATIONSHIP"),
        ("google connectivity", lambda b: b["flow"]["eas_a"].__setitem__("google_connectivity", "PASS"), "FLOW_GOOGLE_CONNECTIVITY"),
        ("google write", lambda b: b["closure"]["eas_a_projection"].__setitem__("google_write", "PASS"), "CLOSURE_GOOGLE_WRITE"),
        ("source correctness", lambda b: b["closure"]["eas_a_projection"].__setitem__("source_correctness", "SUPPORTED"), "CLOSURE_SOURCE_CORRECTNESS"),
        ("requirements", lambda b: b["closure"]["closure_summary"].__setitem__("requirements_total", 14), "CLOSURE_REQUIREMENTS"),
        ("required lane promotion", lambda b: b["closure"]["closure_summary"].__setitem__("requirements_required_lane_satisfied", 2), "CLOSURE_REQUIRED_LANES"),
        ("closure credit", lambda b: b["closure"]["closure_summary"].__setitem__("requirements_closure_credit", 1), "CLOSURE_CREDIT"),
        ("contradiction loss", lambda b: b["closure"]["closure_summary"].__setitem__("contradictions_total", 13), "CLOSURE_CONTRADICTIONS"),
        ("stronger loss", lambda b: b["closure"]["stronger_lanes"].pop(), "STRONGER_DENOMINATOR"),
        ("requirement credit", lambda b: b["closure"]["requirements"][0].__setitem__("closure_credit", 1), "REQUIREMENT_CREDIT"),
        ("canary executed", lambda b: b["canary"].update({"state": "EXECUTED", "execution_receipt": "fake"}), "CANARY_EXECUTION"),
        ("canary digest", lambda b: b["canary"].__setitem__("contract_digest", "sha256:" + "0" * 64), "CANARY_DIGEST"),
        ("receipt canary", lambda b: b["receipts"]["vertical_canary"].__setitem__("state", "EXECUTED"), "RECEIPT_CANARY_STATE"),
        ("full closure", lambda b: b["closure"]["closure_summary"].__setitem__("full_architecture", "PASS"), "FULL_CLOSURE"),
        ("release", lambda b: b["closure"]["closure_summary"].__setitem__("profile_release_state", "ADMITTED"), "PROFILE_RELEASE"),
        ("stack profile x", lambda b: next(x for x in b["stack"]["current_atoms"] if x["atom"] == "PROFILE-X-V4").__setitem__("commit", "0" * 40), "STACK_PROFILE_X"),
        ("stack stale authority", lambda b: b["stack"]["stale_or_superseded"][0].__setitem__("authority", "CURRENT"), "STACK_STALE_AUTHORITY"),
        ("stack stale denominator", lambda b: b["stack"]["stale_or_superseded"].__setitem__(slice(0, 1), []), "STACK_STALE_DENOMINATOR"),
        ("p7 current", lambda b: next(x for x in b["state"]["entries"] if x["phase"] == "P7").__setitem__("evidence_ceiling", "CURRENT"), "STATE_P7_CURRENT"),
        ("p6 authority widening", lambda b: next(x for x in b["state"]["entries"] if x["phase"] == "P6").__setitem__("evidence_ceiling", "RUNTIME_PASS"), "STATE_P6_CEILING"),
        ("flow projection promotion", lambda b: b["flow"]["closure_projection"].__setitem__("requirements_closure_credit", 15), "FLOW_CLOSURE_PROJECTION"),
        (
            "docs stale parent",
            lambda b: (
                b.__setitem__("doc", b["doc"].replace(PX["commit"], "0" * 40)),
                b.__setitem__("prompts", b["prompts"].replace(PX["commit"], "0" * 40)),
                b.__setitem__("p6_prompt", b["p6_prompt"].replace(PX["commit"], "0" * 40)),
            ),
            f"DOC_TOKEN:{PX['commit']}",
        ),
        (
            "docs canary promotion",
            lambda b: (
                b.__setitem__("doc", b["doc"].replace("PLAN_ONLY", "EXECUTED")),
                b.__setitem__("prompts", b["prompts"].replace("PLAN_ONLY", "EXECUTED")),
                b.__setitem__("p6_prompt", b["p6_prompt"].replace("PLAN_ONLY", "EXECUTED")),
            ),
            "DOC_TOKEN:PLAN_ONLY",
        ),
        ("prompt loses fresh session", lambda b: b.__setitem__("p6_prompt", b["p6_prompt"].replace("Prior chat memory is not an execution\ninput.", "")), "PROMPT_FRESH_SESSION"),
        ("prompt google authority", lambda b: b.__setitem__("prompts", b["prompts"].replace("ADVISORY_ONLY", "CANONICAL")), "PROMPT_GOOGLE_AUTHORITY"),
    ]
    for label, mutate, expected in cases:
        must_refuse(label, mutate, expected)
    require(len(cases) == 28, "SELFTEST_DENOMINATOR")
    print("PASS Profile-D v5 planted mutations 28/28")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    selftest() if args.selftest else verify()


if __name__ == "__main__":
    try:
        main()
    except (DocsError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}")
        raise SystemExit(1)
