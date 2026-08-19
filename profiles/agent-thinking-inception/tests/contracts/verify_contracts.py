#!/usr/bin/env python3
"""Deterministic semantic gate for Agent Thinking Inception detailed contracts."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pathlib
import re
import sys
from collections.abc import Callable
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "contracts" / "inception-contract-bundle.v1.schema.json"
EXAMPLE_PATH = ROOT / "examples" / "inception-contract-bundle.example.json"

PROFILE_ID = "PROFILE-AGENT-THINKING-INCEPTION-001"
SOURCE_ID = "SRC-PDF-INCEPTION-001"
SOURCE_DIGEST = "sha256:a6f1245ff865cae24838ed8ec4828330be684f3c03b29b9064ade8bfac94d8da"

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
REPOSITORY = re.compile(r"^[^/\s]+/[^/\s]+$")
ISSUE = re.compile(
    r"^https://github\.com/ed3c/enterprise_agent_system/issues/[1-9][0-9]*$"
)
DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SECRET_OR_PRIVATE = re.compile(
    r"(?i)(PRIVATE KEY|(?:password|secret|token|cookie|session)\s*[:=]\s*\S{6,}"
    r"|/Users/|/home/|/mnt/data/|gemini\.google\.com/app/)"
)

RECORD_FIELDS: dict[str, set[str]] = {
    "enterprise-agent-system/context-budget-policy/v1": {
        "schema_version", "policy_id", "provider_id", "model_id", "tokenizer_id",
        "advertised_context_tokens", "reserve_tokens", "soft_checkpoint_ratio",
        "hard_stop_ratio", "measured_tokens", "active_transaction_id", "state",
        "owner", "claims_not_proven",
    },
    "enterprise-agent-system/safe-tool-transaction/v1": {
        "schema_version", "transaction_id", "task_id", "assistant_message_id",
        "tool_calls", "tool_results", "safe_boundary", "state", "owner",
        "claims_not_proven",
    },
    "enterprise-agent-system/compaction-request/v1": {
        "schema_version", "request_id", "task_id", "policy_id",
        "expected_state_version", "trigger", "old_context_digest",
        "candidate_checkpoint_id", "requested_at", "state", "owner",
        "claims_not_proven",
    },
    "enterprise-agent-system/compaction-checkpoint-binding/v1": {
        "schema_version", "checkpoint_id", "request_id", "task_id", "attempt_id",
        "state_version_before", "state_version_after", "prior_context_digest",
        "new_context_digest", "artifact_manifest_digest", "unresolved_work_digest",
        "capability_leases_digest", "pending_effects_digest", "policy_epoch",
        "rollback", "activation_state", "recovery_probe", "owner",
        "claims_not_proven",
    },
    "enterprise-agent-system/steering-capability-requirement/v1": {
        "schema_version", "requirement_id", "provider_id", "model_id",
        "capabilities", "allowed_actions", "observation_receipt", "state",
        "owner", "claims_not_proven",
    },
    "enterprise-agent-system/code-evidence-requirement/v1": {
        "schema_version", "evidence_id", "claim_id", "repository", "commit", "tree",
        "normalized_path", "line_start", "line_end", "snippet_digest", "symbol",
        "parser", "source_readback_digest", "state", "owner",
        "claims_not_proven",
    },
    "enterprise-agent-system/citation-claim-requirement/v1": {
        "schema_version", "claim_id", "source_subject_id", "source_digest",
        "locator", "exact_quote_digest", "authority_class", "deterministic_gate",
        "semantic_review", "final_state", "owner", "claims_not_proven",
    },
    "enterprise-agent-system/four-tier-provenance-requirement/v1": {
        "schema_version", "provenance_id", "dimensions", "data_flow_digest",
        "review_expiry", "state", "owner", "claims_not_proven",
    },
    "enterprise-agent-system/ingress-writeback-requirement/v1": {
        "schema_version", "binding_id", "provider", "event_identity",
        "authenticity", "dedupe_key", "inbox", "task_admission", "write_intent",
        "effect_ledger", "remote_readback", "compensation", "final_state",
        "owner", "claims_not_proven",
    },
    "enterprise-agent-system/profile-owner-binding/v1": {
        "schema_version", "binding_id", "profile_id", "interfaces", "consumers",
        "state", "claims_not_proven",
    },
    "enterprise-agent-system/profile-closure-record/v1": {
        "schema_version", "closure_id", "profile_id", "source_digest",
        "requirements_total", "contradictions_total", "evidence", "blockers",
        "next_transition", "human_owned", "closure_state", "claims_not_proven",
    },
}

EXPECTED_OWNER_INTERFACES = {
    "inception/domain-state-compaction": "ed3c/bettor-arena",
    "inception/runtime-sandbox-steering": "ed3c/agent-shield-monorepo",
    "inception/code-source-citation-evidence": "ed3c/truth-verify-loop",
    "inception/four-tier-provenance": "ed3c/enterprise_agent_system",
    "inception/discovery-admission": "ed3c/bettor-arena",
    "inception/ingress-effect-writeback": "ed3c/bettor-arena",
}

NO_CREDIT_STATES = {
    "ABSENT", "NOT_IMPLEMENTED", "NOT_EXERCISED", "SKIPPED_BY_POLICY",
    "STALE", "BLOCKED", "CANDIDATE", "HUMAN_ADMIT_REQUIRED",
}


class Refusal(ValueError):
    pass


def req(condition: bool, reason: str) -> None:
    if not condition:
        raise Refusal(reason)


def load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    req(isinstance(value, dict), f"ROOT_NOT_OBJECT:{path}")
    return value


def strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from strings(item)


def strict(
    value: Any,
    required: set[str],
    name: str,
    optional: set[str] | None = None,
) -> dict[str, Any]:
    req(isinstance(value, dict), f"{name}_NOT_OBJECT")
    optional = optional or set()
    missing = required - set(value)
    unknown = set(value) - required - optional
    req(
        not missing and not unknown,
        f"{name}_FIELDS:missing={sorted(missing)}:unknown={sorted(unknown)}",
    )
    return value


def nonempty_strings(value: Any, name: str) -> list[str]:
    req(isinstance(value, list) and bool(value), f"{name}_EMPTY")
    req(
        all(isinstance(item, str) and bool(item.strip()) for item in value),
        f"{name}_ITEM",
    )
    req(len(value) == len(set(value)), f"{name}_DUPLICATE")
    return value


def digest(value: Any, name: str, *, nullable: bool = False) -> None:
    if value is None:
        req(nullable, f"{name}_ABSENT")
        return
    req(isinstance(value, str) and SHA256.fullmatch(value) is not None, name)


def owner(value: Any, name: str) -> None:
    item = strict(value, {"repository", "directory", "issue"}, name)
    req(REPOSITORY.fullmatch(str(item["repository"])) is not None, f"{name}_REPO")
    req(isinstance(item["directory"], str) and bool(item["directory"]), f"{name}_DIR")
    req(ISSUE.fullmatch(str(item["issue"])) is not None, f"{name}_ISSUE")


def validate_schema_document(schema: dict[str, Any]) -> None:
    req(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "SCHEMA_DRAFT")
    req(schema.get("additionalProperties") is False, "SCHEMA_TOP_NOT_STRICT")
    definitions = schema.get("$defs")
    req(isinstance(definitions, dict), "SCHEMA_DEFS")
    req(len(definitions) == len(RECORD_FIELDS), "SCHEMA_DEFINITION_COUNT")
    declared_versions: set[str] = set()
    for name, definition in definitions.items():
        req(definition.get("additionalProperties") is False, f"SCHEMA_NOT_STRICT:{name}")
        required = definition.get("required")
        req(isinstance(required, list), f"SCHEMA_REQUIRED:{name}")
        properties = definition.get("properties", {})
        version = properties.get("schema_version", {}).get("const")
        req(version in RECORD_FIELDS, f"SCHEMA_VERSION:{name}")
        req(set(required) == RECORD_FIELDS[version], f"SCHEMA_FIELDS:{name}")
        declared_versions.add(version)
    req(declared_versions == set(RECORD_FIELDS), "SCHEMA_VERSION_DENOMINATOR")


def validate_context_budget(record: dict[str, Any]) -> None:
    for key in ("policy_id", "provider_id", "model_id", "tokenizer_id"):
        req(isinstance(record[key], str) and bool(record[key]), f"CONTEXT_{key}")
    advertised = record["advertised_context_tokens"]
    reserve = record["reserve_tokens"]
    measured = record["measured_tokens"]
    req(isinstance(advertised, int) and advertised > 0, "CONTEXT_ADVERTISED")
    req(isinstance(reserve, int) and 0 <= reserve < advertised, "CONTEXT_RESERVE")
    req(isinstance(measured, int) and 0 <= measured <= advertised, "CONTEXT_MEASURED")
    soft = record["soft_checkpoint_ratio"]
    hard = record["hard_stop_ratio"]
    req(isinstance(soft, (int, float)) and isinstance(hard, (int, float)), "CONTEXT_RATIO_TYPE")
    req(0 < soft < hard <= 1, "CONTEXT_THRESHOLD_ORDER")
    req(record["active_transaction_id"] is None or isinstance(record["active_transaction_id"], str), "CONTEXT_TRANSACTION")
    req(record["state"] in {"DISCOVERED", "BOUND", "ACTIVE", "BLOCKED"}, "CONTEXT_STATE")


def validate_tool_transaction(record: dict[str, Any]) -> None:
    calls = record["tool_calls"]
    results = record["tool_results"]
    req(isinstance(calls, list) and bool(calls), "TOOL_CALLS_EMPTY")
    req(isinstance(results, list), "TOOL_RESULTS_NOT_ARRAY")
    call_ids: list[str] = []
    result_ids: list[str] = []
    for index, raw in enumerate(calls):
        call = strict(raw, {"call_id", "tool_name", "ordinal"}, f"TOOL_CALL_{index}")
        req(call["ordinal"] == index, f"TOOL_CALL_ORDINAL:{index}")
        req(isinstance(call["call_id"], str) and bool(call["call_id"]), f"TOOL_CALL_ID:{index}")
        req(isinstance(call["tool_name"], str) and bool(call["tool_name"]), f"TOOL_NAME:{index}")
        call_ids.append(call["call_id"])
    for index, raw in enumerate(results):
        result = strict(raw, {"call_id", "ordinal", "state"}, f"TOOL_RESULT_{index}")
        req(result["ordinal"] == index, f"TOOL_RESULT_ORDINAL:{index}")
        req(result["state"] in {"PASS", "FAIL", "CANCELLED"}, f"TOOL_RESULT_STATE:{index}")
        result_ids.append(result["call_id"])
    req(len(call_ids) == len(set(call_ids)), "TOOL_CALL_DUPLICATE")
    req(len(result_ids) == len(set(result_ids)), "TOOL_RESULT_DUPLICATE")
    req(record["state"] in {"OPEN", "COMPLETE", "FAILED", "CANCELLED"}, "TOOL_TRANSACTION_STATE")
    req(record["safe_boundary"] in {"BEFORE_TRANSACTION", "AFTER_ALL_RESULTS", "UNSAFE"}, "TOOL_BOUNDARY")
    if record["state"] == "COMPLETE":
        req(call_ids == result_ids, "TOOL_TRANSACTION_INCOMPLETE")
        req(record["safe_boundary"] == "AFTER_ALL_RESULTS", "TOOL_COMPLETE_UNSAFE_BOUNDARY")


def validate_compaction_request(record: dict[str, Any]) -> None:
    trigger = strict(
        record["trigger"],
        {
            "measured_tokens", "advertised_context_tokens", "usage_ratio",
            "active_transaction_state",
        },
        "COMPACTION_TRIGGER",
    )
    measured = trigger["measured_tokens"]
    advertised = trigger["advertised_context_tokens"]
    ratio = trigger["usage_ratio"]
    req(isinstance(measured, int) and measured >= 0, "COMPACTION_MEASURED")
    req(isinstance(advertised, int) and advertised > 0, "COMPACTION_ADVERTISED")
    req(isinstance(ratio, (int, float)), "COMPACTION_RATIO_TYPE")
    req(abs(ratio - measured / advertised) < 1e-9, "COMPACTION_RATIO_MISMATCH")
    req(trigger["active_transaction_state"] in {"SAFE", "ACTIVE", "UNKNOWN"}, "COMPACTION_TRANSACTION_STATE")
    req(record["state"] in {"REQUESTED", "BLOCKED", "ADMITTED"}, "COMPACTION_REQUEST_STATE")
    if record["state"] == "ADMITTED":
        req(trigger["active_transaction_state"] == "SAFE", "COMPACTION_ACTIVE_TRANSACTION")
    req(isinstance(record["expected_state_version"], int) and record["expected_state_version"] >= 0, "COMPACTION_STATE_VERSION")
    req(DATETIME.fullmatch(str(record["requested_at"])) is not None, "COMPACTION_REQUESTED_AT")
    digest(record["old_context_digest"], "COMPACTION_OLD_CONTEXT")


def validate_checkpoint(record: dict[str, Any]) -> None:
    before = record["state_version_before"]
    after = record["state_version_after"]
    req(isinstance(before, int) and isinstance(after, int), "CHECKPOINT_VERSION_TYPE")
    req(after == before + 1, "CHECKPOINT_VERSION_INCREMENT")
    for key in (
        "prior_context_digest", "new_context_digest", "artifact_manifest_digest",
        "unresolved_work_digest", "capability_leases_digest",
        "pending_effects_digest",
    ):
        digest(record[key], f"CHECKPOINT_{key}")
    rollback = strict(record["rollback"], {"checkpoint_id", "digest"}, "CHECKPOINT_ROLLBACK")
    req(isinstance(rollback["checkpoint_id"], str) and bool(rollback["checkpoint_id"]), "CHECKPOINT_ROLLBACK_ID")
    digest(rollback["digest"], "CHECKPOINT_ROLLBACK_DIGEST")
    probe = strict(record["recovery_probe"], {"state", "receipt_digest"}, "CHECKPOINT_RECOVERY")
    req(probe["state"] in {"PASS", "FAIL", "NOT_EXERCISED"}, "CHECKPOINT_RECOVERY_STATE")
    digest(probe["receipt_digest"], "CHECKPOINT_RECOVERY_RECEIPT", nullable=True)
    req(record["activation_state"] in {"PREPARED", "VALIDATED", "COMMITTED", "ACTIVATED", "ROLLED_BACK", "BLOCKED"}, "CHECKPOINT_ACTIVATION")
    if record["activation_state"] == "ACTIVATED":
        req(probe["state"] == "PASS" and probe["receipt_digest"] is not None, "CHECKPOINT_ACTIVATED_WITHOUT_RECOVERY")


def validate_steering(record: dict[str, Any]) -> None:
    capabilities = strict(
        record["capabilities"],
        {
            "streaming_visibility", "safe_sync_point", "cancellation", "resume",
            "assistant_prefill", "hidden_reasoning_access",
        },
        "STEERING_CAPABILITIES",
    )
    allowed_states = {"SUPPORTED", "UNSUPPORTED", "UNKNOWN"}
    req(all(value in allowed_states for value in capabilities.values()), "STEERING_CAPABILITY_STATE")
    actions = nonempty_strings(record["allowed_actions"], "STEERING_ACTIONS")
    req(set(actions) <= {"CHECKPOINT", "TOOL_REQUEST", "CANCEL", "NO_ACTION", "HUMAN_ESCALATE"}, "STEERING_ACTION")
    digest(record["observation_receipt"], "STEERING_OBSERVATION", nullable=True)
    req(record["state"] in {"CAPABILITY_UNBOUND", "CAPABILITY_BOUND", "BLOCKED"}, "STEERING_STATE")
    if record["state"] == "CAPABILITY_BOUND":
        req(record["observation_receipt"] is not None, "STEERING_BOUND_WITHOUT_RECEIPT")
    if capabilities["hidden_reasoning_access"] == "SUPPORTED":
        req(record["observation_receipt"] is not None, "STEERING_HIDDEN_REASONING_UNPROVEN")


def validate_code_evidence(record: dict[str, Any]) -> None:
    req(REPOSITORY.fullmatch(str(record["repository"])) is not None, "CODE_REPOSITORY")
    req(SHA40.fullmatch(str(record["commit"])) is not None, "CODE_COMMIT")
    req(SHA40.fullmatch(str(record["tree"])) is not None, "CODE_TREE")
    path = record["normalized_path"]
    req(isinstance(path, str) and bool(path), "CODE_PATH")
    req(not path.startswith("/") and ".." not in pathlib.PurePosixPath(path).parts, "CODE_PATH_ESCAPE")
    req(isinstance(record["line_start"], int) and isinstance(record["line_end"], int), "CODE_LINES_TYPE")
    req(1 <= record["line_start"] <= record["line_end"], "CODE_LINES")
    digest(record["snippet_digest"], "CODE_SNIPPET_DIGEST")
    digest(record["source_readback_digest"], "CODE_READBACK_DIGEST")
    symbol = strict(record["symbol"], {"name", "kind", "signature_digest"}, "CODE_SYMBOL")
    req(symbol["kind"] in {"FUNCTION", "CLASS", "METHOD", "VARIABLE", "MODULE"}, "CODE_SYMBOL_KIND")
    digest(symbol["signature_digest"], "CODE_SIGNATURE_DIGEST")
    parser = strict(record["parser"], {"name", "version", "grammar"}, "CODE_PARSER")
    req(all(isinstance(parser[key], str) and bool(parser[key]) for key in parser), "CODE_PARSER_VALUE")
    req(record["state"] in {"CANDIDATE", "VERIFIED", "STALE", "UNVERIFIABLE"}, "CODE_STATE")


def validate_citation(record: dict[str, Any]) -> None:
    req(record["source_subject_id"] == SOURCE_ID, "CITATION_SOURCE_ID")
    req(record["source_digest"] == SOURCE_DIGEST, "CITATION_SOURCE_DIGEST")
    locator = strict(record["locator"], {"kind", "start", "end"}, "CITATION_LOCATOR")
    req(locator["kind"] in {"PAGE_LINES", "LINES", "SPAN"}, "CITATION_LOCATOR_KIND")
    req(isinstance(locator["start"], int) and isinstance(locator["end"], int), "CITATION_LOCATOR_TYPE")
    req(1 <= locator["start"] <= locator["end"], "CITATION_LOCATOR_RANGE")
    digest(record["exact_quote_digest"], "CITATION_QUOTE_DIGEST")
    gate = strict(record["deterministic_gate"], {"state", "receipt_digest"}, "CITATION_GATE")
    req(gate["state"] in {"PASS", "FAIL"}, "CITATION_GATE_STATE")
    digest(gate["receipt_digest"], "CITATION_GATE_RECEIPT")
    review = strict(record["semantic_review"], {"state", "reviewer_type", "receipt_digest"}, "CITATION_REVIEW")
    req(review["state"] in {"SUPPORTED", "REFUTED", "CONFLICTED", "ABSTAIN"}, "CITATION_REVIEW_STATE")
    req(review["reviewer_type"] in {"MODEL_JUDGE", "HUMAN", "DETERMINISTIC"}, "CITATION_REVIEWER")
    digest(review["receipt_digest"], "CITATION_REVIEW_RECEIPT", nullable=True)
    req(record["final_state"] in {"SUPPORTED", "REFUTED", "CONFLICTED", "STALE", "UNVERIFIABLE"}, "CITATION_FINAL")
    if record["final_state"] == "SUPPORTED":
        req(gate["state"] == "PASS" and review["state"] == "SUPPORTED", "CITATION_FALSE_SUPPORT")
        req(review["receipt_digest"] is not None, "CITATION_SUPPORT_WITHOUT_RECEIPT")


def validate_provenance(record: dict[str, Any]) -> None:
    dimensions = record["dimensions"]
    req(isinstance(dimensions, dict) and set(dimensions) == {"CODE", "MODEL", "DATA", "TRACE"}, "PROVENANCE_DIMENSIONS")
    for name, raw in dimensions.items():
        item = strict(
            raw,
            {
                "subject_id", "version", "terms_digest", "policy_state",
                "obligations", "blockers", "human_review_required",
            },
            f"PROVENANCE_{name}",
        )
        req(isinstance(item["subject_id"], str) and bool(item["subject_id"]), f"PROVENANCE_SUBJECT:{name}")
        req(isinstance(item["version"], str) and bool(item["version"]), f"PROVENANCE_VERSION:{name}")
        digest(item["terms_digest"], f"PROVENANCE_TERMS:{name}", nullable=True)
        req(item["policy_state"] in {"UNKNOWN", "BLOCKED", "POLICY_CANDIDATE", "POLICY_ADMITTED"}, f"PROVENANCE_POLICY:{name}")
        nonempty_strings(item["obligations"], f"PROVENANCE_OBLIGATIONS:{name}")
        nonempty_strings(item["blockers"], f"PROVENANCE_BLOCKERS:{name}")
        req(isinstance(item["human_review_required"], bool), f"PROVENANCE_HUMAN:{name}")
    digest(record["data_flow_digest"], "PROVENANCE_DATA_FLOW")
    req(DATETIME.fullmatch(str(record["review_expiry"])) is not None, "PROVENANCE_EXPIRY")
    req(record["state"] in {"UNKNOWN", "BLOCKED", "POLICY_CANDIDATE", "HUMAN_REVIEW_REQUIRED", "POLICY_ADMITTED"}, "PROVENANCE_STATE")
    if record["state"] == "POLICY_ADMITTED":
        req(
            all(
                item["policy_state"] == "POLICY_ADMITTED"
                and item["human_review_required"] is False
                for item in dimensions.values()
            ),
            "PROVENANCE_FALSE_ADMISSION",
        )


def receipt_state(value: Any, name: str, allowed: set[str]) -> dict[str, Any]:
    item = strict(value, {"state", "receipt_digest"}, name)
    req(item["state"] in allowed, f"{name}_STATE")
    digest(item["receipt_digest"], f"{name}_RECEIPT", nullable=True)
    if item["state"] == "PASS":
        req(item["receipt_digest"] is not None, f"{name}_PASS_WITHOUT_RECEIPT")
    return item


def validate_ingress(record: dict[str, Any]) -> None:
    authenticity = receipt_state(record["authenticity"], "INGRESS_AUTH", {"PASS", "FAIL"})
    inbox = receipt_state(record["inbox"], "INGRESS_INBOX", {"PASS", "FAIL", "NOT_EXERCISED"})
    admission = receipt_state(record["task_admission"], "INGRESS_TASK", {"PASS", "FAIL", "NOT_EXERCISED"})
    intent = strict(
        record["write_intent"],
        {"effect_id", "capability_id", "expected_remote_version", "payload_digest"},
        "INGRESS_INTENT",
    )
    req(all(isinstance(intent[key], str) and bool(intent[key]) for key in ("effect_id", "capability_id", "expected_remote_version")), "INGRESS_INTENT_ID")
    digest(intent["payload_digest"], "INGRESS_PAYLOAD")
    ledger = receipt_state(record["effect_ledger"], "INGRESS_LEDGER", {"ABSENT", "RESERVED", "COMMITTED", "UNKNOWN_EFFECT", "COMPENSATION_REQUIRED"})
    readback = receipt_state(record["remote_readback"], "INGRESS_READBACK", {"PASS", "FAIL", "NOT_EXERCISED", "UNKNOWN_EFFECT"})
    compensation = receipt_state(record["compensation"], "INGRESS_COMPENSATION", {"NOT_REQUIRED", "PASS", "FAIL", "NOT_EXERCISED"})
    req(record["final_state"] in {"EVENT_RECEIVED", "TASK_ADMITTED", "WRITE_INTENT_PREPARED", "COMMITTED", "UNKNOWN_EFFECT", "COMPENSATION_REQUIRED", "HUMAN_ESCALATE"}, "INGRESS_FINAL")
    if record["final_state"] == "COMMITTED":
        req(
            authenticity["state"] == inbox["state"] == admission["state"] == "PASS",
            "INGRESS_COMMIT_PREREQUISITES",
        )
        req(ledger["state"] == "COMMITTED", "INGRESS_LEDGER_NOT_COMMITTED")
        req(readback["state"] == "PASS", "INGRESS_COMMIT_WITHOUT_READBACK")
    if ledger["state"] == "UNKNOWN_EFFECT":
        req(record["final_state"] in {"UNKNOWN_EFFECT", "HUMAN_ESCALATE"}, "INGRESS_UNKNOWN_EFFECT_RETRY")


def validate_owner_binding(record: dict[str, Any]) -> None:
    req(record["profile_id"] == PROFILE_ID, "OWNER_PROFILE")
    interfaces = record["interfaces"]
    req(isinstance(interfaces, list), "OWNER_INTERFACES_NOT_ARRAY")
    seen: set[str] = set()
    for index, raw in enumerate(interfaces):
        item = strict(
            raw,
            {
                "interface_id", "owner_repository", "owner_directory",
                "owner_issue", "next_issue", "implementation_state",
                "required_lane",
            },
            f"OWNER_INTERFACE_{index}",
        )
        interface_id = item["interface_id"]
        req(interface_id not in seen, f"OWNER_DUPLICATE_INTERFACE:{interface_id}")
        seen.add(interface_id)
        req(
            item["owner_repository"] == EXPECTED_OWNER_INTERFACES.get(interface_id),
            f"OWNER_SUBSTITUTION:{interface_id}",
        )
        req(isinstance(item["owner_directory"], str) and bool(item["owner_directory"]), f"OWNER_DIRECTORY:{interface_id}")
        req(ISSUE.fullmatch(str(item["owner_issue"])) is not None, f"OWNER_ISSUE:{interface_id}")
        req(ISSUE.fullmatch(str(item["next_issue"])) is not None, f"OWNER_NEXT_ISSUE:{interface_id}")
        req(item["implementation_state"] in {"ABSENT", "NOT_IMPLEMENTED", "CANDIDATE", "IMPLEMENTED", "PASS"}, f"OWNER_IMPLEMENTATION:{interface_id}")
        req(item["required_lane"] in {"CLOUD", "LOCAL", "INDEPENDENT", "HUMAN"}, f"OWNER_LANE:{interface_id}")
    req(seen == set(EXPECTED_OWNER_INTERFACES), "OWNER_INTERFACE_DENOMINATOR")
    consumers = nonempty_strings(record["consumers"], "OWNER_CONSUMERS")
    req(all(REPOSITORY.fullmatch(item) is not None for item in consumers), "OWNER_CONSUMER_REPO")
    req(record["state"] in {"OWNER_LANES_BOUND", "BLOCKED", "CONSUMER_READY"}, "OWNER_STATE")


def validate_closure(record: dict[str, Any]) -> None:
    req(record["profile_id"] == PROFILE_ID, "CLOSURE_PROFILE")
    req(record["source_digest"] == SOURCE_DIGEST, "CLOSURE_SOURCE_DIGEST")
    req(record["requirements_total"] == 15, "CLOSURE_REQUIREMENTS")
    req(record["contradictions_total"] == 14, "CLOSURE_CONTRADICTIONS")
    evidence = record["evidence"]
    req(isinstance(evidence, list) and bool(evidence), "CLOSURE_EVIDENCE_EMPTY")
    lanes: set[str] = set()
    for index, raw in enumerate(evidence):
        item = strict(raw, {"lane", "state", "closure_credit", "subject"}, f"CLOSURE_EVIDENCE_{index}")
        lane = item["lane"]
        req(isinstance(lane, str) and bool(lane) and lane not in lanes, f"CLOSURE_LANE:{lane}")
        lanes.add(lane)
        req(isinstance(item["closure_credit"], int) and item["closure_credit"] >= 0, f"CLOSURE_CREDIT:{lane}")
        if item["state"] in NO_CREDIT_STATES:
            req(item["closure_credit"] == 0, f"CLOSURE_FALSE_CREDIT:{lane}")
        if item["state"] in {"PASS", "RELEASED"}:
            req(isinstance(item["subject"], dict), f"CLOSURE_PASS_WITHOUT_SUBJECT:{lane}")
            digest(item["subject"].get("digest"), f"CLOSURE_SUBJECT:{lane}")
    req({"SOURCE", "CONTRACT", "RUNTIME", "USER_OUTCOME", "HUMAN_ADMIT", "RELEASE"} <= lanes, "CLOSURE_LANE_DENOMINATOR")
    blockers = record["blockers"]
    req(isinstance(blockers, list) and bool(blockers), "CLOSURE_BLOCKERS_EMPTY")
    for index, raw in enumerate(blockers):
        item = strict(raw, {"id", "owner_issue", "state"}, f"CLOSURE_BLOCKER_{index}")
        req(ISSUE.fullmatch(str(item["owner_issue"])) is not None, f"CLOSURE_BLOCKER_OWNER:{index}")
        req(item["state"] in {"OPEN", "BLOCKED_BY_PREDECESSOR", "HUMAN_ADMIT_REQUIRED"}, f"CLOSURE_BLOCKER_STATE:{index}")
    nonempty_strings(record["human_owned"], "CLOSURE_HUMAN_OWNED")
    req(record["closure_state"] in {"CONTRACT_CANDIDATE", "BLOCKED", "HUMAN_ADMIT_REQUIRED", "RELEASED"}, "CLOSURE_STATE")
    by_lane = {item["lane"]: item for item in evidence}
    if record["closure_state"] == "RELEASED":
        req(by_lane["HUMAN_ADMIT"]["state"] == "PASS", "CLOSURE_RELEASE_WITHOUT_HUMAN")
        req(by_lane["RELEASE"]["state"] == "RELEASED", "CLOSURE_RELEASE_LANE")
    req(isinstance(record["next_transition"], str) and bool(record["next_transition"]), "CLOSURE_NEXT")


VALIDATORS: dict[str, Callable[[dict[str, Any]], None]] = {
    "enterprise-agent-system/context-budget-policy/v1": validate_context_budget,
    "enterprise-agent-system/safe-tool-transaction/v1": validate_tool_transaction,
    "enterprise-agent-system/compaction-request/v1": validate_compaction_request,
    "enterprise-agent-system/compaction-checkpoint-binding/v1": validate_checkpoint,
    "enterprise-agent-system/steering-capability-requirement/v1": validate_steering,
    "enterprise-agent-system/code-evidence-requirement/v1": validate_code_evidence,
    "enterprise-agent-system/citation-claim-requirement/v1": validate_citation,
    "enterprise-agent-system/four-tier-provenance-requirement/v1": validate_provenance,
    "enterprise-agent-system/ingress-writeback-requirement/v1": validate_ingress,
    "enterprise-agent-system/profile-owner-binding/v1": validate_owner_binding,
    "enterprise-agent-system/profile-closure-record/v1": validate_closure,
}


def sign(bundle: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(bundle)
    value.pop("bundle_digest", None)
    raw = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    value["bundle_digest"] = "sha256:" + hashlib.sha256(raw).hexdigest()
    return value


def record(bundle: dict[str, Any], version: str) -> dict[str, Any]:
    return next(item for item in bundle["records"] if item["schema_version"] == version)


def validate_bundle(bundle: dict[str, Any], schema: dict[str, Any]) -> None:
    req(
        not any(SECRET_OR_PRIVATE.search(item) for item in strings(bundle)),
        "SECRET_SESSION_OR_LOCAL_PATH",
    )
    strict(
        bundle,
        {
            "schema_version", "bundle_id", "profile_id", "source_subject_id",
            "source_digest", "records", "claims_not_proven", "bundle_digest",
        },
        "BUNDLE",
    )
    req(
        bundle["schema_version"]
        == "enterprise-agent-system/inception-contract-bundle/v1",
        "BUNDLE_VERSION",
    )
    req(bundle["profile_id"] == PROFILE_ID, "BUNDLE_PROFILE")
    req(bundle["source_subject_id"] == SOURCE_ID, "BUNDLE_SOURCE_ID")
    req(bundle["source_digest"] == SOURCE_DIGEST, "BUNDLE_SOURCE_DIGEST")
    nonempty_strings(bundle["claims_not_proven"], "BUNDLE_CLAIMS")
    digest(bundle["bundle_digest"], "BUNDLE_DIGEST")
    unsigned = copy.deepcopy(bundle)
    unsigned.pop("bundle_digest")
    expected = sign(unsigned)["bundle_digest"]
    req(bundle["bundle_digest"] == expected, "BUNDLE_DIGEST_MISMATCH")

    records = bundle["records"]
    req(isinstance(records, list), "RECORDS_NOT_ARRAY")
    versions = [item.get("schema_version") for item in records]
    req(len(versions) == len(set(versions)), "DUPLICATE_RECORD_VERSION")
    req(set(versions) == set(RECORD_FIELDS), "RECORD_VERSION_DENOMINATOR")

    validate_schema_document(schema)
    for item in records:
        version = item["schema_version"]
        strict(item, RECORD_FIELDS[version], f"RECORD:{version}")
        owner_value = item.get("owner")
        if owner_value is not None:
            owner(owner_value, f"OWNER:{version}")
        nonempty_strings(item["claims_not_proven"], f"CLAIMS:{version}")
        VALIDATORS[version](item)


def selftest(bundle: dict[str, Any], schema: dict[str, Any]) -> None:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("BUNDLE_DIGEST_MISMATCH", lambda value: value.update(bundle_id="BUNDLE-TAMPERED")),
        ("RECORD_VERSION_DENOMINATOR", lambda value: value["records"].pop()),
        ("FIELDS", lambda value: record(value, "enterprise-agent-system/context-budget-policy/v1").update(extra=True)),
        ("CONTEXT_THRESHOLD_ORDER", lambda value: record(value, "enterprise-agent-system/context-budget-policy/v1").update(soft_checkpoint_ratio=0.9)),
        ("TOOL_TRANSACTION_INCOMPLETE", lambda value: record(value, "enterprise-agent-system/safe-tool-transaction/v1")["tool_results"].pop()),
        ("TOOL_COMPLETE_UNSAFE_BOUNDARY", lambda value: record(value, "enterprise-agent-system/safe-tool-transaction/v1").update(safe_boundary="UNSAFE")),
        ("COMPACTION_RATIO_MISMATCH", lambda value: record(value, "enterprise-agent-system/compaction-request/v1")["trigger"].update(usage_ratio=0.5)),
        ("COMPACTION_ACTIVE_TRANSACTION", lambda value: record(value, "enterprise-agent-system/compaction-request/v1")["trigger"].update(active_transaction_state="ACTIVE")),
        ("CHECKPOINT_VERSION_INCREMENT", lambda value: record(value, "enterprise-agent-system/compaction-checkpoint-binding/v1").update(state_version_after=9)),
        ("CHECKPOINT_ACTIVATED_WITHOUT_RECOVERY", lambda value: record(value, "enterprise-agent-system/compaction-checkpoint-binding/v1")["recovery_probe"].update(state="NOT_EXERCISED", receipt_digest=None)),
        ("STEERING_BOUND_WITHOUT_RECEIPT", lambda value: record(value, "enterprise-agent-system/steering-capability-requirement/v1").update(state="CAPABILITY_BOUND")),
        ("CODE_PATH_ESCAPE", lambda value: record(value, "enterprise-agent-system/code-evidence-requirement/v1").update(normalized_path="../secret")),
        ("CITATION_FALSE_SUPPORT", lambda value: record(value, "enterprise-agent-system/citation-claim-requirement/v1").update(final_state="SUPPORTED")),
        ("PROVENANCE_FALSE_ADMISSION", lambda value: record(value, "enterprise-agent-system/four-tier-provenance-requirement/v1").update(state="POLICY_ADMITTED")),
        ("INGRESS_COMMIT_WITHOUT_READBACK", lambda value: (record(value, "enterprise-agent-system/ingress-writeback-requirement/v1").update(final_state="COMMITTED"), record(value, "enterprise-agent-system/ingress-writeback-requirement/v1")["effect_ledger"].update(state="COMMITTED"))),
        ("OWNER_DUPLICATE_INTERFACE", lambda value: record(value, "enterprise-agent-system/profile-owner-binding/v1")["interfaces"].append(copy.deepcopy(record(value, "enterprise-agent-system/profile-owner-binding/v1")["interfaces"][0]))),
        ("CLOSURE_FALSE_CREDIT", lambda value: record(value, "enterprise-agent-system/profile-closure-record/v1")["evidence"][2].update(closure_credit=1)),
        ("CLOSURE_RELEASE_WITHOUT_HUMAN", lambda value: record(value, "enterprise-agent-system/profile-closure-record/v1").update(closure_state="RELEASED")),
        ("SECRET_SESSION_OR_LOCAL_PATH", lambda value: value["claims_not_proven"].append("/mnt/data/private.pdf")),
        ("BUNDLE_SOURCE_DIGEST", lambda value: value.update(source_digest="sha256:" + "0" * 64)),
    ]
    for expected, mutate in mutations:
        candidate = copy.deepcopy(bundle)
        mutate(candidate)
        if expected != "BUNDLE_DIGEST_MISMATCH":
            candidate = sign(candidate)
        try:
            validate_bundle(candidate, schema)
        except Refusal as exc:
            req(expected in str(exc), f"WRONG_REFUSAL:{expected}:{exc}")
        else:
            raise Refusal(f"MUTATION_DID_NOT_FAIL:{expected}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    try:
        schema = load(SCHEMA_PATH)
        bundle = load(EXAMPLE_PATH)
        validate_bundle(bundle, schema)
        if args.selftest:
            selftest(bundle, schema)
    except (OSError, json.JSONDecodeError, Refusal, StopIteration) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(
        "PASS records=11 mutations="
        f"{20 if args.selftest else 0} "
        "evidence_ceiling=CONTRACT_CANDIDATE_ONLY"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
