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

QUEUE_PARENT_COMMIT = "00b9ae644352485e4779102b1c3c2d18f6a7155c"
QUEUE_PARENT_TREE = "4effe7ce338753ee61972890f676700ad33c3e04"
ACTIVE_ID = "LH-P7-01-FINAL-P6-LOCAL-READBACK"
TEMP_REF = "refs/remotes/origin/p7-root-d"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
SAFE_HOST_ENV = (
    "PATH",
    "HOME",
    "TMPDIR",
    "TMP",
    "TEMP",
    "LANG",
    "LC_ALL",
    "SYSTEMROOT",
    "COMSPEC",
    "PATHEXT",
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
        raise RunnerError(f"GIT_FAILED:{' '.join(args[:3])}:{result.returncode}")
    return result.stdout


def git_subject(cwd: pathlib.Path) -> dict[str, str]:
    commit = git_bytes(["rev-parse", "HEAD"], cwd).decode().strip()
    tree = git_bytes(["rev-parse", "HEAD^{tree}"], cwd).decode().strip()
    return {"repository": "ed3c/enterprise_agent_system", "commit": commit, "tree": tree}


def dirty_state(cwd: pathlib.Path) -> str:
    output = git_bytes(["status", "--porcelain", "--untracked-files=normal"], cwd)
    return "CLEAN" if not output else "DIRTY:" + digest_bytes(output)


def validate_runner_contract(contract: dict[str, Any]) -> None:
    if contract.get("schema_version") != "enterprise-agent-system/local-handoff-runner-contract/v1":
        raise RunnerError("RUNNER_CONTRACT_SCHEMA")
    subject = contract.get("queue_subject", {})
    if (subject.get("commit"), subject.get("tree")) != (QUEUE_PARENT_COMMIT, QUEUE_PARENT_TREE):
        raise RunnerError("QUEUE_PARENT_DRIFT")
    if subject.get("verification_run") != 32282597889 or subject.get("shadow_review") != 4975029921:
        raise RunnerError("QUEUE_PARENT_RECEIPT_DRIFT")
    if contract.get("active_item_id") != ACTIVE_ID:
        raise RunnerError("ACTIVE_ID_DRIFT")
    if contract.get("default_mode") != "plan":
        raise RunnerError("DEFAULT_MODE_NOT_PLAN")
    if contract.get("runner_execution") != "NOT_PERFORMED" or contract.get("queue_execution") != "NOT_PERFORMED":
        raise RunnerError("FALSE_EXECUTION_PROMOTION")
    if contract.get("execute_requires_external_runner_admission") is not True:
        raise RunnerError("RUNNER_ADMISSION_NOT_REQUIRED")


def assert_exact_parent_bytes(repo: pathlib.Path) -> None:
    expected_tree = git_bytes(["rev-parse", f"{QUEUE_PARENT_COMMIT}^{{tree}}"], repo).decode().strip()
    if expected_tree != QUEUE_PARENT_TREE:
        raise RunnerError("QUEUE_PARENT_TREE_MISMATCH")
    ancestor = run_process(["git", "merge-base", "--is-ancestor", QUEUE_PARENT_COMMIT, "HEAD"], cwd=repo)
    if ancestor.returncode != 0:
        raise RunnerError("RUNNER_NOT_TRUE_CHILD")
    unchanged = run_process(
        [
            "git",
            "diff",
            "--quiet",
            f"{QUEUE_PARENT_COMMIT}..HEAD",
            "--",
            "handoff/local-handoff-queue.json",
            "handoff/local-handoff-receipt.schema.json",
            "tests/verify_handoff.py",
        ],
        cwd=repo,
    )
    if unchanged.returncode != 0:
        raise RunnerError("CONSUMED_QUEUE_BYTES_MUTATED")


def assert_admitted_runner_subject(repo: pathlib.Path, commit: str, tree: str) -> None:
    if SHA40.fullmatch(commit) is None or SHA40.fullmatch(tree) is None:
        raise RunnerError("INVALID_ADMITTED_RUNNER_SUBJECT")
    observed = git_subject(repo)
    if (observed["commit"], observed["tree"]) != (commit, tree):
        raise RunnerError("RUNNER_SUBJECT_NOT_ADMITTED")


def active_item(queue: dict[str, Any]) -> dict[str, Any]:
    items = queue.get("items")
    if not isinstance(items, list):
        raise RunnerError("QUEUE_ITEMS")
    active = [item for item in items if isinstance(item, dict) and item.get("state") == "ACTIVE"]
    if len(active) != 1 or active[0].get("item_id") != queue.get("active_item_id") or active[0].get("item_id") != ACTIVE_ID:
        raise RunnerError("ACTIVE_CARDINALITY")
    return active[0]


def validate_relative(relative: str) -> pathlib.PurePath:
    path = pathlib.PurePath(relative)
    if path.is_absolute() or ".." in path.parts:
        raise RunnerError("PATH_ESCAPE")
    return path


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
    raw_root = environ.get(env_name)
    if not raw_root:
        raise RunnerError(f"MISSING_ENV:{env_name}")
    raw_path = pathlib.Path(raw_root).expanduser()
    if not raw_path.is_absolute():
        raise RunnerError(f"ENV_ROOT_NOT_ABSOLUTE:{env_name}")
    root = raw_path.resolve()
    rel = validate_relative(relative)
    target = (root / rel).resolve()
    if target != root and root not in target.parents:
        raise RunnerError("PATH_RESOLUTION_ESCAPE")
    if must_exist and not target.exists():
        raise RunnerError(f"PATH_MISSING:{env_name}")
    return target


def resolve_execution_roots(environ: Mapping[str, str], allowlist: set[str]) -> dict[str, pathlib.Path]:
    roots = {
        "EAS_CHECKOUT": resolve_env_path({"env": "EAS_CHECKOUT", "relative": "."}, environ, allowlist, must_exist=True),
        "EAS_WORKTREES": resolve_env_path({"env": "EAS_WORKTREES", "relative": "."}, environ, allowlist),
        "EAS_RECEIPT_DIR": resolve_env_path({"env": "EAS_RECEIPT_DIR", "relative": "."}, environ, allowlist),
    }
    names = list(roots)
    for index, left_name in enumerate(names):
        left = roots[left_name]
        for right_name in names[index + 1 :]:
            right = roots[right_name]
            if left == right or left in right.parents or right in left.parents:
                raise RunnerError(f"EXECUTION_ROOTS_OVERLAP:{left_name}:{right_name}")
    return roots


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


def public_command_record(spec: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "command_id": spec.get("command_id"),
        "cwd": spec.get("cwd"),
        "argv": spec.get("argv"),
        "timeout_seconds": spec.get("timeout_seconds"),
    }


def build_plan(queue: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    item = active_item(queue)
    return {
        "schema_version": "enterprise-agent-system/local-handoff-runner-plan/v1",
        "mode": "plan",
        "queue_parent": contract["queue_subject"],
        "queue_id": queue.get("queue_id"),
        "active_item_id": item.get("item_id"),
        "required_runtime_any_of": item.get("required_runtime_any_of"),
        "required_environment_names": required_env_names(item),
        "command_ids": [entry.get("command_id") for entry in item.get("commands", [])],
        "cleanup_ids": [entry.get("command_id") for entry in item.get("cleanup", [])],
        "receipt": item.get("required_receipt"),
        "execute_requires_external_runner_admission": True,
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
        failure = None if result.returncode == 0 else {
            "command_id": spec.get("command_id"),
            "kind": "NONZERO_EXIT",
            "exit_code": result.returncode,
        }
        return result.returncode, digest_bytes(result.stdout), digest_bytes(result.stderr), failure
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, bytes) else b""
        stderr = exc.stderr if isinstance(exc.stderr, bytes) else b""
        return 124, digest_bytes(stdout), digest_bytes(stderr), {
            "command_id": spec.get("command_id"),
            "kind": "TIMEOUT",
            "timeout_seconds": timeout,
        }
    except OSError as exc:
        return 126, digest_bytes(b""), digest_bytes(type(exc).__name__.encode()), {
            "command_id": spec.get("command_id"),
            "kind": "OS_ERROR",
            "error_type": type(exc).__name__,
        }


def temp_ref_present(checkout: pathlib.Path) -> bool:
    result = run_process(["git", "show-ref", "--verify", "--quiet", TEMP_REF], cwd=checkout)
    return result.returncode == 0


def residue_inventory(environ: Mapping[str, str], allowlist: set[str]) -> dict[str, Any]:
    checkout = resolve_env_path({"env": "EAS_CHECKOUT", "relative": "."}, environ, allowlist, must_exist=True)
    worktree = resolve_env_path({"env": "EAS_WORKTREES", "relative": "root-d-final"}, environ, allowlist)
    worktrees = git_bytes(["worktree", "list", "--porcelain"], checkout)
    listing = worktrees.decode("utf-8", errors="replace")
    registered = any(line == f"worktree {worktree}" for line in listing.splitlines())
    return {
        "root_d_worktree_exists": worktree.exists(),
        "root_d_worktree_registered": registered,
        "temporary_root_d_ref_present": temp_ref_present(checkout),
        "worktree_listing_digest": digest_bytes(worktrees),
        "checkout_dirty_state": dirty_state(checkout),
    }


def clean_residue(inventory: Mapping[str, Any], before_dirty: str) -> bool:
    return (
        inventory.get("root_d_worktree_exists") is False
        and inventory.get("root_d_worktree_registered") is False
        and inventory.get("temporary_root_d_ref_present") is False
        and inventory.get("checkout_dirty_state") == before_dirty
    )


def assert_clean_preflight_residue(inventory: Mapping[str, Any]) -> None:
    if inventory.get("root_d_worktree_exists") or inventory.get("root_d_worktree_registered") or inventory.get("temporary_root_d_ref_present"):
        raise RunnerError("PREEXISTING_RUNNER_RESIDUE_BLOCKED")


def validate_subject(value: Any, reason: str) -> None:
    if not isinstance(value, dict) or set(value) != {"repository", "commit", "tree"}:
        raise RunnerError(reason)
    if not isinstance(value.get("repository"), str) or not value["repository"]:
        raise RunnerError(reason)
    if SHA40.fullmatch(str(value.get("commit", ""))) is None or SHA40.fullmatch(str(value.get("tree", ""))) is None:
        raise RunnerError(reason)


def validate_receipt_against_schema(receipt: dict[str, Any], schema: dict[str, Any]) -> None:
    properties = schema.get("properties")
    required = schema.get("required")
    if not isinstance(properties, dict) or not isinstance(required, list):
        raise RunnerError("RECEIPT_SCHEMA_INVALID")
    if set(receipt) - set(properties):
        raise RunnerError("RECEIPT_ADDITIONAL_PROPERTIES")
    if any(field not in receipt for field in required):
        raise RunnerError("RECEIPT_REQUIRED_FIELDS")
    if receipt.get("schema_version") != "enterprise-agent-system/local-handoff-receipt/v2":
        raise RunnerError("RECEIPT_SCHEMA_VERSION")
    validate_subject(receipt.get("subject_before"), "RECEIPT_SUBJECT_BEFORE")
    validate_subject(receipt.get("subject_after"), "RECEIPT_SUBJECT_AFTER")
    if SHA40.fullmatch(str(receipt.get("observed_commit", ""))) is None or SHA40.fullmatch(str(receipt.get("observed_tree", ""))) is None:
        raise RunnerError("RECEIPT_OBSERVED_SUBJECT")
    commands = receipt.get("commands")
    codes = receipt.get("exit_codes")
    stdout = receipt.get("stdout_digests")
    stderr = receipt.get("stderr_digests")
    if not all(isinstance(value, list) for value in (commands, codes, stdout, stderr)):
        raise RunnerError("RECEIPT_COMMAND_ARRAYS")
    if not (len(commands) == len(codes) == len(stdout) == len(stderr)) or not commands:
        raise RunnerError("RECEIPT_COMMAND_CARDINALITY")
    if any(not isinstance(code, int) for code in codes):
        raise RunnerError("RECEIPT_EXIT_CODES")
    if any(SHA256.fullmatch(str(value)) is None for value in stdout + stderr):
        raise RunnerError("RECEIPT_DIGEST")
    if receipt.get("result") not in properties["result"].get("enum", []):
        raise RunnerError("RECEIPT_RESULT")
    if receipt.get("cleanup_result") not in properties["cleanup_result"].get("enum", []):
        raise RunnerError("RECEIPT_CLEANUP_RESULT")
    for field in ("effect_state", "readback_state", "compensation_state"):
        if field in receipt and receipt[field] not in properties[field].get("enum", []):
            raise RunnerError(f"RECEIPT_{field.upper()}")
    claims = receipt.get("claims_not_proven")
    if not isinstance(claims, list) or not claims or any(not isinstance(value, str) or not value for value in claims):
        raise RunnerError("RECEIPT_CLAIMS")
    if not isinstance(receipt.get("next_transition"), str) or not receipt["next_transition"]:
        raise RunnerError("RECEIPT_NEXT_TRANSITION")


def atomic_write_json(path: pathlib.Path, value: Mapping[str, Any]) -> None:
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
    queue: dict[str, Any],
    contract: dict[str, Any],
    schema: dict[str, Any],
    *,
    runtime_kind: str,
    admitted_runner_commit: str,
    admitted_runner_tree: str,
    environ: Mapping[str, str],
) -> tuple[dict[str, Any], pathlib.Path]:
    item = active_item(queue)
    allowed_runtime = item.get("required_runtime_any_of")
    if runtime_kind not in allowed_runtime or runtime_kind not in contract.get("allowed_runtime_kinds", []):
        raise RunnerError("RUNTIME_NOT_ADMITTED")
    assert_admitted_runner_subject(ROOT, admitted_runner_commit, admitted_runner_tree)

    allowlist = set(queue.get("environment_name_allowlist", []))
    required_names = required_env_names(item)
    for name in required_names:
        if name not in environ or not environ[name]:
            raise RunnerError(f"MISSING_ENV:{name}")

    roots = resolve_execution_roots(environ, allowlist)
    checkout = roots["EAS_CHECKOUT"]
    receipt_path = resolve_env_path(item["required_receipt"]["path"], environ, allowlist)
    if receipt_path == checkout or checkout in receipt_path.parents:
        raise RunnerError("RECEIPT_PATH_INSIDE_CHECKOUT")
    child_env = sanitized_child_env(environ, required_names)
    before_subject = git_subject(checkout)
    before_dirty = dirty_state(checkout)
    if before_dirty != "CLEAN":
        raise RunnerError("DIRTY_CHECKOUT_BLOCKED")
    before_inventory = residue_inventory(environ, allowlist)
    assert_clean_preflight_residue(before_inventory)

    started = now_iso()
    attempted: list[dict[str, Any]] = []
    exit_codes: list[int] = []
    stdout_digests: list[str] = []
    stderr_digests: list[str] = []
    failures: list[dict[str, Any]] = []
    cleanup_failures: list[dict[str, Any]] = []
    observed = before_subject.copy()
    result_state = "PASS"

    try:
        for spec in item.get("commands", []):
            attempted.append(public_command_record(spec))
            code, out_digest, err_digest, failure = command_result(
                spec,
                environ=environ,
                allowlist=allowlist,
                child_env=child_env,
            )
            exit_codes.append(code)
            stdout_digests.append(out_digest)
            stderr_digests.append(err_digest)
            if failure is not None:
                failures.append(failure)
                result_state = "FAIL"
                break
        worktree = resolve_env_path({"env": "EAS_WORKTREES", "relative": "root-d-final"}, environ, allowlist)
        if result_state == "PASS" and worktree.exists():
            observed = git_subject(worktree)
            root_subject = next(subject for subject in item["subjects"] if subject["subject_id"] == "ROOT-D")
            if (observed["commit"], observed["tree"]) != (root_subject["commit"], root_subject["tree"]):
                failures.append({"kind": "ROOT_D_OBSERVED_SUBJECT_MISMATCH"})
                result_state = "FAIL"
        elif result_state == "PASS":
            failures.append({"kind": "ROOT_D_WORKTREE_NOT_OBSERVED"})
            result_state = "FAIL"
    finally:
        for spec in item.get("cleanup", []):
            _code, _out_digest, _err_digest, failure = command_result(
                spec,
                environ=environ,
                allowlist=allowlist,
                child_env=child_env,
            )
            if failure is not None:
                cleanup_failures.append(failure)

    inventory = residue_inventory(environ, allowlist)
    cleanup_result = "PASS" if not cleanup_failures and clean_residue(inventory, before_dirty) else "FAIL"
    if cleanup_result != "PASS":
        result_state = "FAIL"
        failures.extend(cleanup_failures)
        if not clean_residue(inventory, before_dirty):
            failures.append({"kind": "RESIDUE_OR_DIRTY_STATE_MISMATCH"})

    after_subject = git_subject(checkout)
    after_dirty = dirty_state(checkout)
    next_transition = item["success_transition"] if result_state == "PASS" else item["failure_transition"]
    receipt = {
        "schema_version": "enterprise-agent-system/local-handoff-receipt/v2",
        "queue_id": queue["queue_id"],
        "item_id": item["item_id"],
        "started_at": started,
        "finished_at": now_iso(),
        "subject_before": before_subject,
        "subject_after": after_subject,
        "commands": attempted,
        "exit_codes": exit_codes,
        "stdout_digests": stdout_digests,
        "stderr_digests": stderr_digests,
        "observed_commit": observed["commit"],
        "observed_tree": observed["tree"],
        "evidence_lane": item["required_evidence_lane"],
        "result": result_state,
        "dirty_state_before": before_dirty,
        "dirty_state_after": after_dirty,
        "residue_inventory": inventory,
        "cleanup_result": cleanup_result,
        "failures": failures,
        "retries": [],
        "effect_state": "NOT_APPLICABLE",
        "readback_state": "MATCH" if result_state == "PASS" else "UNKNOWN",
        "compensation_state": "NOT_APPLICABLE",
        "claims_not_proven": item["claims_not_proven"],
        "next_transition": next_transition,
    }
    validate_receipt_against_schema(receipt, schema)
    atomic_write_json(receipt_path, receipt)
    return receipt, receipt_path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail-closed runner for the single ACTIVE Local Handoff item")
    parser.add_argument("--mode", choices=("plan", "execute"), default="plan")
    parser.add_argument("--runtime-kind", choices=("CODEX_CLI_LOCAL", "CLAUDE_CODE_LOCAL"))
    parser.add_argument("--admitted-runner-commit")
    parser.add_argument("--admitted-runner-tree")
    args = parser.parse_args(argv)

    contract = load_json(CONTRACT_PATH)
    queue = load_json(QUEUE_PATH)
    schema = load_json(SCHEMA_PATH)
    validate_runner_contract(contract)
    assert_exact_parent_bytes(ROOT)

    if args.mode == "plan":
        print(json.dumps(build_plan(queue, contract), indent=2, sort_keys=True))
        return 0
    if args.runtime_kind is None:
        raise RunnerError("EXECUTE_REQUIRES_RUNTIME_KIND")
    if args.admitted_runner_commit is None or args.admitted_runner_tree is None:
        raise RunnerError("EXECUTE_REQUIRES_ADMITTED_RUNNER_SUBJECT")
    receipt, _receipt_path = execute_active(
        queue,
        contract,
        schema,
        runtime_kind=args.runtime_kind,
        admitted_runner_commit=args.admitted_runner_commit,
        admitted_runner_tree=args.admitted_runner_tree,
        environ=os.environ,
    )
    print(
        json.dumps(
            {
                "item_id": receipt["item_id"],
                "result": receipt["result"],
                "cleanup_result": receipt["cleanup_result"],
                "next_transition": receipt["next_transition"],
            },
            sort_keys=True,
        )
    )
    return 0 if receipt["result"] == "PASS" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RunnerError as exc:
        print(f"BLOCKED:{exc}", file=sys.stderr)
        raise SystemExit(3)
