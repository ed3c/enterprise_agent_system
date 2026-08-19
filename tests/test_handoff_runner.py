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

    def test_contract_and_plan_bind_exact_queue_without_execution(self):
        contract = self.contract()
        queue = self.queue()
        runner.validate_runner_contract(contract)
        plan = runner.build_plan(queue, contract)
        self.assertEqual(plan["mode"], "plan")
        self.assertEqual(plan["queue_parent"]["commit"], runner.QUEUE_PARENT_COMMIT)
        self.assertEqual(plan["queue_parent"]["tree"], runner.QUEUE_PARENT_TREE)
        self.assertEqual(plan["active_item_id"], runner.ACTIVE_ID)
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

    def test_clean_residue_requires_no_worktree_no_ref_and_same_dirty_state(self):
        before = "CLEAN"
        self.assertTrue(
            runner.clean_residue(
                {
                    "root_d_worktree_exists": False,
                    "temporary_root_d_ref_present": False,
                    "checkout_dirty_state": "CLEAN",
                },
                before,
            )
        )
        for mutation in (
            {"root_d_worktree_exists": True, "temporary_root_d_ref_present": False, "checkout_dirty_state": "CLEAN"},
            {"root_d_worktree_exists": False, "temporary_root_d_ref_present": True, "checkout_dirty_state": "CLEAN"},
            {"root_d_worktree_exists": False, "temporary_root_d_ref_present": False, "checkout_dirty_state": "DIRTY:x"},
        ):
            self.assertFalse(runner.clean_residue(mutation, before))

    def test_atomic_write_json_replaces_complete_document(self):
        with tempfile.TemporaryDirectory() as root_dir:
            path = pathlib.Path(root_dir) / "receipt.json"
            runner.atomic_write_json(path, {"a": 1, "state": "candidate"})
            first = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(first, {"a": 1, "state": "candidate"})
            runner.atomic_write_json(path, {"a": 2, "state": "replaced"})
            second = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(second, {"a": 2, "state": "replaced"})
            self.assertEqual(list(path.parent.glob("receipt.json.*.tmp")), [])

    def test_execute_requires_explicit_admitted_runtime(self):
        queue = self.queue()
        contract = self.contract()
        with self.assertRaisesRegex(runner.RunnerError, "RUNTIME_NOT_ADMITTED"):
            runner.execute_active(queue, contract, runtime_kind="UNADMITTED", environ={})

    def test_public_command_record_does_not_resolve_paths(self):
        item = runner.active_item(self.queue())
        record = runner.public_command_record(item["commands"][1])
        self.assertIsInstance(record["argv"][4]["env_path"], dict)
        self.assertEqual(record["argv"][4]["env_path"]["env"], "EAS_WORKTREES")
        self.assertNotIn("resolved_path", record)


if __name__ == "__main__":
    unittest.main()
