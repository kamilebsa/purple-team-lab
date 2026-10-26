import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from simulator import load_scenarios
from validator import run_validation


class PurpleTeamTests(unittest.TestCase):
    def test_scenarios_have_unique_ids(self):
        scenarios = load_scenarios()
        ids = [item["id"] for item in scenarios]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreater(len(scenarios), 0)

    def test_validation_report_is_simulation_only(self):
        report = run_validation()
        self.assertTrue(report["simulation_only"])
        self.assertEqual(report["total"], 3)
        self.assertEqual(report["failed"], 0)

    def test_guardian_does_not_execute_actions(self):
        report = run_validation()
        for result in report["results"]:
            self.assertFalse(result["executed"])


if __name__ == "__main__":
    unittest.main()
