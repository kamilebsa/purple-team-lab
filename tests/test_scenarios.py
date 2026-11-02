import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from simulator import load_scenarios
from validator import run_validation
from red_team_integration import load_red_team_report


class PurpleTeamTests(unittest.TestCase):
    def test_scenarios_have_unique_ids(self):
        scenarios = load_scenarios()
        ids = [item["id"] for item in scenarios]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreater(len(scenarios), 0)

    def test_validation_report_is_simulation_only(self):
        report = run_validation()
        red_report = load_red_team_report()

        expected_total = len(load_scenarios()) + red_report["total_open_ports"]

        self.assertTrue(report["simulation_only"])
        self.assertEqual(report["total"], expected_total)
        self.assertEqual(report["failed"], 0)

    def test_red_team_evidence_is_integrated(self):
        report = run_validation()
        red_results = [
            item for item in report["results"]
            if item["source"] == "red-team-lab"
        ]

        self.assertEqual(
            len(red_results),
            load_red_team_report()["total_open_ports"],
        )

        for result in red_results:
            self.assertEqual(result["expected_action"], "log_only")
            self.assertEqual(result["actual_action"], "log_only")
            self.assertTrue(result["passed"])

    def test_guardian_does_not_execute_actions(self):
        report = run_validation()

        for result in report["results"]:
            self.assertFalse(result["executed"])
            self.assertEqual(result["mode"], "simulation")


if __name__ == "__main__":
    unittest.main()
