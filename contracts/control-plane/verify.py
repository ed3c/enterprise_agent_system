#!/usr/bin/env python3
"""Zero-dependency semantic gate for enterprise_agent_system control-plane JSON."""

from __future__ import annotations
import argparse, copy, json, re, sys
from pathlib import Path
from typing import Any

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REPO = re.compile(r"^[^/\s]+/[^/\s]+$")
ISSUE = re.compile(r"^https://github\.com/[^/]+/[^/]+/issues/[0-9]+$")
SECRET = re.compile(r"(?i)(PRIVATE KEY|(?:password|secret|token|cookie|session)\s*[:=]\s*\S{6,}|/Users/|/home/)")
VERSIONS = {
 "enterprise-agent-system/source-subject/v1",
 "enterprise-agent-system/cross-repo-binding/v1",
 "enterprise-agent-system/closure-record/v1",
 "enterprise-agent-system/orchestration-run/v1",
}
STATES = {"PASS","FAIL","ABSENT","NOT_IMPLEMENTED","NOT_EXERCISED","SKIPPED_BY_POLICY",
          "STALE","BLOCKED","PARTIAL","HUMAN_ADMIT_REQUIRED","RELEASED"}

class Refusal(ValueError): pass

def req(ok: bool, reason: str) -> None:
    if not ok: raise Refusal(reason)

def strings(v: Any):
    if isinstance(v, str): yield v
    elif isinstance(v, list):
        for x in v: yield from strings(x)
    elif isinstance(v, dict):
        for k, x in v.items():
            yield k; yield from strings(x)

def exact(v: dict, fields: set[str], name: str) -> None:
    req(set(v) == fields, f"{name}_FIELDS:missing={sorted(fields-set(v))}:unknown={sorted(set(v)-fields)}")

def source(v: dict) -> None:
    fields={"schema_version","subject_id","source_kind","locator","identity","data_class",
            "egress_allowed","captured_at","content_digest","claims_not_proven"}
    exact(v,fields,"SOURCE")
    req(v["subject_id"].startswith("SRC-"),"SOURCE_ID")
    req(SHA256.fullmatch(v["content_digest"]) is not None,"CONTENT_DIGEST")
    req(v["claims_not_proven"],"CLAIMS_NOT_PROVEN_EMPTY")
    if v["data_class"]=="LOCAL_ONLY": req(v["egress_allowed"] is False,"LOCAL_ONLY_REMOTE_EGRESS")
    identity=v["identity"]; kind=identity.get("identity_kind")
    req(kind in {"GIT","REVISION","CONTENT_ONLY"},"IDENTITY_KIND")
    if kind=="GIT":
        req(REPO.fullmatch(identity.get("repository","")) is not None,"GIT_REPOSITORY")
        req(SHA40.fullmatch(identity.get("commit","")) is not None,"MUTABLE_SUBJECT")
        req(SHA40.fullmatch(identity.get("tree","")) is not None,"MUTABLE_SUBJECT")
    if kind=="REVISION": req(bool(identity.get("revision")),"REVISION_ABSENT")

def binding(v: dict) -> None:
    fields={"schema_version","binding_id","source_subject_id","owner","interfaces","consumers","state","claims_not_proven"}
    exact(v,fields,"BINDING")
    req(REPO.fullmatch(v["owner"].get("repository","")) is not None,"OWNER_REPOSITORY")
    seen=set()
    for item in v["interfaces"]:
        iid=item.get("interface_id",""); owner=item.get("owner_repository","")
        req(iid and REPO.fullmatch(owner) is not None,"INTERFACE_OWNER")
        req(iid not in seen,f"DUPLICATE_INTERFACE:{iid}"); seen.add(iid)
        if item.get("implementation_state") in {"IMPLEMENTED","PASS"}:
            req(isinstance(item.get("digest"),str) and SHA256.fullmatch(item["digest"]) is not None,
                f"IMPLEMENTED_WITHOUT_DIGEST:{iid}")
        if iid.startswith("runtime-env/dual-agent/"):
            req(owner=="ed3c/runtime-env",f"DUPLICATE_RUNTIME_SCHEMA_AUTHORITY:{iid}")
    req(len(v["consumers"])==len(set(v["consumers"])),"DUPLICATE_CONSUMER")

