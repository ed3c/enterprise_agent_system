from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from enterprise_agent_system.orchestration import validate_prompt_packet  # noqa: E402

EAS_C_COMMIT = "ac0a7645392f689ae488328a53e7b6f3bb6ad02d"
EAS_C_TREE = "51c94cb43ed1e4a3a3ac05e42838532c3ec2e598"
PACKET = ROOT / "plans" / "examples" / "eas-k-prompt-packet.example.json"


class ParentBindingTests(unittest.TestCase):
    def test_persisted_packet_binds_admitted_eas_c_subject(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        self.assertEqual(
            packet["subject"],
            {
                "repository": "ed3c/enterprise_agent_system",
                "commit": EAS_C_COMMIT,
                "tree": EAS_C_TREE,
            },
        )
        validate_prompt_packet(packet)

    def test_packet_preserves_handoff_and_human_boundaries(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        self.assertEqual(
            packet["handoff"]["on_unavailable_capability"],
            "LOCAL_HANDOFF_REQUIRED",
        )
        self.assertEqual(
            packet["handoff"]["on_semantic_conflict"],
            "HUMAN_ADMIT_REQUIRED",
        )
        for operation in (
            "data_egress",
            "irreversible_effect",
            "merge",
            "permission_change",
            "promotion",
            "release",
            "rollback",
            "semantic_conflict_resolution",
            "visibility_change",
        ):
            self.assertIn(operation, packet["forbidden_actions"])


if __name__ == "__main__":
    unittest.main()
