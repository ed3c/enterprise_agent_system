#!/usr/bin/env python3
"""Fail-closed verifier for INCEPTION-X v4 after admitted EAS-A."""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[2]
REQ = ROOT / "requirements"
CLOSURE = ROOT / "plans" / "closure-record.json"
CANARY = ROOT / "plans" / "vertical-canary.json"
RECEIPTS = ROOT / "evidence" / "convergence" / "receipt-index.json"
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
EXPECTED_BASE="3a20e442afc6c0fc6999c3e0faec997524d1559c"; EXPECTED_BASE_TREE="4f9c5605c00841321108587434df38d0857ebe75"
EXPECTED_GX={"repository":"ed3c/enterprise_agent_system","pull_request":31,"commit":"b295eabec7b4c9d4e1f65f7fb0238034f454ae7f","tree":"25bd4c7e934690b3ac15692ba04af4418a46b1f2","verification_run":32296886625,"shadow_review":4976304922,"verdict":"ADMIT_FOR_PROFILE_X_REBIND_AFTER_EAS_A"}
EXPECTED_PE={"repository":"ed3c/enterprise_agent_system","pull_request":32,"commit":"9f25b94ca891faf0d926b0fc22b67be88925aa81","tree":"1452d1b9931c70ef70ed3b7dec78cedc51d6db35","shadow_review":4973593318,"verdict":"ADMIT_FOR_PROFILE_CONVERGENCE"}
EXPECTED_EAS_A={"repository":"ed3c/enterprise_agent_system","pull_request":68,"commit":"250717db1cad584d50890c0d851153fa2cd755e8","tree":"fbf6a75b6e89e906f227110dc5a61e4355b8a891","verification_run":32295871632,"shadow_review":4976213414,"authority":"ADVISORY_ONLY","relationship":"PROCESS_DEPENDENCY_NOT_GIT_PARENT","evidence_ceiling":"ADAPTER_AND_ADVISORY_PROJECTION_SEMANTICS_ONLY","google_connectivity":"NOT_PERFORMED","google_write":"NOT_PERFORMED","source_correctness":"NOT_PROVEN"}
EXPECTED_OWNERS={
"A1":("ed3c/bettor-arena","21ac4fdcd6ce4c5acea920dc4e59a53d13ecd328","31ea6bec01899a4c9e4f994998ea6041116db49d",(32259216877,)),
"A2R":("ed3c/runtime-env","2ff4efe7bee3d12fb3063fed93631f8d323cd64a","273c6873e7075d90a7f11275c5d39e746dd075dc",(32249588945,32249588946)),
"A2":("ed3c/agent-shield-monorepo","8ec782b78ec9e13f78f2faf14e6ffa722c1b78f2","51adf9791485d597849c026a3828ded0088b3805",(32262032532,32262032583,32262032553)),
"A3":("ed3c/truth-verify-loop","5ea4dd42d2ee5bbd22537f5426cd276f10222980","fc6486b9ab6a48752e32a536a847c6e5635f8547",(32260293092,32260291970)),
"A4":("ed3c/enterprise_agent_system","bf976c7c33e315d1743733a79c15521e645ff6dc","c09bef2457ad507433f253c8a5fd211147fae247",(32261864341,)),
"A5":("ed3c/bettor-arena","81f02f4148273ffe5f5571c8605e1ee0afc59866","f9612314e47ced69796db00703dd5d34ab592e36",(32260835956,)),
"A6":("ed3c/bettor-arena","c2613432736c65756ed13d871feb2df486c69118","53680d47048f88b9402c6320355121b7ec2f7244",(32262080676,))}
EXPECTED_STRONGER={"PHYSICAL_POWER_LOSS_MULTI_HOST","NETWORK_GVISOR_ISOLATION","PROVIDER_CAPABILITY_ENROLLMENT","EXTERNAL_INDEPENDENT_SEMANTIC","PRIVATE_EVIDENCE","EXACT_EXTERNAL_MODEL_DATA_TRACE_TERMS","LIVE_TELEMETRY_EXPORT_STORE_DELETE","EXTERNAL_CANDIDATE_BENCHMARK","REAL_EXTERNAL_EFFECT_REMOTE_READBACK","COMPENSATION","BUSINESS_USER_OUTCOME","HUMAN_LEGAL_SECURITY_ADMISSION","MERGE_RELEASE_ROLLBACK"}
NO_CREDIT={"NOT_EXERCISED","NOT_PERFORMED","NOT_VERIFIED","UNBOUND","HUMAN_ADMIT_REQUIRED","BLOCKED"}
EXPECTED_STALE={(44,"a7a034ef1db778fcee586fff8d8ff7848bc9a1ab"),(57,"68828ec8de5f3ad5aa133a5c772eefb80c775568"),(59,"a6dbbc52fba70c9732a1bf664f52a072cd83d608"),(67,"f81c2ecabaaac44ff82832a482524124baec106a"),(71,"82366dabf871f466c0c1353ef49198f82de90c16")}
class ProfileConvergenceError(ValueError): pass
def require(ok,reason):
    if not ok: raise ProfileConvergenceError(reason)
