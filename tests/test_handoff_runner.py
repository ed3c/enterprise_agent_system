#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "handoff/run_active.py"
SPEC = importlib.util.spec_from_file_location("eas_h3r_runner", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load H3R runner")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class H3RRunnerTests(unittest.TestCase):
    def queue(self):
        return runner.load_json(runner.QUEUE_PATH)

    def contract(self):
        return runner.load_json(runner.CONTRACT_PATH)

    def schema(self):
        return runner.load_json(runner.SCHEMA_PATH)

    def test_contract_and_plan_bind_queue_v3_without_execution(self):
        contract = self.contract()
        queue = self.queue()
        runner.validate_runner_contract(contract)
        plan = runner.build_plan(queue, contract)
        self.assertEqual(plan["mode"], "plan")
        self.assertEqual(plan["queue_parent"]["commit"], runner.QUEUE_PARENT_COMMIT)
        self.assertEqual(plan["queue_parent"]["tree"], runner.QUEUE_PARENT_TREE)
        self.assertEqual(plan["active_item_id"], runner.ACTIVE_ID)
        self.assertEqual(plan["queue_id"], runner.QUEUE_ID)
        self.assertEqual(plan["queue_execution"], "NOT_PERFORMED")
        self.assertEqual(plan["superseded_queue_v2_authority"], "NONE")
        self.assertEqual(plan["superseded_runner_v2_authority"], "NONE")
        self.assertTrue(plan["execute_requires_external_runner_admission"])
        self.assertEqual(len(plan["command_ids"]), 9)
        self.assertEqual(
            plan["cleanup_ids"],
            ["REMOVE_ROOT_D_WORKTREE", "PRUNE_WORKTREES", "DELETE_TEMP_ROOT_D_REF"],
        )
        self.assertEqual(plan["required_environment_names"], ["EAS_CHECKOUT", "EAS_RECEIPT_DIR", "EAS_WORKTREES"])

    def test_queue_v2_is_refused(self):
        queue = self.queue()
        queue["schema_version"] = "enterprise-agent-system/local-handoff-queue/v2"
        with self.assertRaisesRegex(runner.RunnerError, "QUEUE_SCHEMA"):
            runner.validate_queue(queue)

    def test_superseded_authority_promotion_is_refused(self):
        contract = self.contract()
        contract["superseded_authority"][1]["authority"] = "ACTIVE"
        with self.assertRaisesRegex(runner.RunnerError, "SUPERSEDED_AUTHORITY_PROMOTED"):
            runner.validate_runner_contract(contract)

    def test_old_runner_subject_is_never_admitted(self):
        with tempfile.TemporaryDirectory() as root_dir:
            with self.assertRaisesRegex(runner.RunnerError, "SUPERSEDED_RUNNER_AUTHORITY_NONE"):
                runner.assert_admitted_runner_subject(
                    pathlib.Path(root_dir),
                    runner.SUPERSEDED_RUNNER_V2,
                    "1" * 40,
                )

    def test_plan_contains_no_resolved_local_paths(self):
        encoded = json.dumps(runner.build_plan(self.queue(), self.contract()), sort_keys=True)
        self.assertNotIn("/Users/", encoded)
        self.assertNotIn("/home/", encoded)
        self.assertNotIn("/mnt/data/", encoded)
        self.assertIn('"EAS_RECEIPT_DIR"', encoded)

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
            checkout.mkdir()
            receipt = root / "receipt"
            receipt.mkdir()
            env = {
                "EAS_CHECKOUT": str(checkout),
                "EAS_WORKTREES": str(checkout / "worktrees"),
                "EAS_RECEIPT_DIR": str(receipt),
            }
            (checkout / "worktrees").mkdir()
            with self.assertRaisesRegex(runner.RunnerError, "EXECUTION_ROOTS_OVERLAP"):
                runner.assert_execution_roots(env)

    def test_sanitized_environment_drops_unrelated_secret_names(self):
        source = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": "/safe-home",
            "EAS_CHECKOUT": "/repo",
            "API_TOKEN": "must-not-survive",
            "PASSWORD": "must-not-survive",
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
                {"env_path": {"env": "EAS_WORKTREES", "relative": runner.WORKTREE_RELATIVE}},
                env,
                {"EAS_WORKTREES"},
            )
            self.assertEqual(pathlib.Path(rendered), pathlib.Path(root_dir) / runner.WORKTREE_RELATIVE)
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

    def test_clean_residue_requires_no_dir_registration_ref_and_same_dirty_state(self):
        clean = {
            "root_d_worktree_exists": False,
            "root_d_worktree_registered": False,
            "temporary_root_d_ref_present": False,
            "checkout_dirty_state": "CLEAN",
        }
        self.assertTrue(runner.clean_residue(clean, "CLEAN"))
        for key in ("root_d_worktree_exists", "root_d_worktree_registered", "temporary_root_d_ref_present"):
            mutated = dict(clean)
            mutated[key] = True
            self.assertFalse(runner.clean_residue(mutated, "CLEAN"))
        dirty = dict(clean)
        dirty["checkout_dirty_state"] = "DIRTY:x"
        self.assertFalse(runner.clean_residue(dirty, "CLEAN"))

    def synthetic_receipt(self):
        subject = {"repository": "ed3c/enterprise_agent_system", "commit": "1" * 40, "tree": "2" * 40}
        return {
            "schema_version": "enterprise-agent-system/local-handoff-receipt/v2",
            "queue_id": runner.QUEUE_ID,
            "item_id": runner.ACTIVE_ID,
            "started_at": "2026-08-20T00:00:00Z",
            "finished_at": "2026-08-20T00:00:01Z",
            "subject_before": subject,
            "subject_after": subject,
            "commands": [{"command_id": "fixture"}],
            "exit_codes": [0],
            "stdout_digests": [runner.digest_bytes(b"")],
            "stderr_digests": [runner.digest_bytes(b"")],
            "observed_commit": runner.ROOT_D_COMMIT,
            "observed_tree": runner.ROOT_D_TREE,
            "evidence_lane": "LOCAL_DETERMINISTIC",
            "result": "PASS",
            "dirty_state_before": "CLEAN",
            "dirty_state_after": "CLEAN",
            "residue_inventory": {},
            "cleanup_result": "PASS",
            "failures": [],
            "retries": [],
            "claims_not_proven": ["fixture only"],
            "next_transition": "CANDIDATE_RECEIPT_READY_FOR_CANONICAL_REDUCER",
        }

    def test_receipt_validation_accepts_declared_pass_shape(self):
        runner.validate_receipt(self.synthetic_receipt(), self.schema(), runner.active_item(self.queue()))

    def test_receipt_validation_refuses_unknown_field(self):
        receipt = self.synthetic_receipt()
        receipt["resolved_local_path"] = "/should/not/serialize"
        with self.assertRaisesRegex(runner.RunnerError, "RECEIPT_UNKNOWN_FIELD"):
            runner.validate_receipt(receipt, self.schema(), runner.active_item(self.queue()))

    def test_pass_receipt_requires_exact_root_d_observation(self):
        receipt = self.synthetic_receipt()
        receipt["observed_commit"] = "3" * 40
        with self.assertRaisesRegex(runner.RunnerError, "PASS_WITHOUT_ROOT_D_OBSERVATION"):
            runner.validate_receipt(receipt, self.schema(), runner.active_item(self.queue()))

    def test_atomic_write_refuses_receipt_overwrite(self):
        with tempfile.TemporaryDirectory() as root_dir:
            path = pathlib.Path(root_dir) / "receipt.json"
            runner.atomic_write_json(path, {"state": "first"})
            self.assertEqual(json.loads(path.read_text()), {"state": "first"})
            with self.assertRaisesRegex(runner.RunnerError, "RECEIPT_ALREADY_EXISTS_BLOCKED"):
                runner.atomic_write_json(path, {"state": "second"})

    def test_execute_requires_explicit_admitted_runtime(self):
        with self.assertRaisesRegex(runner.RunnerError, "RUNTIME_NOT_ADMITTED"):
            runner.execute_active(
                self.queue(), self.contract(), self.schema(),
                runtime_kind="UNADMITTED",
                admitted_runner_commit="3" * 40,
                admitted_runner_tree="4" * 40,
                environ={},
            )

    def test_execute_cli_requires_external_runner_subject_before_environment(self):
        with self.assertRaisesRegex(runner.RunnerError, "EXECUTE_REQUIRES_ADMITTED_RUNNER_SUBJECT"):
            runner.main(["--mode", "execute", "--runtime-kind", "CODEX_CLI_LOCAL"])

    def test_preexisting_residue_blocks_before_any_command(self):
        with tempfile.TemporaryDirectory() as root_dir:
            root = pathlib.Path(root_dir)
            checkout, worktrees, receipts = root / "checkout", root / "worktrees", root / "receipts"
            checkout.mkdir(); worktrees.mkdir(); receipts.mkdir()
            env = {"EAS_CHECKOUT": str(checkout), "EAS_WORKTREES": str(worktrees), "EAS_RECEIPT_DIR": str(receipts)}
            subject = {"repository": "ed3c/enterprise_agent_system", "commit": "3" * 40, "tree": "4" * 40}
            residue = {
                "root_d_worktree_exists": False,
                "root_d_worktree_registered": False,
                "temporary_root_d_ref_present": True,
                "worktree_listing_digest": runner.digest_bytes(b"fixture"),
                "checkout_dirty_state": "CLEAN",
            }
            with (
                mock.patch.object(runner, "assert_exact_parent_bytes"),
                mock.patch.object(runner, "assert_admitted_runner_subject", return_value=subject),
                mock.patch.object(runner, "dirty_state", return_value="CLEAN"),
                mock.patch.object(runner, "residue_inventory", return_value=residue),
                mock.patch.object(runner, "command_result") as command,
            ):
                with self.assertRaisesRegex(runner.RunnerError, "PREEXISTING_RUNNER_RESIDUE_BLOCKED"):
                    runner.execute_active(
                        self.queue(), self.contract(), self.schema(),
                        runtime_kind="CODEX_CLI_LOCAL",
                        admitted_runner_commit=subject["commit"],
                        admitted_runner_tree=subject["tree"],
                        environ=env,
                    )
            command.assert_not_called()

    def test_main_failure_still_attempts_all_cleanup_and_writes_fail_receipt(self):
        with tempfile.TemporaryDirectory() as root_dir:
            root = pathlib.Path(root_dir)
            checkout, worktrees, receipts = root / "checkout", root / "worktrees", root / "receipts"
            checkout.mkdir(); worktrees.mkdir(); receipts.mkdir()
            env = {"EAS_CHECKOUT": str(checkout), "EAS_WORKTREES": str(worktrees), "EAS_RECEIPT_DIR": str(receipts)}
            subject = {"repository": "ed3c/enterprise_agent_system", "commit": "3" * 40, "tree": "4" * 40}
            clean = {
                "root_d_worktree_exists": False,
                "root_d_worktree_registered": False,
                "temporary_root_d_ref_present": False,
                "worktree_listing_digest": runner.digest_bytes(b"fixture"),
                "checkout_dirty_state": "CLEAN",
            }
            digest = runner.digest_bytes(b"")
            main_failure = (7, digest, digest, {"command_id": "FETCH_ROOT_D", "kind": "NONZERO_EXIT", "exit_code": 7})
            cleanup_ok = (0, digest, digest, None)
            with (
                mock.patch.object(runner, "assert_exact_parent_bytes"),
                mock.patch.object(runner, "assert_admitted_runner_subject", return_value=subject),
                mock.patch.object(runner, "git_subject", return_value=subject),
                mock.patch.object(runner, "dirty_state", return_value="CLEAN"),
                mock.patch.object(runner, "residue_inventory", side_effect=[clean, clean]),
                mock.patch.object(runner, "command_result", side_effect=[main_failure, cleanup_ok, cleanup_ok, cleanup_ok]) as command,
                mock.patch.object(runner, "atomic_write_json") as write,
            ):
                receipt, _path = runner.execute_active(
                    self.queue(), self.contract(), self.schema(),
                    runtime_kind="CODEX_CLI_LOCAL",
                    admitted_runner_commit=subject["commit"],
                    admitted_runner_tree=subject["tree"],
                    environ=env,
                )
            self.assertEqual(receipt["result"], "FAIL")
            self.assertEqual(receipt["cleanup_result"], "PASS")
            self.assertEqual(receipt["next_transition"], "BLOCKED_WITH_EXACT_LOCAL_RECEIPT")
            self.assertEqual(
                [call.args[0]["command_id"] for call in command.call_args_list],
                ["FETCH_ROOT_D", "REMOVE_ROOT_D_WORKTREE", "PRUNE_WORKTREES", "DELETE_TEMP_ROOT_D_REF"],
            )
            write.assert_called_once()

    def test_public_command_record_never_resolves_local_paths(self):
        item = runner.active_item(self.queue())
        record = runner.public_command_record(item["commands"][1], "main")
        self.assertEqual(record["phase"], "main")
        self.assertEqual(record["argv"][4]["env_path"]["env"], "EAS_WORKTREES")
        self.assertNotIn("resolved_path", record)


if __name__ == "__main__":
    unittest.main()
