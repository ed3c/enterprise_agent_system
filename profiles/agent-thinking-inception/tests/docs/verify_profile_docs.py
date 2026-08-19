#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
REQ = ROOT / "requirements"
PLANS = ROOT / "plans"
DOCS = ROOT / "docs" / "README.md"
PROMPTS = ROOT / "prompts" / "README.md"
CLOSURE = PLANS / "closure-record.json"
CANARY = PLANS / "vertical-canary.json"
RECEIPTS = ROOT / "evidence" / "convergence" / "receipt-index.json"
STACK = PLANS / "molecular-stack-index.json"
DIRECTORIES = PLANS / "directory-state-machine-index.json"
FLOW = PLANS / "data-flow.json"

EXPECTED_PARENT = {
    "commit": "fe2748e09a5222f439f09c5d0d71e486e1ade3e8",
    "tree": "0425916bea831c125702696544ae2848fdf9bd0e",
    "pull_request": 40,
    "shadow_review": 4974017388,
}
EXPECTED_GENERIC_X = {
    "commit": "8b1bfa38c103e1c064b8ef0aafecfc8f2a2642dc",
    "tree": "9c8fb0e8e25f357fdb695a94c4ab74fc3dcd4631",
    "shadow_review": 4973896050,
}
EXPECTED_PROFILE_E = {
    "commit": "9f25b94ca891faf0d926b0fc22b67be88925aa81",
    "tree": "1452d1b9931c70ef70ed3b7dec78cedc51d6db35",
    "shadow_review": 4973593318,
}
EXPECTED_CANARY_DIGEST = "sha256:7a881bbe4b2b9605d56838f5f1e9a3c76dbf45ebc1b0aa7a973fd1329f88efbb"
CURRENT_A1_RUN = 32259216877
STALE_A1_RUN = 32259476821
EXPECTED_DOC_PATHS = {
    "profiles/agent-thinking-inception/docs/README.md",
    "profiles/agent-thinking-inception/plans/data-flow.json",
    "profiles/agent-thinking-inception/plans/directory-state-machine-index.json",
    "profiles/agent-thinking-inception/plans/molecular-stack-index.json",
    "profiles/agent-thinking-inception/prompts/12-profile-docs-convergence.system.md",
    "profiles/agent-thinking-inception/prompts/README.md",
    "profiles/agent-thinking-inception/tests/docs/verify_profile_docs.py",
}
REQUIRED_ATOMS = {
    "INCEPTION-C0", "INCEPTION-C1", "INCEPTION-K",
    "A1", "A2R", "A2", "A3", "A4", "A5", "A6",
    "INCEPTION-E", "GENERIC-EAS-X", "INCEPTION-X", "INCEPTION-D", "EAS-H",
}
EXPECTED_RESIDUES = {
    "agent/inception-x-profile-convergence",
    "agent/inception-x-profile-convergence-v2",
    "#37",
    "#39",
    "agent/inception-d-profile-docs-v2",
    "agent/inception-d-profile-docs-v3",
}


class DocsError(ValueError):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise DocsError(reason)


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"NOT_OBJECT:{path}")
    return value


def source_denominator() -> tuple[int, int]:
    requirements: set[str] = set()
    for name in ("control-requirements.json", "assurance-requirements.json", "delivery-requirements.json"):
        shard = load(REQ / name)
        require(shard.get("schema_version") == "enterprise-agent-system/inception-requirement-shard/v1", f"SOURCE_SCHEMA:{name}")
        for item in shard.get("requirements", []):
            rid = item.get("requirement_id")
            require(isinstance(rid, str) and rid.startswith("REQ-PDF-INCEPTION-"), f"SOURCE_REQUIREMENT:{name}")
            require(rid not in requirements, f"SOURCE_REQUIREMENT_DUPLICATE:{rid}")
            requirements.add(rid)
    contradictions = load(REQ / "contradictions.json").get("items", [])
    require(len(requirements) == 15, "SOURCE_REQUIREMENTS")
    require({item.get("id") for item in contradictions} == {f"UNK-INCEPTION-{i:03d}" for i in range(1, 15)}, "SOURCE_CONTRADICTIONS")
    return len(requirements), len(contradictions)