def load(path):
    x=json.loads(path.read_text(encoding="utf-8")); require(isinstance(x,dict),f"NOT_OBJECT:{path}"); return x
def source_denominator():
    requirements={}
    for name in ("control-requirements.json","assurance-requirements.json","delivery-requirements.json"):
        shard=load(REQ/name)
        for item in shard.get("requirements",[]):
            rid=item.get("requirement_id"); require(isinstance(rid,str) and rid.startswith("REQ-PDF-INCEPTION-"),f"SOURCE_REQUIREMENT:{name}"); require(rid not in requirements,f"SOURCE_DUPLICATE:{rid}"); requirements[rid]=item
    ids={x["id"] for x in load(REQ/"contradictions.json").get("items",[])}
    require(len(requirements)==15,f"SOURCE_REQUIREMENTS:{len(requirements)}"); require(ids=={f"UNK-INCEPTION-{i:03d}" for i in range(1,15)},"SOURCE_CONTRADICTIONS"); return requirements,ids
def canary_digest(c): return "sha256:"+hashlib.sha256(json.dumps(c["contract"],sort_keys=True,separators=(",",":")).encode()).hexdigest()
def validate_eas_a(v): require(v==EXPECTED_EAS_A,"EAS_A_DRIFT")
def validate_canary(c):
    require(c.get("schema_version")=="enterprise-agent-system/inception-profile-vertical-canary/v2","CANARY_SCHEMA"); require(c.get("state")=="PLAN_ONLY" and c.get("execution_receipt") is None,"CANARY_FALSE_EXECUTION"); require(DIGEST.fullmatch(str(c.get("contract_digest",""))) is not None,"CANARY_DIGEST"); require(canary_digest(c)==c["contract_digest"],"CANARY_DIGEST_MISMATCH")
    x=c["contract"]; require(x["generic_x"]==EXPECTED_GX,"CANARY_GX"); require(x["profile_shadow"]==EXPECTED_PE,"CANARY_PE"); validate_eas_a(x["eas_a_projection"]); require(x["eas_a_projection"]["relationship"]=="PROCESS_DEPENDENCY_NOT_GIT_PARENT","EAS_A_FALSE_PARENT")
    constraints=x["constraints"]; require(constraints.get("public_only") is True and constraints.get("reversible") is True,"CANARY_PUBLIC_REVERSIBLE")
    for k in ("private_data","external_effects","human_operation","provider_enrollment","production_credentials"): require(constraints.get(k) is False,f"CANARY_AUTHORITY:{k}")
    steps=x["steps"]; require(len(steps)==7 and [i["atom"] for i in steps]==list(EXPECTED_OWNERS),"CANARY_STEPS"); seen=set()
    for n,i in enumerate(steps,1):
        require(i["order"]==n and i["mode"]=="CONSTITUENT_RECEIPT_ONLY",f"CANARY_ORDER:{n}"); exp=EXPECTED_OWNERS[i["atom"]]; require((i["repository"],i["commit"],i["tree"],tuple(i["hosted_runs"]))==exp,f"CANARY_SUBJECT:{i['atom']}"); ident=(i["repository"],i["commit"],i["tree"]); require(ident not in seen,f"CANARY_DUP:{i['atom']}"); seen.add(ident)
