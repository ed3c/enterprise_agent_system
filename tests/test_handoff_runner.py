#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "handoff/run_active.py"
SPEC = importlib.util.spec_from_file_location("eas_handoff_runner", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load handoff runner")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class HandoffRunnerTests(unittest.TestCase):
    def queue(self):
        return runner.load_json(runner.QUEUE_PATH)

    def contract(self):
        return runner.load_json(runner.CONTRACT_PATH)

    def schema(self):
        return runner.load_json(runner.SCHEMA_PATH)

    def valid_receipt(self):
        digest = runner.digest_bytes(b"fixture")
        subject = {
            "repository": "ed3c/enterprise_agent_system",
            "commit": "1" * 40,
            "tree": "2" * 40,
        }
        return {
            "schema_version": "enterprise-agent-system/local-handoff-receipt/v2",
            "queue_id": "fixture-queue",
            "item_id": runner.ACTIVE_ID,
            "started_at": "2026-08-20T00:00:00Z",
            "finished_at": "2026-08-20T00:00:01Z",
            "subject_before": subject,
            "subject_after": subject.copy(),
            "commands": [{"command_id": "FIXTURE"}],
            "exit_codes": [0],
            "stdout_digests": [digest],
            "stderr_digests": [digest],
            "observed_commit": "1" * 40,
            "observed_tree": "2" * 40,
            "evidence_lane": "LOCAL_DETERMINISTIC",
            "result": "PASS",
            "dirty_state_before": "CLEAN",
            "dirty_state_after": "CLEAN",
            "residue_inventory": {},
            "cleanup_result": "PASS",
            "failures": [],
            "retries": [],
            "effect_state": "NOT_APPLICABLE",
            "readback_state": "MATCH",
            "compensation_state": "NOT_APPLICABLE",
            "claims_not_proven": ["fixture only"],
            "next_transition": "CANDIDATE_RECEIPT_READY_FOR_CANONICAL_REDUCER",
        }

    def test_contract_and_plan_bind_exact_queue_without_execution(self):
        contract = self.contract()
        queue = self.queue()
        runner.validate_runner_contract(contract)
        plan = runner.build_plan(queue, contract)
        self.assertEqual(plan["mode"], "plan")
        self.assertEqual(plan["queue_parent"]["commit"], runner.QUEUE_PARENT_COMMIT)
        self.assertEqual(plan["queue_parent"]["tree"], runner.QUEUE_PARENT_TREE)
        self.assertEqual(plan["active_item_id"], runner.ACTIVE_ID)
        self.assertTrue(plan["execute_requires_external_runner_admission"])
        self.assertEqual(plan["queue_execution"], "NOT_PERFORMED")
        self.assertEqual(
            plan["cleanup_ids"],
            ["REMOVE_ROOT_D_WORKTREE", "PRUNE_WORKTREES", "DELETE_TEMP_ROOT_D_REF"],
        )
        self.assertEqual(plan["required_environment_names"], ["EAS_CHECKOUT", "EAS_RECEIPT_DIR", "EAS_WORKTREES"])

    def test_plan_contains_no_resolved_local_paths(self):
        plan = runner.build_plan(self.queue(), self.contract())
        encoded = json.dumps(plan, sort_keys=True)
        self.assertNotIn("/Users/", encoded)
        self.assertNotIn("/home/", encoded)
        self.assertNotIn("/mnt/data/", encoded)
        self.assertIn('"env": "EAS_RECEIPT_DIR"', encoded)

    def test_path_escape_is_refused(self):
        with tempfile.TemporaryDirectory() as root_dir:
            env = {"EAS_WORKTREES": root_dir}
            with self.assertRaisesRegex(runner.RunnerError, "PATH_ESCAPE"):
                runner.resolve_env_path(
                    {"env": "EAS_WORKTREES", "relative": "../escape"},
                    env,
                    {"EAS_WORKTREES"},
                )

    def test_unknown_environment_is_refused(self):
        with tempfile.TemporaryDirectory() as root_dir:
            env = {"UNDECLARED": root_dir}
            with self.assertRaisesRegex(runner.RunnerError, "ENV_NOT_ALLOWED"):
                runner.resolve_env_path(
                    {"env": "UNDECLARED", "relative": "."},
                    env,
                    {"EAS_WORKTREES"},
                )

    def test_relative_environment_root_is_refused(self):
        with self.assertRaisesRegex(runner.RunnerError, "ENV_ROOT_NOT_ABSOLUTE"):
            runner.resolve_env_path(
                {"env": "EAS_WORKTREES", "relative": "."},
                {"EAS_WORKTREES": "relative-root"},
                {"EAS_WORKTREES"},
            )

    def test_execution_roots_must_be_pairwise_disjoint(self):
        with tempfile.TemporaryDirectory() as root_dir:
            root = pathlib.Path(root_dir)
            checkout = root / "checkout"
            worktrees = root / "worktrees"
            receipts = root / "receipts"
            checkout.mkdir()
            worktrees.mkdir()
            receipts.mkdir()
            env = {
                "EAS_CHECKOUT": str(checkout),
                "EAS_WORKTREES": str(worktrees),
                "EAS_RECEIPT_DIR": str(receipts),
            }
            resolved = runner.resolve_execution_roots(env, set(env))
            self.assertEqual(resolved["EAS_CHECKOUT"], checkout.resolve())
            nested = checkout / "worktrees"
            nested.mkdir()
            env["EAS_WORKTREES"] = str(nested)
            with self.assertRaisesRegex(runner.RunnerError, "EXECUTION_ROOTS_OVERLAP"):
                runner.resolve_execution_roots(env, set(env))

    def test_sanitized_environment_drops_unrelated_secret_names(self):
        source = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": "/safe-home",
            "EAS_CHECKOUT": "/repo",
            "API_TOKEN": "should-not-survive",
            "PASSWORD": "should-not-survive",
        }
        child = runner.sanitized_child_env(source, ["EAS_CHECKOUT"])
        self.assertEqual(child["EAS_CHECKOUT"], "/repo")
        self.assertEqual(child["GIT_TERMINAL_PROMPT"], "0")
        self.assertNotIn("API_TOKEN", child)
        self.assertNotIn("PASSWORD", child)

    def test_render_arg_accepts_declared_env_path_only(self):
        with tempfile.TemporaryDirectory() as root_dir:
            env = {"EAS_WORKTREES": root_dir}
            rendered = runner.render_arg(
                {"env_path": {"env": "EAS_WORKTREES", "relative": "root-d-final"}},
                env,
                {"EAS_WORKTREES"},
            )
            self.assertEqual(pathlib.Path(rendered), pathlib.Path(root_dir) / "root-d-final")
            with self.assertRaisesRegex(runner.RunnerError, "UNSUPPORTED_ARG_SHAPE"):
                runner.render_arg({"shell": "echo no"}, env, {"EAS_WORKTREES"})

    def test_command_result_uses_hermetic_subprocess_and_digest_only(self):
        with tempfile.TemporaryDirectory() as root_dir:
            env = {"FIXTURE_ROOT": root_dir}
            spec = {
                "command_id": "HERMETIC_OK",
                "cwd": {"env": "FIXTURE_ROOT", "relative": "."},
                "argv": [
                    {"literal": sys.executable},
                    {"literal": "-c"},
                    {"literal": "print('fixture-ok')"},
                ],
                "timeout_seconds": 30,
            }
            code, out_digest, err_digest, failure = runner.command_result(
                spec,
                environ=env,
                allowlist={"FIXTURE_ROOT"},
                child_env=runner.sanitized_child_env(env, ["FIXTURE_ROOT"]),
            )
            self.assertEqual(code, 0)
            self.assertRegex(out_digest, r"^sha256:[0-9a-f]{64}$")
            self.assertRegex(err_digest, r"^sha256:[0-9a-f]{64}$")
            self.assertIsNone(failure)
            self.assertNotIn("fixture-ok", out_digest)

    def test_command_failure_stays_failure_candidate(self):
        with tempfile.TemporaryDirectory() as root_dir:
            env = {"FIXTURE_ROOT": root_dir}
            spec = {
                "command_id": "HERMETIC_FAIL",
                "cwd": {"env": "FIXTURE_ROOT", "relative": "."},
                "argv": [
                    {"literal": sys.executable},
                    {"literal": "-c"},
                    {"literal": "raise SystemExit(7)"},
                ],
                "timeout_seconds": 30,
            }
            code, _out, _err, failure = runner.command_result(
                spec,
                environ=env,
                allowlist={"FIXTURE_ROOT"},
                child_env=runner.sanitized_child_env(env, ["FIXTURE_ROOT"]),
            )
            self.assertEqual(code, 7)
            self.assertEqual(failure["kind"], "NONZERO_EXIT")
            self.assertEqual(failure["exit_code"], 7)

    def test_clean_residue_requires_no_worktree_registration_ref_and_same_dirty_state(self):
        before = "CLEAN"
        clean = {
            "root_d_worktree_exists": False,
            "root_d_worktree_registered": False,
            "temporary_root_d_ref_present": False,
            "checkout_dirty_state": "CLEAN",
        }
        self.assertTrue(runner.clean_residue(clean, before))
        for field in ("root_d_worktree_exists", "root_d_worktree_registered", "temporary_root_d_ref_present"):
            mutation = dict(clean)
            mutation[field] = True
            self.assertFalse(runner.clean_residue(mutation, before))
        mutation = dict(clean)
        mutation["checkout_dirty_state"] = "DIRTY:x"
        self.assertFalse(runner.clean_residue(mutation, before))

    def test_preexisting_residue_is_refused_before_execution(self):
        for field in ("root_d_worktree_exists", "root_d_worktree_registered", "temporary_root_d_ref_present"):
            inventory = {
                "root_d_worktree_exists": False,
                "root_d_worktree_registered": False,
                "temporary_root_d_ref_present": False,
            }
            inventory[field] = True
            with self.assertRaisesRegex(runner.RunnerError, "PREEXISTING_RUNNER_RESIDUE_BLOCKED"):
                runner.assert_clean_preflight_residue(inventory)

    def test_atomic_write_json_replaces_complete_document(self):
        with tempfile.TemporaryDirectory() as root_dir:
            path = pathlib.Path(root_dir) / "receipt.json"
            runner.atomic_write_json(path, {"a": 1, "state": "candidate"})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"a": 1, "state": "candidate"})
            runner.atomic_write_json(path, {"a": 2, "state": "replaced"})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"a": 2, "state": "replaced"})
            self.assertEqual(list(path.parent.glob("receipt.json.*.tmp")), [])

    def test_receipt_validation_accepts_declared_shape_and_refuses_drift(self):
        schema = self.schema()
        receipt = self.valid_receipt()
        runner.validate_receipt_against_schema(receipt, schema)
        extra = dict(receipt)
        extra["local_path"] = "/private/path"
        with self.assertRaisesRegex(runner.RunnerError, "RECEIPT_ADDITIONAL_PROPERTIES"):
            runner.validate_receipt_against_schema(extra, schema)
        bad_digest = dict(receipt)
        bad_digest["stdout_digests"] = ["not-a-digest"]
        with self.assertRaisesRegex(runner.RunnerError, "RECEIPT_DIGEST"):
            runner.validate_receipt_against_schema(bad_digest, schema)

    def test_admitted_runner_subject_must_match_exact_head(self):
        observed = runner.git_subject(ROOT)
        runner.assert_admitted_runner_subject(ROOT, observed["commit"], observed["tree"])
        with self.assertRaisesRegex(runner.RunnerError, "RUNNER_SUBJECT_NOT_ADMITTED"):
            runner.assert_admitted_runner_subject(ROOT, "0" * 40, "1" * 40)

    def test_execute_requires_explicit_admitted_runtime(self):
        with self.assertRaisesRegex(runner.RunnerError, "RUNTIME_NOT_ADMITTED"):
            runner.execute_active(
                self.queue(),
                self.contract(),
                self.schema(),
                runtime_kind="UNADMITTED",
                admitted_runner_commit="0" * 40,
                admitted_runner_tree="1" * 40,
                environ={},
            )

    def test_execute_cli_requires_external_runner_subject_before_environment(self):
        with self.assertRaisesRegex(runner.RunnerError, "EXECUTE_REQUIRES_ADMITTED_RUNNER_SUBJECT"):
            runner.main(["--mode", "execute", "--runtime-kind", "CODEX_CLI_LOCAL"])

    def test_public_command_record_does_not_resolve_paths(self):
        item = runner.active_item(self.queue())
        record = runner.public_command_record(item["commands"][1])
        self.assertIsInstance(record["argv"][4]["env_path"], dict)
        self.assertEqual(record["argv"][4]["env_path"]["env"], "EAS_WORKTREES")
        self.assertNotIn("resolved_path", record)


if __name__ == "__main__":
    unittest.main()