def validate_stack(stack: dict) -> None:
    require(stack.get("schema_version") == "enterprise-agent-system/inception-profile-molecular-stack/v2", "STACK_SCHEMA")
    require(stack.get("state") == "P6_PROFILE_DOCUMENTATION_CANDIDATE", "STACK_STATE")
    parent = stack.get("true_git_parent", {})
    for key, value in EXPECTED_PARENT.items():
        require(parent.get(key) == value, f"PROFILE_X_PARENT_DRIFT:{key}")
    require(parent.get("verdict") == "ADMIT_FOR_P6_DOCUMENTATION_PREPARATION", "PROFILE_X_VERDICT")

    deps = {item.get("name"): item for item in stack.get("process_dependencies", [])}
    gx = deps.get("GENERIC_EAS_X", {})
    for key, value in EXPECTED_GENERIC_X.items():
        require(gx.get(key) == value, f"GENERIC_X_DRIFT:{key}")
    require(gx.get("relationship") == "PROCESS_EVIDENCE_DEPENDENCY_NOT_GIT_PARENT", "GENERIC_X_FALSE_GIT_PARENT")
    require(deps.get("PROFILE_D_VERIFICATION_OWNER", {}).get("issue") == 38, "DV_OWNER")
    require(deps.get("PROFILE_D_VERIFICATION_OWNER", {}).get("subject") is None, "DV_FALSE_SUBJECT")

    atoms = stack.get("atoms")
    require(isinstance(atoms, list), "STACK_ATOMS")
    indexed = {item.get("atom"): item for item in atoms if isinstance(item, dict)}
    require(set(indexed) == REQUIRED_ATOMS, "STACK_DENOMINATOR")
    require(indexed["INCEPTION-X"].get("pull_request") == 40, "PROFILE_X_PR")
    require(indexed["INCEPTION-X"].get("subject") == {"commit": EXPECTED_PARENT["commit"], "tree": EXPECTED_PARENT["tree"]}, "PROFILE_X_SUBJECT")
    require(indexed["INCEPTION-X"].get("shadow_review") == EXPECTED_PARENT["shadow_review"], "PROFILE_X_SHADOW")
    require(indexed["INCEPTION-X"].get("hosted_profile_x_gate") == "ABSENT", "PROFILE_X_HOSTED_GATE_FABRICATED")
    require(indexed["INCEPTION-X"].get("canary") == {
        "id": "INCEPTION-X-PUBLIC-NO-EFFECT-001",
        "digest": EXPECTED_CANARY_DIGEST,
        "state": "PLAN_ONLY",
        "execution_receipt": None,
    }, "STACK_CANARY")
    require(indexed["INCEPTION-D"].get("branch") == "agent/inception-d-profile-docs-v4", "PROFILE_D_BRANCH")
    require(indexed["INCEPTION-D"].get("state") == "IN_PROGRESS", "PROFILE_D_FALSE_COMPLETION")
    require(indexed["INCEPTION-D"].get("subject") is None, "PROFILE_D_SELF_RECEIPT")
    require(indexed["INCEPTION-D"].get("parent_subject") == {"commit": EXPECTED_PARENT["commit"], "tree": EXPECTED_PARENT["tree"]}, "PROFILE_D_PARENT")
    require(indexed["INCEPTION-E"].get("class") == "MULTI_PARENT_READ_ONLY_GIT_CHILD", "SHADOW_CLASS")
    require(indexed["INCEPTION-E"].get("shadow_review") == EXPECTED_PROFILE_E["shadow_review"], "PROFILE_E_SHADOW")
    require(indexed["A2"].get("consumed_runtime_pin", {}).get("commit") == "cdfe74ac993cb0b4795fa80df237e8bb542409d2", "A2_RUNTIME_PIN")
    require(indexed["A2R"].get("subject", {}).get("commit") == "2ff4efe7bee3d12fb3063fed93631f8d323cd64a", "A2R_OWNER_HEAD")
    require(indexed["A1"].get("hosted_runs") == [CURRENT_A1_RUN], "A1_RUN_DRIFT")

    relationships = stack.get("relationships", [])
    require(any(x.get("from") == "INCEPTION-X" and x.get("to") == "INCEPTION-D" and x.get("type") == "GIT_PARENT" for x in relationships), "PROFILE_D_GIT_PARENT_EDGE")
    require(not any(x.get("from") == "GENERIC-EAS-X" and x.get("to") == "INCEPTION-D" and x.get("type") == "GIT_PARENT" for x in relationships), "GENERIC_X_FALSE_D_PARENT")

    residue = stack.get("residue", [])
    require(len(residue) == 6, "RESIDUE_DENOMINATOR")
    refs = {item.get("ref") for item in residue}
    require(refs == EXPECTED_RESIDUES, "RESIDUE_REFS")
    require(all(item.get("authority") == "NONE" for item in residue), "RESIDUE_AUTHORITY")

    projection = stack.get("closure_projection", {})
    require(projection == {
        "requirements": 15,
        "contradictions": 14,
        "stronger_no_credit_lanes": 13,
        "required_lanes_satisfied": 1,
        "requirement_closure_credit": 0,
        "vertical_canary": "PLAN_ONLY",
        "vertical_canary_digest": EXPECTED_CANARY_DIGEST,
        "vertical_canary_execution_receipt": None,
        "hosted_profile_x_gate": "ABSENT",
        "highest_profile_state": "DETERMINISTIC_EVIDENCE_VERIFIED",
        "full_architecture": "BLOCKED_FOR_CLOSURE",
        "profile_release": "NOT_ADMITTED",
    }, "STACK_CLOSURE_PROJECTION")
    require(STALE_A1_RUN not in [run for item in atoms for run in item.get("hosted_runs", [])], "STALE_A1_RUN_IN_STACK")