def validate_receipts(r,c):
    require(r.get("schema_version")=="enterprise-agent-system/inception-profile-convergence-receipts/v4","RECEIPT_SCHEMA"); m=r["multi_parent_input"]; require(m["commit"]==EXPECTED_BASE and m["tree"]==EXPECTED_BASE_TREE,"MULTI_PARENT_BASE"); require([x["atom"] for x in m["parents"]]==["EAS-X","INCEPTION-E"],"MULTI_PARENT_DENOMINATOR"); require({k:v for k,v in m["parents"][0].items() if k!="atom"}==EXPECTED_GX,"MULTI_PARENT_GX"); require({k:v for k,v in m["parents"][1].items() if k!="atom"}==EXPECTED_PE,"MULTI_PARENT_PE"); validate_eas_a(r["eas_a_projection"]); require(all(x.get("atom")!="EAS-A" for x in m["parents"]),"EAS_A_FALSE_PARENT")
    owners=r["owners"]; require(len(owners)==7 and [x["atom"] for x in owners]==list(EXPECTED_OWNERS),"OWNER_DENOMINATOR")
    for x in owners:
        exp=EXPECTED_OWNERS[x["atom"]]; require((x["repository"],x["commit"],x["tree"],tuple(x["hosted_runs"]))==exp,f"OWNER:{x['atom']}")
    h=r["local_handoff"]; require(h["pull_request"]==59 and h["state"]=="STALE_PENDING_EAS_A_REBIND" and h["authority"]=="NONE" and h["queue_execution"]=="NOT_PERFORMED","HANDOFF_STALE"); require(r["source"]["class"]=="SOURCE_PROPOSAL" and r["source"]["requirements"]==15 and r["source"]["contradictions"]==14,"SOURCE"); require(r["vertical_canary"]["digest"]==c["contract_digest"] and r["vertical_canary"]["state"]=="PLAN_ONLY" and r["vertical_canary"]["execution_receipt"] is None,"RECEIPT_CANARY"); require(r["closure"]["closure_credit"]==0 and r["closure"]["full_architecture"]=="BLOCKED_FOR_CLOSURE","RECEIPT_CLOSURE")
    residues=r["residue"]["superseded_branches"]; require({x["branch"] for x in residues}=={"agent/inception-x-profile-convergence","agent/inception-x-profile-convergence-v2","agent/inception-x-profile-convergence-v3"},"RESIDUES"); require(all(x["authority"]=="NONE" for x in residues),"RESIDUE_AUTHORITY"); require(r["residue"]["rejected_base_attempts"]==[{"commit":"7d8b4ab76647e9817df74148107de27e65b2fd88","reason":"PROFILE_SUBTREE_INCOMPLETE","authority":"NONE"}],"REJECTED_BASE"); stale=r["downstream_freshness"]; require({(x["pull_request"],x["commit"]) for x in stale}==EXPECTED_STALE and all(x["authority"]=="NONE" and x["state"]=="STALE_PENDING_EAS_A_REBIND" for x in stale),"DOWNSTREAM_STALE")
