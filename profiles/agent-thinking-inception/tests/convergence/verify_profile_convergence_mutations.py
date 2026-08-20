#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; sys.path.insert(0,str(HERE))
from verify_profile_convergence import ProfileConvergenceError,load,validate_canary,validate_receipts,validate_closure
CLOSURE=ROOT/"plans"/"closure-record.json"; CANARY=ROOT/"plans"/"vertical-canary.json"; RECEIPTS=ROOT/"evidence"/"convergence"/"receipt-index.json"
def rehash(c): c["contract_digest"]="sha256:"+hashlib.sha256(json.dumps(c["contract"],sort_keys=True,separators=(",",":")).encode()).hexdigest()
def refuse(label,fn,expected):
    try: fn()
    except ProfileConvergenceError as e:
        if expected not in str(e): raise AssertionError(f"{label}: wrong refusal {e}") from e
        return
    raise AssertionError(f"{label}: mutation accepted")
def main():
    bc=load(CLOSURE); bcan=load(CANARY); br=load(RECEIPTS); cases=[]
    def can(label,mut,exp,reh=False):
        v=copy.deepcopy(bcan); mut(v)
        if reh: rehash(v)
        refuse(label,lambda:validate_canary(v),exp); cases.append(label)
    can("false execution",lambda v:v.__setitem__("state","EXECUTED"),"CANARY_FALSE_EXECUTION")
    can("false receipt",lambda v:v.__setitem__("execution_receipt",{"x":1}),"CANARY_FALSE_EXECUTION")
    can("external effects",lambda v:v["contract"]["constraints"].__setitem__("external_effects",True),"CANARY_AUTHORITY:external_effects",True)
    can("human operation",lambda v:v["contract"]["constraints"].__setitem__("human_operation",True),"CANARY_AUTHORITY:human_operation",True)
    can("provider enrollment",lambda v:v["contract"]["constraints"].__setitem__("provider_enrollment",True),"CANARY_AUTHORITY:provider_enrollment",True)
    can("generic x drift",lambda v:v["contract"]["generic_x"].__setitem__("commit","0"*40),"CANARY_GX",True)
    can("profile e drift",lambda v:v["contract"]["profile_shadow"].__setitem__("shadow_review",1),"CANARY_PE",True)
    can("eas-a authority",lambda v:v["contract"]["eas_a_projection"].__setitem__("authority","CANONICAL"),"EAS_A_DRIFT",True)
    can("google connectivity",lambda v:v["contract"]["eas_a_projection"].__setitem__("google_connectivity","PASS"),"EAS_A_DRIFT",True)
    can("google write",lambda v:v["contract"]["eas_a_projection"].__setitem__("google_write","PASS"),"EAS_A_DRIFT",True)
    can("source correctness",lambda v:v["contract"]["eas_a_projection"].__setitem__("source_correctness","SUPPORTED"),"EAS_A_DRIFT",True)
    can("owner substitution",lambda v:v["contract"]["steps"][1].__setitem__("repository","ed3c/agent-shield-monorepo"),"CANARY_SUBJECT:A2R",True)
    can("step loss",lambda v:v["contract"]["steps"].pop(),"CANARY_STEPS",True)
    for label,mut,exp in [
      ("eas-a false parent",lambda v:v["multi_parent_input"]["parents"].append({"atom":"EAS-A",**v["eas_a_projection"]}),"MULTI_PARENT_DENOMINATOR"),
      ("receipt eas-a authority",lambda v:v["eas_a_projection"].__setitem__("authority","CANONICAL"),"EAS_A_DRIFT"),
      ("handoff current",lambda v:v["local_handoff"].update({"state":"CURRENT","authority":"CURRENT"}),"HANDOFF_STALE"),
      ("handoff executed",lambda v:v["local_handoff"].__setitem__("queue_execution","PASS"),"HANDOFF_STALE"),
      ("owner loss",lambda v:v["owners"].pop(),"OWNER_DENOMINATOR"),
      ("v3 authority",lambda v:next(x for x in v["residue"]["superseded_branches"] if x["branch"].endswith("-v3")).__setitem__("authority","CURRENT"),"RESIDUE_AUTHORITY"),
      ("downstream promotion",lambda v:v["downstream_freshness"][0].update({"state":"CURRENT","authority":"CURRENT"}),"DOWNSTREAM_STALE"),
      ("rejected base erased",lambda v:v["residue"].__setitem__("rejected_base_attempts",[]),"REJECTED_BASE")]:
        v=copy.deepcopy(br); mut(v); refuse(label,lambda v=v:validate_receipts(v,bcan),exp); cases.append(label)
    for label,mut,exp in [
      ("source promotion",lambda v:v["source_subject"].__setitem__("class","CURRENT_FACT"),"SOURCE_PROMOTION"),
      ("requirement loss",lambda v:v["requirements"].pop(),"REQUIREMENT_DENOMINATOR"),
      ("owner substitution",lambda v:v["requirements"][0].__setitem__("canonical_owner_repository","ed3c/runtime-env"),"OWNER_SUBSTITUTION"),
      ("required lane rewrite",lambda v:v["requirements"][0].__setitem__("required_evidence_lane","CLOUD_DETERMINISTIC"),"REQUIRED_LANE"),
      ("false lane satisfaction",lambda v:v["requirements"][0].__setitem__("required_lane_satisfied",True),"REQUIRED_LANE_COUNT"),
      ("closure credit",lambda v:v["requirements"][0].__setitem__("closure_credit",1),"CLOSURE_CREDIT"),
      ("contradiction loss",lambda v:v["contradictions"].pop(),"CONTRADICTION_DENOMINATOR"),
      ("contradiction resolved",lambda v:v["contradictions"][0].__setitem__("state","RESOLVED"),"CONTRADICTION_RESOLUTION"),
      ("stronger promoted",lambda v:v["stronger_lanes"][0].__setitem__("state","PASS"),"STRONGER_PROMOTION"),
      ("human laundering",lambda v:v["closure_summary"].__setitem__("highest_state","HUMAN_ADMITTED"),"SUMMARY_CANARY"),
      ("full closure",lambda v:v["closure_summary"].__setitem__("full_architecture","PASS"),"SUMMARY_CLOSURE"),
      ("closure eas-a authority",lambda v:v["eas_a_projection"].__setitem__("authority","CANONICAL"),"EAS_A_DRIFT"),
      ("closure downstream current",lambda v:v["downstream_freshness"][0].__setitem__("authority","CURRENT"),"CLOSURE_DOWNSTREAM_STALE")]:
        v=copy.deepcopy(bc); mut(v); refuse(label,lambda v=v:validate_closure(v,bcan),exp); cases.append(label)
    assert len(cases)==34,len(cases); print("PASS profile convergence v4 semantic mutations 34/34")
if __name__=="__main__": main()