def validate_directories(directories: dict) -> None:
    require(directories.get("schema_version") == "enterprise-agent-system/inception-directory-state-machine-index/v2", "DIRECTORY_SCHEMA")
    parent = directories.get("parent_profile_x", {})
    for key, value in EXPECTED_PARENT.items():
        require(parent.get(key) == value, f"DIRECTORY_PARENT:{key}")
    entries = directories.get("entries")
    require(isinstance(entries, list) and len(entries) == 15, "DIRECTORY_DENOMINATOR")
    phases = {entry.get("phase") for entry in entries}
    require({"P0", "P1", "P2", "P3-A1", "P3-A2R", "P3-A2", "P3-A3", "P3-A4", "P3-A5", "P3-A6", "P4", "P5", "P6", "P7"} <= phases, "DIRECTORY_PHASES")
    for entry in entries:
        for key in (
            "phase", "directory", "owner_interface", "state_machine", "dag_owner",
            "inputs", "outputs", "required_evidence_lane", "current_evidence_ceiling",
            "gates", "blockers", "next_owner", "claims_not_proven",
        ):
            require(key in entry, f"DIRECTORY_FIELD:{key}:{entry.get('phase')}")
        require(isinstance(entry["state_machine"], list) and entry["state_machine"], f"DIRECTORY_STATE_MACHINE:{entry.get('phase')}")
        require(entry["inputs"] and entry["outputs"], f"DIRECTORY_IO:{entry.get('phase')}")
        require(entry["gates"], f"DIRECTORY_GATE:{entry.get('phase')}")
        require(entry["blockers"], f"DIRECTORY_BLOCKER:{entry.get('phase')}")
        require(entry["next_owner"], f"DIRECTORY_NEXT:{entry.get('phase')}")
        require(entry["claims_not_proven"], f"DIRECTORY_CLAIMS:{entry.get('phase')}")
    p5 = next(x for x in entries if x["phase"] == "P5")
    require("hosted Profile-X Gate ABSENT" in p5["gates"], "DIRECTORY_HOSTED_X_GAP")
    p6 = next(x for x in entries if x["phase"] == "P6")
    require("hosted P6 verification must be supplied by external sibling #38" in p6["blockers"], "DIRECTORY_DV_GAP")