def closure(v: dict) -> None:
    fields={"schema_version","problem_id","source_subject_id","owner","state_machine","evidence",
            "blockers","next_transition","human_owned","claims_not_proven"}
    exact(v,fields,"CLOSURE")
    req(REPO.fullmatch(v["owner"].get("repository","")) is not None,"OWNER_REPOSITORY")
    req(ISSUE.fullmatch(v["owner"].get("issue","")) is not None,"OWNER_ISSUE")
    lanes=set()
    for item in v["evidence"]:
        lane=item.get("lane"); required=item.get("required_lane"); state=item.get("state")
        req(lane==required,f"LANE_SUBSTITUTION:{lane}->{required}")
        req(lane not in lanes,f"DUPLICATE_EVIDENCE_LANE:{lane}"); lanes.add(lane)
        req(state in STATES,f"INVALID_EVIDENCE_STATE:{state}")
        subject=item.get("subject")
        if state in {"PASS","RELEASED"}: req(subject is not None or lane=="SOURCE",f"PASS_WITHOUT_SUBJECT:{lane}")
        if subject and ("commit" in subject or "tree" in subject):
            req(SHA40.fullmatch(subject.get("commit","")) is not None,f"MUTABLE_SUBJECT:{lane}")
            req(SHA40.fullmatch(subject.get("tree","")) is not None,f"MUTABLE_SUBJECT:{lane}")
    for item in v["blockers"]:
        req(ISSUE.fullmatch(item.get("owner_issue","")) is not None,f"BLOCKER_WITHOUT_OWNER:{item.get('id')}")
    req(v["human_owned"],"HUMAN_BOUNDARY_EMPTY")
    req(v["claims_not_proven"],"CLAIMS_NOT_PROVEN_EMPTY")

def prefix(path: str) -> str: return path.split("*",1)[0].rstrip("/")
def overlap(a: str,b: str) -> bool:
    a,b=prefix(a),prefix(b); return a==b or a.startswith(b+"/") or b.startswith(a+"/")

def orchestration(v: dict) -> None:
    fields={"schema_version","run_id","request_subject","tasks","leases","canonical_reducer","shadow","authority","state"}
    exact(v,fields,"ORCHESTRATION")
    req(SHA40.fullmatch(v["request_subject"].get("commit","")) is not None,"MUTABLE_SUBJECT")
    req(SHA40.fullmatch(v["request_subject"].get("tree","")) is not None,"MUTABLE_SUBJECT")
    tasks=v["tasks"]; ids=[x["id"] for x in tasks]; idset=set(ids)
    req(len(ids)==len(idset),"DUPLICATE_TASK")
    remaining={}
    for task in tasks:
        start=set(task["start_dependencies"]); complete=set(task["completion_dependencies"])
        req(complete.issubset(start),f"COMPLETION_EDGE_WITHOUT_START_EDGE:{task['id']}")
        for dep in start|complete:
            req(dep in idset and dep!=task["id"],f"UNKNOWN_OR_SELF_DEPENDENCY:{task['id']}:{dep}")
        remaining[task["id"]]=complete
    while remaining:
        ready={k for k,d in remaining.items() if not d}; req(bool(ready),"CYCLIC_COMPLETION_DAG")
        for k in ready: remaining.pop(k)
        for d in remaining.values(): d.difference_update(ready)
    leases={x["task_id"]:x for x in v["leases"]}; req(set(leases)==idset,"TASK_LEASE_MISMATCH")
    active=[x for x in tasks if x["state"] in {"READY","ACTIVE","CANDIDATE"}]
    for i,left in enumerate(active):
        for right in active[i+1:]:
            for a in leases[left["id"]]["paths"]:
                for b in leases[right["id"]]["paths"]:
                    req(not overlap(a,b),f"OVERLAPPING_PATH_LEASE:{left['id']}:{right['id']}")
            req(set(leases[left["id"]]["resources"]).isdisjoint(leases[right["id"]]["resources"]),
                f"OVERLAPPING_RESOURCE_LEASE:{left['id']}:{right['id']}")
    req(v["canonical_reducer"].get("may_commit")==["TASK_STATE"],"REDUCER_AUTHORITY_WIDENED")
    shadow=v["shadow"]
    req(shadow.get("read_only") is True and shadow.get("separate_evaluation_path") is True,"SHADOW_NOT_INDEPENDENT")
    req(shadow.get("may_commit")==[],"SHADOW_SECOND_STATE_WRITER")
    forbidden=set(v["authority"].get("automation_forbidden",[]))
    for op in {"merge","permission_change","semantic_conflict_resolution","release","rollback"}:
        req(op in forbidden,f"AUTOMATION_AUTHORITY_WIDENED:{op}")