def validate_closure(cl,c):
    source,cids=source_denominator(); require(cl.get("schema_version")=="enterprise-agent-system/inception-profile-closure/v4","CLOSURE_SCHEMA"); require(cl.get("state")=="PROFILE_CLOSURE_CANDIDATE_BLOCKED_STRONGER_LANES","CLOSURE_STATE"); require(cl["source_subject"]["class"]=="SOURCE_PROPOSAL","SOURCE_PROMOTION"); require(cl["multi_parent_input"]["commit"]==EXPECTED_BASE and cl["multi_parent_input"]["tree"]==EXPECTED_BASE_TREE,"CLOSURE_BASE"); require(cl["multi_parent_input"]["parents"]==[EXPECTED_GX,EXPECTED_PE],"CLOSURE_PARENTS"); validate_eas_a(cl["eas_a_projection"])
    rows=cl["requirements"]; require(len(rows)==15,"REQUIREMENT_DENOMINATOR"); indexed={x["requirement_id"]:x for x in rows}; require(set(indexed)==set(source),"REQUIREMENT_IDS"); require(sum(1 for x in rows if x["required_lane_satisfied"])==1,"REQUIRED_LANE_COUNT")
    for rid,row in indexed.items():
        src=source[rid]; require(row["canonical_owner_repository"]==src["owner"]["repository"],f"OWNER_SUBSTITUTION:{rid}"); require(row["owner_issue"]==src["owner"]["issue"],f"OWNER_ISSUE:{rid}"); require(row["required_evidence_lane"]==src["required_evidence_lane"],f"REQUIRED_LANE:{rid}"); require(row["closure_credit"]==0,f"CLOSURE_CREDIT:{rid}"); require(row["blockers"] and row["next_transition"],f"ROUTE:{rid}")
    require(indexed["REQ-PDF-INCEPTION-DAG-001"]["required_lane_satisfied"] is True,"DAG_LANE"); require(all(not x["required_lane_satisfied"] for rid,x in indexed.items() if rid!="REQ-PDF-INCEPTION-DAG-001"),"FALSE_LANE")
    contradictions=cl["contradictions"]; require(len(contradictions)==14 and {x["id"] for x in contradictions}==cids,"CONTRADICTION_DENOMINATOR"); require(all(x["state"]=="PRESERVED_WITH_PARTIAL_CONTROL" and x["control_atom"] and x["remaining_blocker"] for x in contradictions),"CONTRADICTION_RESOLUTION"); stronger=cl["stronger_lanes"]; require(len(stronger)==13 and {x["lane"] for x in stronger}==EXPECTED_STRONGER,"STRONGER_DENOMINATOR"); require(all(x["state"] in NO_CREDIT for x in stronger),"STRONGER_PROMOTION")
    selected=cl["selected_vertical_canary"]; require(selected["contract_digest"]==c["contract_digest"] and selected["state"]=="PLAN_ONLY" and selected["execution_receipt"] is None,"SELECTED_CANARY"); stale=cl["downstream_freshness"]; require({(x["pull_request"],x["commit"]) for x in stale}==EXPECTED_STALE and all(x["authority"]=="NONE" for x in stale),"CLOSURE_DOWNSTREAM_STALE"); s=cl["closure_summary"]; require(s["requirements_total"]==15 and s["requirements_required_lane_satisfied"]==1 and s["requirements_closure_credit"]==0,"SUMMARY_REQUIREMENTS"); require(s["contradictions_total"]==14 and s["contradictions_preserved"]==14,"SUMMARY_CONTRADICTIONS"); require(s["generic_x"]=="ADMIT_FOR_PROFILE_X_REBIND_AFTER_EAS_A","SUMMARY_GX"); require(s["eas_a"]=="ADVISORY_PROJECTION_ADMITTED_NO_STRONGER_CREDIT","SUMMARY_EAS_A"); require(s["vertical_canary"]=="PLAN_ONLY" and s["highest_state"]=="DETERMINISTIC_EVIDENCE_VERIFIED","SUMMARY_CANARY"); require(s["full_architecture"]=="BLOCKED_FOR_CLOSURE" and s["profile_release_state"]=="NOT_ADMITTED","SUMMARY_CLOSURE"); require(cl["next_transition"]=="P6_PROFILE_DOCUMENTATION_REBIND_AFTER_EAS_A","NEXT")
def validate_all():
    c=load(CANARY); r=load(RECEIPTS); cl=load(CLOSURE); validate_canary(c); validate_receipts(r,c); validate_closure(cl,c); return {"owners":7,"requirements":15,"contradictions":14,"stronger_lanes":13,"required_lanes_satisfied":1,"closure_credit":0,"canary":"PLAN_ONLY","eas_a":"ADVISORY_ONLY","downstream_stale":5,"full_architecture":"BLOCKED_FOR_CLOSURE"}
if __name__=="__main__":
    try: print("PASS",json.dumps(validate_all(),sort_keys=True))
    except (ProfileConvergenceError,KeyError,TypeError,json.JSONDecodeError) as exc: print(f"FAIL {exc}",file=sys.stderr); raise SystemExit(1)