def validate_flow(flow: dict) -> None:
    require(flow.get("schema_version") == "enterprise-agent-system/inception-profile-data-flow/v2", "FLOW_SCHEMA")
    parent = flow.get("parent_profile_x", {})
    for key, value in EXPECTED_PARENT.items():
        require(parent.get(key) == value, f"FLOW_PARENT:{key}")
    node_ids = {node.get("id") for node in flow.get("nodes", [])}
    require({"SOURCE", "REQUIREMENTS", "CONTRACTS", "PROFILE_K", "A1", "A2R", "A2", "A3", "A4", "A5", "A6", "GENERIC_X", "PROFILE_E", "PROFILE_X", "PROFILE_D", "PROFILE_DV", "ROOT_D", "LOCAL_HANDOFF", "HUMAN"} == node_ids, "FLOW_NODE_DENOMINATOR")
    edges = flow.get("edges", [])
    require(len(edges) >= 20, "FLOW_EDGE_DENOMINATOR")
    for edge in edges:
        require(edge.get("from") in node_ids and edge.get("to") in node_ids, "FLOW_EDGE_NODE")
        require(edge.get("type") and edge.get("guard") and edge.get("evidence"), "FLOW_EDGE_GUARD")
    require(any(x.get("from") == "PROFILE_X" and x.get("to") == "PROFILE_D" and x.get("type") == "GIT_PARENT" for x in edges), "FLOW_D_GIT_PARENT")
    require(any(x.get("from") == "PROFILE_D" and x.get("to") == "PROFILE_DV" and x.get("type") == "EXTERNAL_VERIFICATION_REQUEST" for x in edges), "FLOW_DV_EDGE")

    forbidden = flow.get("forbidden_edges", [])
    require(len(forbidden) >= 14, "FORBIDDEN_FLOW_DENOMINATOR")
    required_forbidden = {
        ("SOURCE", "RUNTIME_PASS"),
        ("A2", "PROVIDER_OR_NETWORK_PASS"),
        ("A4", "ZERO_LEAKAGE_OR_LEGAL_PASS"),
        ("A6", "REAL_EXTERNAL_EFFECT_PASS"),
        ("OWNER_RECEIPTS", "INTEGRATED_EXECUTION"),
        ("MODEL_OR_JUDGE", "HUMAN_ADMITTED"),
        ("PROFILE_D", "TASK_OR_EFFECT_STATE"),
        ("GOOGLE_DOC_OR_SHEET", "CANONICAL_STATE"),
        ("PLAN_ONLY_CANARY", "EXECUTED"),
    }
    require(required_forbidden <= {(x.get("from"), x.get("to")) for x in forbidden}, "FORBIDDEN_FLOW_REQUIRED")
    require(all(x.get("reason") for x in forbidden), "FORBIDDEN_FLOW_REASON")
    residues = flow.get("residue_edges", [])
    require(len(residues) == 5 and all(x.get("authority") == "NONE" for x in residues), "FLOW_RESIDUE")

    projection = flow.get("closure_projection", {})
    require(projection == {
        "requirements_total": 15,
        "requirements_required_lane_satisfied": 1,
        "requirements_closure_credit": 0,
        "contradictions_total": 14,
        "contradictions_preserved": 14,
        "stronger_no_credit_lanes": 13,
        "vertical_canary": "PLAN_ONLY",
        "vertical_canary_digest": EXPECTED_CANARY_DIGEST,
        "vertical_canary_execution_receipt": None,
        "hosted_profile_x_gate": "ABSENT",
        "profile_shadow": "ADMIT_FOR_PROFILE_CONVERGENCE",
        "profile_x": "ADMIT_FOR_P6_DOCUMENTATION_PREPARATION",
        "highest_profile_state": "DETERMINISTIC_EVIDENCE_VERIFIED",
        "full_architecture": "BLOCKED_FOR_CLOSURE",
        "profile_release": "NOT_ADMITTED",
    }, "FLOW_CLOSURE_PROMOTION")


