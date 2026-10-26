import json
import sys
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import simulator


def valid_scenario():
    return {
        "id": "PT-TEST",
        "name": "Cenário de teste",
        "event": {
            "event_type": "suspicious_activity",
            "source_ip": "192.0.2.50",
            "severity": "WARNING",
            "message": "Evento fictício de teste",
        },
        "expected_action": "monitor",
    }


class SimulatorValidationTests(unittest.TestCase):
    def load_from_data(self, data):
        content = json.dumps(data)
        with patch.object(
            simulator,
            "SCENARIOS_FILE",
            ROOT / "scenarios" / "arquivo-ficticio.json",
        ), patch.object(
            Path,
            "open",
            mock_open(read_data=content),
        ):
            return simulator.load_scenarios()

    def test_accepts_valid_scenario(self):
        self.assertEqual(len(self.load_from_data([valid_scenario()])), 1)

    def test_rejects_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError, "duplicado"):
            self.load_from_data([valid_scenario(), valid_scenario()])

    def test_rejects_missing_required_field(self):
        scenario = valid_scenario()
        del scenario["expected_action"]
        with self.assertRaisesRegex(ValueError, "ausente"):
            self.load_from_data([scenario])

    def test_rejects_invalid_severity(self):
        scenario = valid_scenario()
        scenario["event"]["severity"] = "EXTREME"
        with self.assertRaisesRegex(ValueError, "severidade inválida"):
            self.load_from_data([scenario])


if __name__ == "__main__":
    unittest.main()
