"""Executable regression tests for the OpenClaw packaging and state contract."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
RETRIEVE = ROOT / "scripts" / "retrieve_symbolic_patterns.py"
REGISTRY_RETRIEVE = ROOT / "scripts" / "retrieve_symbolic_patterns_registry.py"
EVOLVE = ROOT / "scripts" / "evolve_from_use.py"
PATTERN = (
    ROOT
    / "references"
    / "patterns"
    / "alchemical"
    / "alchemical_nigredo_putrefaction.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class OpenClawPortabilityTests(unittest.TestCase):
    def run_script(
        self, script: Path, *arguments: str, state: Path
    ) -> subprocess.CompletedProcess[str]:
        env = {**os.environ, "KUBRICK_STATE_DIR": str(state)}
        return subprocess.run(
            [sys.executable, str(script), *arguments],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_retrieval_logs_outside_skill(self) -> None:
        brief = {
            "dramatic_problem": "identity dissolution and breakdown",
            "genre": "drama",
            "format": "feature",
            "cultural_context": "contemporary",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            brief_path = root / "brief.json"
            brief_path.write_text(json.dumps(brief), encoding="utf-8")
            result = self.run_script(
                RETRIEVE,
                "--brief",
                str(brief_path),
                "--no-cache",
                state=root / "state",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = yaml.safe_load(result.stdout)["retrieval_receipt"]
            self.assertEqual(receipt["status"], "SELECTED")
            logged = Path(receipt["logged_to"])
            self.assertTrue(logged.is_file())
            self.assertTrue(logged.is_relative_to(root / "state"))
            self.assertNotIn(str(ROOT), str(logged))

    def test_registry_cache_and_receipt_stay_outside_skill(self) -> None:
        brief = {
            "dramatic_problem": "authority transfers through a threshold",
            "desired_state_change": "ownership visibly transfers",
            "format": "storyboard",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            brief_path = root / "brief.json"
            brief_path.write_text(json.dumps(brief), encoding="utf-8")
            result = self.run_script(
                REGISTRY_RETRIEVE,
                "--brief",
                str(brief_path),
                state=root / "state",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = yaml.safe_load(result.stdout)["retrieval_receipt"]
            self.assertTrue(Path(receipt["cached_to"]).is_relative_to(root / "state"))
            self.assertTrue(Path(receipt["logged_to"]).is_relative_to(root / "state"))
            self.assertFalse((ROOT / "references" / "usage" / "cache-registry").exists())

    def test_prohibited_pattern_is_recorded(self) -> None:
        brief = {
            "dramatic_problem": "identity breakdown",
            "genre": "drama",
            "format": "feature",
            "prohibited_patterns": ["nigredo"],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            brief_path = root / "brief.json"
            brief_path.write_text(json.dumps(brief), encoding="utf-8")
            result = self.run_script(
                RETRIEVE,
                "--brief",
                str(brief_path),
                "--no-log",
                state=root / "state",
            )
            self.assertIn(result.returncode, (0, 1), result.stderr)
            receipt = yaml.safe_load(result.stdout)["retrieval_receipt"]
            rejected = receipt.get("rejected_patterns", [])
            self.assertTrue(
                any(
                    item["pattern_id"] == "alchemical_nigredo_putrefaction"
                    and "PROHIBITED" in item["reason"]
                    for item in rejected
                )
            )

    def test_evolution_writes_overlay_not_bundled_pattern(self) -> None:
        before = digest(PATTERN)
        initial_history = len(
            json.loads(PATTERN.read_text(encoding="utf-8")).get("usage_history", [])
        )
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state"
            receipts = state / "receipts"
            outcomes = state / "outcomes"
            receipts.mkdir(parents=True)
            outcomes.mkdir(parents=True)
            for index in range(3):
                receipt = {
                    "retrieval_receipt": {
                        "request_hash": f"case-{index}",
                        "ranked_patterns": [
                            {
                                "pattern_id": "alchemical_nigredo_putrefaction",
                                "total_score": 0.8,
                            }
                        ],
                    }
                }
                (receipts / f"{index}.json").write_text(
                    json.dumps(receipt), encoding="utf-8"
                )
            (outcomes / "success.json").write_text(
                json.dumps(
                    {
                        "pattern_id": "alchemical_nigredo_putrefaction",
                        "project": "test",
                        "outcome": "success",
                    }
                ),
                encoding="utf-8",
            )
            result = self.run_script(EVOLVE, state=state)
            self.assertEqual(result.returncode, 0, result.stderr)
            second = self.run_script(EVOLVE, state=state)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(before, digest(PATTERN))
            overlay = state / "patterns" / "alchemical_nigredo_putrefaction.json"
            self.assertTrue(overlay.is_file())
            data = json.loads(overlay.read_text())
            self.assertEqual(data["pattern_id"], "alchemical_nigredo_putrefaction")
            self.assertEqual(len(data["usage_history"]), initial_history + 2)


if __name__ == "__main__":
    unittest.main()