def validate_p5(closure: dict, canary: dict, receipts: dict) -> None:
    req_count, contradiction_count = source_denominator()
    require(req_count == 15 and contradiction_count == 14, "SOURCE_DENOMINATOR")
    require(closure.get("schema_version") == "enterprise-agent-system/inception-profile-closure/v3", "CLOSURE_SCHEMA")
    require(closure.get("source_subject", {}).get("class") == "SOURCE_PROPOSAL", "CLOSURE_SOURCE_PROMOTION")
    summary = closure.get("closure_summary", {})
    require(summary.get("requirements_total") == 15, "CLOSURE_REQUIREMENTS")
    require(summary.get("requirements_required_lane_satisfied") == 1, "CLOSURE_REQUIRED_LANES")
    require(summary.get("requirements_closure_credit") == 0, "CLOSURE_FALSE_CREDIT")
    require(summary.get("contradictions_total") == 14 and summary.get("contradictions_preserved") == 14, "CLOSURE_CONTRADICTIONS")
    require(summary.get("profile_shadow") == "ADMIT_FOR_PROFILE_CONVERGENCE", "CLOSURE_SHADOW")
    require(summary.get("generic_x") == "ADMIT_FOR_PROFILE_X_REBIND", "CLOSURE_GENERIC_X")
    require(summary.get("vertical_canary") == "PLAN_ONLY", "CLOSURE_CANARY")
    require(summary.get("highest_state") == "DETERMINISTIC_EVIDENCE_VERIFIED", "CLOSURE_STATE_PROMOTION")
    require(summary.get("full_architecture") == "BLOCKED_FOR_CLOSURE", "CLOSURE_FULL_PROMOTION")
    require(summary.get("profile_release_state") == "NOT_ADMITTED", "CLOSURE_RELEASE_PROMOTION")
    require(len(closure.get("stronger_lanes", [])) == 13, "CLOSURE_STRONGER_DENOMINATOR")
    require(all(row.get("closure_credit") == 0 for row in closure.get("requirements", [])), "CLOSURE_ROW_FALSE_CREDIT")

    require(canary.get("state") == "PLAN_ONLY", "CANARY_FALSE_EXECUTION")
    require(canary.get("execution_receipt") is None, "CANARY_FALSE_RECEIPT")
    require(canary.get("contract_digest") == EXPECTED_CANARY_DIGEST, "CANARY_DIGEST")
    require(canary.get("contract", {}).get("generic_x", {}).get("shadow_review") == EXPECTED_GENERIC_X["shadow_review"], "CANARY_GENERIC_X_REVIEW")
    require(canary.get("contract", {}).get("profile_shadow", {}).get("shadow_review") == EXPECTED_PROFILE_E["shadow_review"], "CANARY_PROFILE_E_REVIEW")

    require(receipts.get("schema_version") == "enterprise-agent-system/inception-profile-convergence-receipts/v3", "RECEIPT_SCHEMA")
    owners = {row.get("atom"): row for row in receipts.get("owners", [])}
    require(len(owners) == 7, "RECEIPT_OWNER_DENOMINATOR")
    require(owners.get("A1", {}).get("hosted_runs") == [CURRENT_A1_RUN], "RECEIPT_A1_RUN")
    machine_text = json.dumps(receipts, sort_keys=True)
    require(str(STALE_A1_RUN) not in machine_text, "STALE_A1_RUN_IN_CURRENT_RECEIPTS")
    require(receipts.get("local_handoff_contract", {}).get("queue_execution") == "NOT_PERFORMED", "HANDOFF_FALSE_EXECUTION")
    residues = receipts.get("residue", {}).get("superseded_branches", [])
    require(len(residues) == 2 and all(x.get("authority") == "NONE" for x in residues), "P5_RESIDUE_AUTHORITY")


