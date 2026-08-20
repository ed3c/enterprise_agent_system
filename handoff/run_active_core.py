#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "handoff/local-handoff-queue.json"
SCHEMA_PATH = ROOT / "handoff/local-handoff-receipt.schema.json"
QUEUE_VERIFY_PATH = ROOT / "tests/verify_handoff.py"
CONTRACT_PATH = ROOT / "handoff/local-handoff-runner-contract.json"

QUEUE_PARENT_COMMIT = "a6dbbc52fba70c9732a1bf664f52a072cd83d608"
QUEUE_PARENT_TREE = "7b54d0c56d088bf7edcf7b4c8984366a89ee9e36"
QUEUE_PARENT_VERIFY = 32286101504
QUEUE_PARENT_SHADOW = 4975366131
QUEUE_ID = "LH-EAS-INCEPTION-P7-V3-2026-08-20"
ACTIVE_ID = "LH-P7-01-ROOT-D-V2-LOCAL-READBACK"
ROOT_D_COMMIT = "68828ec8de5f3ad5aa133a5c772eefb80c775568"
ROOT_D_TREE = "bf338e0cd959a2b97adee79af7459222bd5211b9"
WORKTREE_RELATIVE = "root-d-v2"
TEMP_REF = "refs/remotes/origin/p7-root-d-v2"
SUPERSEDED_QUEUE_V2 = "00b9ae644352485e4779102b1c3c2d18f6a7155c"
SUPERSEDED_RUNNER_V2 = "521a8028ea66a137a7649a8292222ac408b87d25"

SHA40 = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
SAFE_HOST_ENV = (
    "PATH", "HOME", "TMPDIR", "TMP", "TEMP", "LANG", "LC_ALL",
    "SYSTEMROOT", "COMSPEC", "PATHEXT",
)


class RunnerError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RunnerError(f"NOT_OBJECT:{path.name}")
    return value