def validate(v: dict) -> None:
    req(not any(SECRET.search(s) for s in strings(v)),"SECRET_SESSION_OR_HOST_PATH")
    version=v.get("schema_version"); req(version in VERSIONS,f"UNKNOWN_SCHEMA_VERSION:{version}")
    {"enterprise-agent-system/source-subject/v1":source,
     "enterprise-agent-system/cross-repo-binding/v1":binding,
     "enterprise-agent-system/closure-record/v1":closure,
     "enterprise-agent-system/orchestration-run/v1":orchestration}[version](v)

def load(path: Path) -> dict:
    v=json.loads(path.read_text(encoding="utf-8")); req(isinstance(v,dict),f"ROOT_NOT_OBJECT:{path}"); return v

def selftest(directory: Path) -> None:
    names=["source-subject.example.json","cross-repo-binding.example.json",
           "closure-record.example.json","orchestration-run.example.json"]
    values={name:load(directory/name) for name in names}
    for v in values.values(): validate(v)
    mutations=[
      ("LOCAL_ONLY_REMOTE_EGRESS","source-subject.example.json",lambda v:(v.update(data_class="LOCAL_ONLY",egress_allowed=True))),
      ("DUPLICATE_RUNTIME_SCHEMA_AUTHORITY","cross-repo-binding.example.json",lambda v:v["interfaces"][2].update(owner_repository="ed3c/enterprise_agent_system")),
      ("IMPLEMENTED_WITHOUT_DIGEST","cross-repo-binding.example.json",lambda v:v["interfaces"][0].update(implementation_state="IMPLEMENTED",digest=None)),
      ("LANE_SUBSTITUTION","closure-record.example.json",lambda v:v["evidence"][3].update(required_lane="TASK")),
      ("BLOCKER_WITHOUT_OWNER","closure-record.example.json",lambda v:v["blockers"][0].update(owner_issue="missing")),
      ("MUTABLE_SUBJECT","orchestration-run.example.json",lambda v:v["request_subject"].update(commit="main")),
      ("COMPLETION_EDGE_WITHOUT_START_EDGE","orchestration-run.example.json",lambda v:v["tasks"][1].update(start_dependencies=[])),
      ("OVERLAPPING_PATH_LEASE","orchestration-run.example.json",lambda v:(v["tasks"][1].update(state="ACTIVE"),v["leases"][1].update(paths=["contracts/control-plane/new/**"]))),
      ("SHADOW_SECOND_STATE_WRITER","orchestration-run.example.json",lambda v:v["shadow"].update(may_commit=["TASK_STATE"])),
      ("SECRET_SESSION_OR_HOST_PATH","source-subject.example.json",lambda v:v["locator"].update(navigation_ref="token=abcdef123456")),
    ]
    for expected,name,mutate in mutations:
        v=copy.deepcopy(values[name]); mutate(v)
        try: validate(v)
        except Refusal as exc: req(expected in str(exc),f"WRONG_REFUSAL:{expected}:{exc}")
        else: raise Refusal(f"MUTATION_DID_NOT_FAIL:{expected}")
    print(f"PASS positives={len(values)} mutations={len(mutations)}")

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("paths",nargs="*",type=Path); p.add_argument("--selftest",type=Path)
    a=p.parse_args()
    try:
        if a.selftest: selftest(a.selftest)
        for path in a.paths: validate(load(path))
    except (OSError,json.JSONDecodeError,Refusal) as exc:
        print(f"FAIL {exc}",file=sys.stderr); return 2
    if a.paths: print(f"PASS validated={len(a.paths)}")
    return 0

if __name__=="__main__": raise SystemExit(main())