def validate_docs_text(docs: str, prompts: str) -> None:
    lower_docs = docs.lower()
    required_docs = (
        EXPECTED_PARENT["commit"],
        str(EXPECTED_PARENT["shadow_review"]),
        EXPECTED_GENERIC_X["commit"],
        str(EXPECTED_GENERIC_X["shadow_review"]),
        EXPECTED_PROFILE_E["commit"],
        str(EXPECTED_PROFILE_E["shadow_review"]),
        str(CURRENT_A1_RUN),
        EXPECTED_CANARY_DIGEST,
        "profile-x hosted gate           absent",
        "plan_only",
        "execution receipt      null",
        "deterministic_evidence_verified",
        "blocked_for_closure",
        "not_admitted",
        "advisory_only",
        "authority none",
        "issue #38",
    )
    for text in required_docs:
        require(text.lower() in lower_docs, f"DOC_ROUTE_MISSING:{text}")
    require(str(STALE_A1_RUN) in docs and "historical" in lower_docs, "DOC_STALE_RUN_HISTORY_MISSING")

    for phase in ("P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7"):
        require(phase in prompts, f"PROMPT_PHASE_MISSING:{phase}")
    for blob in (
        "e786de9d2465d551bab625e03a8dbf3321bdb102",
        "53d6752f246062f537b24f14ad6ff2fb5253e654",
        "e3115597a6344b0fb26bc3f3e2d6beba973614ee",
        "c8073d5ccc250e61a4bb0e78c0e60744473ac40b",
        "884d8037653b8ffc89f825b7939cb03c455ec873",
        "7f855e4d3ae637354dc474c45bfc5cd6dc15cb7c",
    ):
        require(blob in prompts, f"PROMPT_BLOB:{blob}")
    require("sha256:dc4473b3195a738e55eb49c43661b6e1f4ea7f95c66749454776f2003b18ebc3" in prompts, "PROMPT_BUNDLE_DIGEST")
    require(EXPECTED_PARENT["commit"] in prompts and EXPECTED_CANARY_DIGEST in prompts, "PROMPT_P5_TRUTH")
    require(str(CURRENT_A1_RUN) in prompts, "PROMPT_CURRENT_A1_RUN")
    require(str(STALE_A1_RUN) in prompts and "historical" in prompts.lower(), "PROMPT_STALE_RUN_LAW")
    require("hidden prior-chat context" in prompts.lower(), "PROMPT_ZERO_CONTEXT_LAW")
    require("advisory_only" in prompts.lower(), "PROMPT_GOOGLE_BOUNDARY")


def verify_git_context() -> None:
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        parent_ok = subprocess.run(["git", "merge-base", "--is-ancestor", EXPECTED_PARENT["commit"], head], check=False).returncode == 0
        require(parent_ok, "GIT_PARENT_NOT_ANCESTOR")
        changed = set(subprocess.check_output(["git", "diff", "--name-only", f"{EXPECTED_PARENT['commit']}...HEAD"], text=True).splitlines())
        require(changed == EXPECTED_DOC_PATHS, f"DOC_PATH_LEASE:{sorted(changed ^ EXPECTED_DOC_PATHS)}")
        require(subprocess.run(["git", "diff", "--check", f"{EXPECTED_PARENT['commit']}...HEAD"], check=False).returncode == 0, "PATCH_HYGIENE")
    except FileNotFoundError as exc:
        raise DocsError("GIT_UNAVAILABLE") from exc


def validate(stack: dict, directories: dict, flow: dict, closure: dict, canary: dict, receipts: dict, docs: str, prompts: str) -> None:
    validate_stack(stack)
    validate_directories(directories)
    validate_flow(flow)
    validate_p5(closure, canary, receipts)
    validate_docs_text(docs, prompts)


def verify(*, git_context: bool = True) -> None:
    validate(load(STACK), load(DIRECTORIES), load(FLOW), load(CLOSURE), load(CANARY), load(RECEIPTS), DOCS.read_text(encoding="utf-8"), PROMPTS.read_text(encoding="utf-8"))
    if git_context:
        verify_git_context()
    print("PASS inception-d-v4 docs atoms=15 directories=15 requirements=15 contradictions=14 stronger=13 required_lanes=1 closure_credit=0 canary=PLAN_ONLY hosted_profile_x_gate=ABSENT")