def run_process(
    argv: Sequence[str],
    *,
    cwd: pathlib.Path,
    env: Mapping[str, str] | None = None,
    timeout: int = 30,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        list(argv),
        cwd=str(cwd),
        env=dict(env) if env is not None else None,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def git_bytes(args: Sequence[str], cwd: pathlib.Path, timeout: int = 30) -> bytes:
    result = run_process(["git", *args], cwd=cwd, timeout=timeout)
    if result.returncode != 0:
        raise RunnerError(f"GIT_FAILED:{':'.join(args[:3])}:{result.returncode}")
    return result.stdout


def git_subject(cwd: pathlib.Path) -> dict[str, str]:
    commit = git_bytes(["rev-parse", "HEAD"], cwd).decode().strip()
    tree = git_bytes(["rev-parse", "HEAD^{tree}"], cwd).decode().strip()
    return {"repository": "ed3c/enterprise_agent_system", "commit": commit, "tree": tree}


def dirty_state(cwd: pathlib.Path) -> str:
    output = git_bytes(["status", "--porcelain", "--untracked-files=normal"], cwd)
    return "CLEAN" if not output else "DIRTY:" + digest_bytes(output)


def validate_runner_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != "enterprise-agent-system/local-handoff-runner-contract/v2":
        raise RunnerError("RUNNER_CONTRACT_SCHEMA")
    subject = contract.get("queue_subject")
    if not isinstance(subject, dict):
        raise RunnerError("QUEUE_SUBJECT_MISSING")
    if (subject.get("commit"), subject.get("tree")) != (QUEUE_PARENT_COMMIT, QUEUE_PARENT_TREE):
        raise RunnerError("QUEUE_PARENT_DRIFT")
    if subject.get("verification_run") != QUEUE_PARENT_VERIFY or subject.get("shadow_review") != QUEUE_PARENT_SHADOW:
        raise RunnerError("QUEUE_PARENT_RECEIPT_DRIFT")
    if contract.get("active_item_id") != ACTIVE_ID:
        raise RunnerError("ACTIVE_ID_DRIFT")
    if contract.get("default_mode") != "plan":
        raise RunnerError("DEFAULT_MODE_NOT_PLAN")
    if contract.get("runner_execution") != "NOT_PERFORMED" or contract.get("queue_execution") != "NOT_PERFORMED":
        raise RunnerError("FALSE_EXECUTION_PROMOTION")
    old = contract.get("superseded_authority")
    if not isinstance(old, list) or len(old) != 2:
        raise RunnerError("SUPERSEDED_DENOMINATOR")
    by_kind = {entry.get("kind"): entry for entry in old if isinstance(entry, dict)}
    if by_kind.get("queue", {}).get("commit") != SUPERSEDED_QUEUE_V2:
        raise RunnerError("OLD_QUEUE_V2_NOT_BOUND")
    if by_kind.get("runner", {}).get("commit") != SUPERSEDED_RUNNER_V2:
        raise RunnerError("OLD_RUNNER_V2_NOT_BOUND")
    if any(entry.get("authority") != "NONE" for entry in old):
        raise RunnerError("SUPERSEDED_AUTHORITY_PROMOTED")


def validate_queue(queue: Mapping[str, Any]) -> dict[str, Any]:
    if queue.get("schema_version") != "enterprise-agent-system/local-handoff-queue/v3":
        raise RunnerError("QUEUE_SCHEMA")
    if queue.get("queue_id") != QUEUE_ID or queue.get("queue_execution") != "NOT_PERFORMED":
        raise RunnerError("QUEUE_ID_OR_EXECUTION_DRIFT")
    if queue.get("active_item_id") != ACTIVE_ID:
        raise RunnerError("QUEUE_ACTIVE_DRIFT")
    items = queue.get("items")
    if not isinstance(items, list):
        raise RunnerError("QUEUE_ITEMS")
    active = [row for row in items if isinstance(row, dict) and row.get("state") == "ACTIVE"]
    if len(active) != 1 or active[0].get("item_id") != ACTIVE_ID:
        raise RunnerError("ACTIVE_CARDINALITY")
    item = active[0]
    if item.get("required_evidence_lane") != "LOCAL_DETERMINISTIC":
        raise RunnerError("ACTIVE_LANE_DRIFT")
    command_ids = [row.get("command_id") for row in item.get("commands", [])]
    if command_ids != [
        "FETCH_ROOT_D", "CREATE_ROOT_D_WORKTREE", "ASSERT_ROOT_D_SUBJECT",
        "REPLAY_GENERIC_X", "REPLAY_PROFILE_X", "REPLAY_PROFILE_X_MUTATIONS",
        "REPLAY_PROFILE_D", "REPLAY_PROFILE_D_MUTATIONS", "ASSERT_ROOT_D_PROJECTION",
    ]:
        raise RunnerError("ACTIVE_COMMAND_DENOMINATOR")
    cleanup_ids = [row.get("command_id") for row in item.get("cleanup", [])]
    if cleanup_ids != ["REMOVE_ROOT_D_WORKTREE", "PRUNE_WORKTREES", "DELETE_TEMP_ROOT_D_REF"]:
        raise RunnerError("CLEANUP_DENOMINATOR")
    subjects = {row.get("subject_id"): row for row in item.get("subjects", []) if isinstance(row, dict)}
    root_subject = subjects.get("ROOT-D", {})
    if (root_subject.get("commit"), root_subject.get("tree")) != (ROOT_D_COMMIT, ROOT_D_TREE):
        raise RunnerError("ROOT_D_SUBJECT_DRIFT")
    receipt = item.get("required_receipt", {})
    if receipt.get("path", {}).get("relative") != "LH-P7-01-ROOT-D-V2-LOCAL-READBACK.json":
        raise RunnerError("RECEIPT_ROUTE_DRIFT")
    return item


def assert_exact_parent_bytes(repo: pathlib.Path) -> None:
    parent_tree = git_bytes(["rev-parse", f"{QUEUE_PARENT_COMMIT}^{{tree}}"], repo).decode().strip()
    if parent_tree != QUEUE_PARENT_TREE:
        raise RunnerError("QUEUE_PARENT_TREE_MISMATCH")
    ancestor = run_process(["git", "merge-base", "--is-ancestor", QUEUE_PARENT_COMMIT, "HEAD"], cwd=repo)
    if ancestor.returncode != 0:
        raise RunnerError("RUNNER_NOT_TRUE_CHILD")
    unchanged = run_process(
        [
            "git", "diff", "--quiet", f"{QUEUE_PARENT_COMMIT}..HEAD", "--",
            "handoff/local-handoff-queue.json",
            "handoff/local-handoff-receipt.schema.json",
            "tests/verify_handoff.py",
        ],
        cwd=repo,
    )
    if unchanged.returncode != 0:
        raise RunnerError("CONSUMED_QUEUE_BYTES_MUTATED")


def active_item(queue: Mapping[str, Any]) -> dict[str, Any]:
    return validate_queue(queue)


def validate_relative(relative: str) -> pathlib.PurePath:
    path = pathlib.PurePath(relative)
    if path.is_absolute() or ".." in path.parts:
        raise RunnerError("PATH_ESCAPE")
    return path


def environment_root(name: str, environ: Mapping[str, str], *, must_exist: bool) -> pathlib.Path:
    raw = environ.get(name)
    if not raw:
        raise RunnerError(f"MISSING_ENV:{name}")
    raw_path = pathlib.Path(raw).expanduser()
    if not raw_path.is_absolute():
        raise RunnerError(f"ENV_ROOT_NOT_ABSOLUTE:{name}")
    root = raw_path.resolve()
    if must_exist and (not root.exists() or not root.is_dir()):
        raise RunnerError(f"ENV_ROOT_MISSING:{name}")
    return root


def assert_execution_roots(environ: Mapping[str, str]) -> dict[str, pathlib.Path]:
    roots = {
        "EAS_CHECKOUT": environment_root("EAS_CHECKOUT", environ, must_exist=True),
        "EAS_WORKTREES": environment_root("EAS_WORKTREES", environ, must_exist=True),
        "EAS_RECEIPT_DIR": environment_root("EAS_RECEIPT_DIR", environ, must_exist=True),
    }
    values = list(roots.items())
    for index, (name_a, path_a) in enumerate(values):
        for name_b, path_b in values[index + 1:]:
            if path_a == path_b or path_a in path_b.parents or path_b in path_a.parents:
                raise RunnerError(f"EXECUTION_ROOTS_OVERLAP:{name_a}:{name_b}")
    return roots


def resolve_env_path(
    spec: Mapping[str, Any],
    environ: Mapping[str, str],
    allowlist: set[str],
    *,
    must_exist: bool = False,
) -> pathlib.Path:
    env_name = spec.get("env")
    relative = spec.get("relative")
    if not isinstance(env_name, str) or env_name not in allowlist:
        raise RunnerError("ENV_NOT_ALLOWED")
    if not isinstance(relative, str):
        raise RunnerError("RELATIVE_PATH_REQUIRED")
    root = environment_root(env_name, environ, must_exist=False)
    target = (root / validate_relative(relative)).resolve()
    if target != root and root not in target.parents:
        raise RunnerError("PATH_RESOLUTION_ESCAPE")
    if must_exist and not target.exists():
        raise RunnerError(f"PATH_MISSING:{env_name}")
    return target


def render_arg(arg: Mapping[str, Any], environ: Mapping[str, str], allowlist: set[str]) -> str:
    if set(arg) == {"literal"}:
        value = arg.get("literal")
        if not isinstance(value, str) or "\x00" in value:
            raise RunnerError("INVALID_LITERAL_ARG")
        return value
    if set(arg) == {"env_path"} and isinstance(arg.get("env_path"), dict):
        return str(resolve_env_path(arg["env_path"], environ, allowlist))
    raise RunnerError("UNSUPPORTED_ARG_SHAPE")


def required_env_names(item: Mapping[str, Any]) -> list[str]:
    names: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if set(value) == {"env", "relative"} and isinstance(value.get("env"), str):
                names.add(value["env"])
            if isinstance(value.get("env_path"), dict) and isinstance(value["env_path"].get("env"), str):
                names.add(value["env_path"]["env"])
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(item.get("commands", []))
    walk(item.get("cleanup", []))
    walk(item.get("required_receipt", {}))
    return sorted(names)


def sanitized_child_env(environ: Mapping[str, str], required_names: Sequence[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in SAFE_HOST_ENV:
        value = environ.get(name)
        if value:
            result[name] = value
    for name in required_names:
        value = environ.get(name)
        if value:
            result[name] = value
    result["GIT_TERMINAL_PROMPT"] = "0"
    result["PYTHONUTF8"] = "1"
    return result


def public_command_record(spec: Mapping[str, Any], phase: str) -> dict[str, Any]:
    return {
        "phase": phase,
        "command_id": spec.get("command_id"),
        "cwd": spec.get("cwd"),
        "argv": spec.get("argv"),
        "timeout_seconds": spec.get("timeout_seconds"),
    }


def build_plan(queue: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, Any]:
    validate_runner_contract(contract)
    item = active_item(queue)
    return {
        "schema_version": "enterprise-agent-system/local-handoff-runner-plan/v2",
        "mode": "plan",
        "queue_parent": contract["queue_subject"],
        "queue_id": queue.get("queue_id"),
        "active_item_id": item.get("item_id"),
        "required_runtime_any_of": item.get("required_runtime_any_of"),
        "required_environment_names": required_env_names(item),
        "command_ids": [row.get("command_id") for row in item.get("commands", [])],
        "cleanup_ids": [row.get("command_id") for row in item.get("cleanup", [])],
        "receipt": item.get("required_receipt"),
        "execute_requires_external_runner_admission": True,
        "superseded_queue_v2_authority": "NONE",
        "superseded_runner_v2_authority": "NONE",
        "queue_execution": "NOT_PERFORMED",
    }


def command_result(
    spec: Mapping[str, Any],
    *,
    environ: Mapping[str, str],
    allowlist: set[str],
    child_env: Mapping[str, str],
) -> tuple[int, str, str, dict[str, Any] | None]:
    cwd_spec = spec.get("cwd")
    argv_spec = spec.get("argv")
    timeout = spec.get("timeout_seconds")
    if not isinstance(cwd_spec, dict) or not isinstance(argv_spec, list) or not isinstance(timeout, int):
        raise RunnerError("COMMAND_SPEC_INVALID")
    cwd = resolve_env_path(cwd_spec, environ, allowlist, must_exist=True)
    argv = [render_arg(arg, environ, allowlist) for arg in argv_spec]
    try:
        result = run_process(argv, cwd=cwd, env=child_env, timeout=timeout)
        failure = None
        if result.returncode != 0:
            failure = {"command_id": spec.get("command_id"), "kind": "NONZERO_EXIT", "exit_code": result.returncode}
        return result.returncode, digest_bytes(result.stdout), digest_bytes(result.stderr), failure
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, bytes) else b""
        stderr = exc.stderr if isinstance(exc.stderr, bytes) else b""
        return 124, digest_bytes(stdout), digest_bytes(stderr), {
            "command_id": spec.get("command_id"), "kind": "TIMEOUT", "timeout_seconds": timeout,
        }
    except OSError as exc:
        return 126, digest_bytes(b""), digest_bytes(type(exc).__name__.encode()), {
            "command_id": spec.get("command_id"), "kind": "OS_ERROR", "error_type": type(exc).__name__,
        }


def temp_ref_present(checkout: pathlib.Path) -> bool:
    result = run_process(["git", "show-ref", "--verify", "--quiet", TEMP_REF], cwd=checkout)
    return result.returncode == 0


def worktree_registered(checkout: pathlib.Path, target: pathlib.Path) -> bool:
    output = git_bytes(["worktree", "list", "--porcelain"], checkout).decode(errors="replace")
    target_resolved = target.resolve()
    for line in output.splitlines():
        if line.startswith("worktree "):
            candidate = pathlib.Path(line[len("worktree "):]).expanduser().resolve()
            if candidate == target_resolved:
                return True
    return False


def residue_inventory(environ: Mapping[str, str], allowlist: set[str]) -> dict[str, Any]:
    checkout = resolve_env_path({"env": "EAS_CHECKOUT", "relative": "."}, environ, allowlist, must_exist=True)
    worktree = resolve_env_path({"env": "EAS_WORKTREES", "relative": WORKTREE_RELATIVE}, environ, allowlist)
    listing = git_bytes(["worktree", "list", "--porcelain"], checkout)
    return {
        "root_d_worktree_exists": worktree.exists(),
        "root_d_worktree_registered": worktree_registered(checkout, worktree),
        "temporary_root_d_ref_present": temp_ref_present(checkout),
        "worktree_listing_digest": digest_bytes(listing),
        "checkout_dirty_state": dirty_state(checkout),
    }


def preflight_residue_clean(inventory: Mapping[str, Any]) -> bool:
    return (
        inventory.get("root_d_worktree_exists") is False
        and inventory.get("root_d_worktree_registered") is False
        and inventory.get("temporary_root_d_ref_present") is False
    )


def clean_residue(inventory: Mapping[str, Any], before_dirty: str) -> bool:
    return preflight_residue_clean(inventory) and inventory.get("checkout_dirty_state") == before_dirty


def assert_admitted_runner_subject(
    checkout: pathlib.Path,
    admitted_commit: str,
    admitted_tree: str,
) -> dict[str, str]:
    if admitted_commit in {SUPERSEDED_QUEUE_V2, SUPERSEDED_RUNNER_V2}:
        raise RunnerError("SUPERSEDED_RUNNER_AUTHORITY_NONE")
    if not SHA40.fullmatch(admitted_commit) or not SHA40.fullmatch(admitted_tree):
        raise RunnerError("ADMITTED_RUNNER_SUBJECT_FORMAT")
    observed = git_subject(checkout)
    if (observed["commit"], observed["tree"]) != (admitted_commit, admitted_tree):
        raise RunnerError("RUNNER_SUBJECT_NOT_ADMITTED")
    return observed


def validate_receipt(receipt: Mapping[str, Any], schema: Mapping[str, Any], item: Mapping[str, Any]) -> None:
    properties = schema.get("properties")
    required = schema.get("required")
    if not isinstance(properties, dict) or not isinstance(required, list):
        raise RunnerError("RECEIPT_SCHEMA_INVALID")
    if set(receipt) - set(properties):
        raise RunnerError("RECEIPT_UNKNOWN_FIELD")
    missing = [name for name in required if name not in receipt]
    if missing:
        raise RunnerError("RECEIPT_MISSING_FIELD:" + ",".join(missing))
    if receipt.get("schema_version") != "enterprise-agent-system/local-handoff-receipt/v2":
        raise RunnerError("RECEIPT_SCHEMA_VERSION")
    if receipt.get("queue_id") != QUEUE_ID or receipt.get("item_id") != ACTIVE_ID:
        raise RunnerError("RECEIPT_QUEUE_ITEM")
    if receipt.get("evidence_lane") != item.get("required_evidence_lane"):
        raise RunnerError("RECEIPT_EVIDENCE_LANE")
    if receipt.get("result") not in {"PASS", "FAIL", "BLOCKED", "NOT_EXERCISED", "UNKNOWN_EFFECT", "HUMAN_ADMIT_REQUIRED"}:
        raise RunnerError("RECEIPT_RESULT")
    if receipt.get("cleanup_result") not in {"PASS", "FAIL", "NOT_REQUIRED", "NOT_EXERCISED"}:
        raise RunnerError("RECEIPT_CLEANUP_RESULT")
    for subject_name in ("subject_before", "subject_after"):
        subject = receipt.get(subject_name)
        if not isinstance(subject, dict) or set(subject) != {"repository", "commit", "tree"}:
            raise RunnerError("RECEIPT_SUBJECT_SHAPE")
        if subject.get("repository") != "ed3c/enterprise_agent_system":
            raise RunnerError("RECEIPT_SUBJECT_REPOSITORY")
        if not SHA40.fullmatch(str(subject.get("commit", ""))) or not SHA40.fullmatch(str(subject.get("tree", ""))):
            raise RunnerError("RECEIPT_SUBJECT_SHA")
    if not SHA40.fullmatch(str(receipt.get("observed_commit", ""))) or not SHA40.fullmatch(str(receipt.get("observed_tree", ""))):
        raise RunnerError("RECEIPT_OBSERVED_SHA")
    commands = receipt.get("commands")
    exits = receipt.get("exit_codes")
    outs = receipt.get("stdout_digests")
    errs = receipt.get("stderr_digests")
    if not all(isinstance(value, list) for value in (commands, exits, outs, errs)):
        raise RunnerError("RECEIPT_COMMAND_ARRAYS")
    if not (len(commands) == len(exits) == len(outs) == len(errs)):
        raise RunnerError("RECEIPT_COMMAND_CARDINALITY")
    if not all(isinstance(code, int) for code in exits):
        raise RunnerError("RECEIPT_EXIT_CODE")
    if not all(isinstance(value, str) and DIGEST.fullmatch(value) for value in [*outs, *errs]):
        raise RunnerError("RECEIPT_DIGEST")
    if not isinstance(receipt.get("failures"), list) or not isinstance(receipt.get("retries"), list):
        raise RunnerError("RECEIPT_ATTEMPT_DENOMINATOR")
    if not isinstance(receipt.get("claims_not_proven"), list) or not receipt.get("claims_not_proven"):
        raise RunnerError("RECEIPT_CLAIMS")
    if receipt.get("result") == "PASS":
        if (receipt.get("observed_commit"), receipt.get("observed_tree")) != (ROOT_D_COMMIT, ROOT_D_TREE):
            raise RunnerError("PASS_WITHOUT_ROOT_D_OBSERVATION")
        if receipt.get("cleanup_result") != "PASS" or any(code != 0 for code in exits):
            raise RunnerError("PASS_WITH_FAILURE_OR_DIRTY_CLEANUP")
        if receipt.get("subject_before") != receipt.get("subject_after"):
            raise RunnerError("PASS_RUNNER_SUBJECT_DRIFT")


def atomic_write_json(path: pathlib.Path, value: Mapping[str, Any]) -> None:
    if path.exists():
        raise RunnerError("RECEIPT_ALREADY_EXISTS_BLOCKED")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def execute_active(
    queue: Mapping[str, Any],
    contract: Mapping[str, Any],
    schema: Mapping[str, Any],
    *,
    runtime_kind: str,
    admitted_runner_commit: str,
    admitted_runner_tree: str,
    environ: Mapping[str, str],
) -> tuple[dict[str, Any], pathlib.Path]:
    validate_runner_contract(contract)
    item = active_item(queue)
    allowed_runtime = item.get("required_runtime_any_of")
    if not isinstance(allowed_runtime, list) or runtime_kind not in allowed_runtime or runtime_kind not in contract.get("allowed_runtime_kinds", []):
        raise RunnerError("RUNTIME_NOT_ADMITTED")

    roots = assert_execution_roots(environ)
    allowlist = set(queue.get("environment_name_allowlist", []))
    required_names = required_env_names(item)
    if set(required_names) != {"EAS_CHECKOUT", "EAS_WORKTREES", "EAS_RECEIPT_DIR"}:
        raise RunnerError("ACTIVE_ENV_DENOMINATOR_DRIFT")
    for name in required_names:
        if name not in environ or not environ[name]:
            raise RunnerError(f"MISSING_ENV:{name}")

    checkout = roots["EAS_CHECKOUT"]
    assert_exact_parent_bytes(checkout)
    before_subject = assert_admitted_runner_subject(checkout, admitted_runner_commit, admitted_runner_tree)
    before_dirty = dirty_state(checkout)
    if before_dirty != "CLEAN":
        raise RunnerError("DIRTY_CHECKOUT_BLOCKED")
    preflight = residue_inventory(environ, allowlist)
    if not preflight_residue_clean(preflight):
        raise RunnerError("PREEXISTING_RUNNER_RESIDUE_BLOCKED")

    receipt_path = resolve_env_path(item["required_receipt"]["path"], environ, allowlist)
    if receipt_path.exists():
        raise RunnerError("RECEIPT_ALREADY_EXISTS_BLOCKED")
    child_env = sanitized_child_env(environ, required_names)

    started = now_iso()
    records: list[dict[str, Any]] = []
    exit_codes: list[int] = []
    stdout_digests: list[str] = []
    stderr_digests: list[str] = []
    failures: list[dict[str, Any]] = []
    observed_root: dict[str, str] | None = None
    main_ok = True
    cleanup_ok = True

    try:
        for spec in item.get("commands", []):
            records.append(public_command_record(spec, "main"))
            code, out_digest, err_digest, failure = command_result(
                spec, environ=environ, allowlist=allowlist, child_env=child_env
            )
            exit_codes.append(code)
            stdout_digests.append(out_digest)
            stderr_digests.append(err_digest)
            if failure is not None:
                failures.append(failure)
                main_ok = False
                break

        worktree = resolve_env_path({"env": "EAS_WORKTREES", "relative": WORKTREE_RELATIVE}, environ, allowlist)
        if main_ok and worktree.exists():
            observed_root = git_subject(worktree)
            if (observed_root["commit"], observed_root["tree"]) != (ROOT_D_COMMIT, ROOT_D_TREE):
                failures.append({"kind": "ROOT_D_OBSERVED_SUBJECT_MISMATCH"})
                main_ok = False
        elif main_ok:
            failures.append({"kind": "ROOT_D_WORKTREE_MISSING_AFTER_COMMANDS"})
            main_ok = False
    finally:
        for spec in item.get("cleanup", []):
            records.append(public_command_record(spec, "cleanup"))
            code, out_digest, err_digest, failure = command_result(
                spec, environ=environ, allowlist=allowlist, child_env=child_env
            )
            exit_codes.append(code)
            stdout_digests.append(out_digest)
            stderr_digests.append(err_digest)
            if failure is not None:
                tagged = dict(failure)
                tagged["phase"] = "cleanup"
                failures.append(tagged)
                cleanup_ok = False

    final_inventory = residue_inventory(environ, allowlist)
    if not clean_residue(final_inventory, before_dirty):
        failures.append({"kind": "RESIDUE_OR_DIRTY_STATE_MISMATCH"})
        cleanup_ok = False
    after_subject = git_subject(checkout)
    if after_subject != before_subject:
        failures.append({"kind": "RUNNER_SUBJECT_DRIFT_DURING_EXECUTION"})
        main_ok = False

    result_state = "PASS" if main_ok and cleanup_ok else "FAIL"
    observed = observed_root if observed_root is not None else before_subject
    receipt: dict[str, Any] = {
        "schema_version": "enterprise-agent-system/local-handoff-receipt/v2",
        "queue_id": QUEUE_ID,
        "item_id": ACTIVE_ID,
        "started_at": started,
        "finished_at": now_iso(),
        "subject_before": before_subject,
        "subject_after": after_subject,
        "commands": records,
        "exit_codes": exit_codes,
        "stdout_digests": stdout_digests,
        "stderr_digests": stderr_digests,
        "observed_commit": observed["commit"],
        "observed_tree": observed["tree"],
        "evidence_lane": item.get("required_evidence_lane"),
        "result": result_state,
        "dirty_state_before": before_dirty,
        "dirty_state_after": final_inventory.get("checkout_dirty_state", "UNKNOWN"),
        "residue_inventory": final_inventory,
        "cleanup_result": "PASS" if cleanup_ok else "FAIL",
        "failures": failures,
        "retries": [],
        "claims_not_proven": list(item.get("claims_not_proven", [])) + [
            "This receipt cannot by itself advance the queue; canonical reducer readback is separate.",
            "This LOCAL_DETERMINISTIC item grants no provider/private/physical/effect/Human/merge/release/rollback credit."
        ],
        "next_transition": item.get("success_transition") if result_state == "PASS" else item.get("failure_transition"),
    }
    validate_receipt(receipt, schema, item)
    atomic_write_json(receipt_path, receipt)
    return receipt, receipt_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail-closed EAS queue-v3 Local Handoff runner")
    parser.add_argument("--mode", choices=["plan", "execute"], default="plan")
    parser.add_argument("--runtime-kind")
    parser.add_argument("--admitted-runner-commit")
    parser.add_argument("--admitted-runner-tree")
    args = parser.parse_args(argv)

    queue = load_json(QUEUE_PATH)
    contract = load_json(CONTRACT_PATH)
    schema = load_json(SCHEMA_PATH)
    validate_runner_contract(contract)
    validate_queue(queue)

    if args.mode == "plan":
        if (ROOT / ".git").exists():
            assert_exact_parent_bytes(ROOT)
        print(json.dumps(build_plan(queue, contract), indent=2, sort_keys=True))
        return 0

    if not args.runtime_kind:
        raise RunnerError("EXECUTE_REQUIRES_RUNTIME_KIND")
    if not args.admitted_runner_commit or not args.admitted_runner_tree:
        raise RunnerError("EXECUTE_REQUIRES_ADMITTED_RUNNER_SUBJECT")
    receipt, path = execute_active(
        queue,
        contract,
        schema,
        runtime_kind=args.runtime_kind,
        admitted_runner_commit=args.admitted_runner_commit,
        admitted_runner_tree=args.admitted_runner_tree,
        environ=os.environ,
    )
    print(json.dumps({
        "result": receipt["result"],
        "cleanup_result": receipt["cleanup_result"],
        "next_transition": receipt["next_transition"],
        "receipt_environment_name": "EAS_RECEIPT_DIR",
        "receipt_filename": path.name,
    }, indent=2, sort_keys=True))
    return 0 if receipt["result"] == "PASS" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RunnerError as exc:
        print(f"BLOCKED:{exc}", file=sys.stderr)
        raise SystemExit(3)