def must_refuse(label: str, mutate) -> None:
    args = [load(STACK), load(DIRECTORIES), load(FLOW), load(CLOSURE), load(CANARY), load(RECEIPTS), DOCS.read_text(encoding="utf-8"), PROMPTS.read_text(encoding="utf-8")]
    mutate(args)
    try:
        validate(*args)
    except DocsError:
        return
    raise AssertionError(f"mutation accepted: {label}")


def selftest() -> None:
    tests = [
        ("old Profile-X parent", lambda a: a[0]["true_git_parent"].update({"commit": "a27aa552f1c258e09f515b4a5d117ba37f4d6615"})),
        ("old Profile-X Shadow", lambda a: a[0]["true_git_parent"].update({"shadow_review": 4973663047})),
        ("current stale A1 run", lambda a: next(x for x in a[0]["atoms"] if x["atom"] == "A1").update({"hosted_runs": [STALE_A1_RUN]})),
        ("drop stack atom", lambda a: a[0]["atoms"].pop()),
        ("false D completion", lambda a: next(x for x in a[0]["atoms"] if x["atom"] == "INCEPTION-D").update({"state": "RELEASED"})),
        ("invent D self receipt", lambda a: next(x for x in a[0]["atoms"] if x["atom"] == "INCEPTION-D").update({"subject": {"commit": "1" * 40, "tree": "2" * 40}})),
        ("give residue authority", lambda a: a[0]["residue"][0].update({"authority": "PASS"})),
        ("false generic-X D Git parent", lambda a: a[0]["relationships"].append({"from": "GENERIC-EAS-X", "to": "INCEPTION-D", "type": "GIT_PARENT"})),
        ("collapse runtime pin", lambda a: next(x for x in a[0]["atoms"] if x["atom"] == "A2")["consumed_runtime_pin"].update({"commit": "2ff4efe7bee3d12fb3063fed93631f8d323cd64a"})),
        ("drop directory blocker", lambda a: a[1]["entries"][0].update({"blockers": []})),
        ("drop directory claims", lambda a: a[1]["entries"][0].update({"claims_not_proven": []})),
        ("fabricate hosted X gate", lambda a: next(x for x in a[1]["entries"] if x["phase"] == "P5")["gates"].remove("hosted Profile-X Gate ABSENT")),
        ("drop flow guard", lambda a: a[2]["edges"][0].update({"guard": ""})),
        ("drop forbidden promotion edge", lambda a: a[2]["forbidden_edges"].clear()),
        ("promote flow closure credit", lambda a: a[2]["closure_projection"].update({"requirements_closure_credit": 1})),
        ("promote flow full architecture", lambda a: a[2]["closure_projection"].update({"full_architecture": "PASS"})),
        ("promote P5 closure credit", lambda a: a[3]["closure_summary"].update({"requirements_closure_credit": 15})),
        ("promote Human state", lambda a: a[3]["closure_summary"].update({"highest_state": "HUMAN_ADMITTED"})),
        ("execute canary", lambda a: a[4].update({"state": "EXECUTED"})),
        ("invent canary receipt", lambda a: a[4].update({"execution_receipt": {"id": "fake"}})),
        ("reintroduce stale A1 receipt", lambda a: next(x for x in a[5]["owners"] if x["atom"] == "A1").update({"hosted_runs": [STALE_A1_RUN]})),
        ("hide current parent in docs", lambda a: a.__setitem__(6, a[6].replace(EXPECTED_PARENT["commit"], "0" * 40))),
        ("hide prompt phase", lambda a: a.__setitem__(7, a[7].replace("P7", "Q7"))),
        ("old canary digest in prompts", lambda a: a.__setitem__(7, a[7].replace(EXPECTED_CANARY_DIGEST, "sha256:" + "0" * 64))),
    ]
    for label, mutate in tests:
        must_refuse(label, mutate)
    print(f"PASS inception-d-v4 planted refusals={len(tests)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--skip-git-context", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        selftest()
    else:
        verify(git_context=not args.skip_git_context)
