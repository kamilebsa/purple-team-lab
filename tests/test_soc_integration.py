import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from soc_integration import compare_decisions


def test_matching_decision_passes():
    scenarios = [{"id": "PT-001", "expected_action": "monitor"}]
    sent_ids = {"PT-001": 101}
    guardian = {"decisions": [{
        "event_id": 101,
        "action": "monitor",
        "mode": "simulation",
        "executed": False,
    }]}

    result = compare_decisions(scenarios, sent_ids, guardian)
    assert result[0]["passed"] is True


def test_wrong_action_fails():
    scenarios = [{"id": "PT-001", "expected_action": "monitor"}]
    guardian = {"decisions": [{
        "event_id": 101,
        "action": "log_only",
        "mode": "simulation",
        "executed": False,
    }]}

    result = compare_decisions(scenarios, {"PT-001": 101}, guardian)
    assert result[0]["passed"] is False


def test_missing_decision_fails():
    scenarios = [{"id": "PT-001", "expected_action": "monitor"}]
    result = compare_decisions(
        scenarios, {"PT-001": 101}, {"decisions": []}
    )
    assert result[0]["passed"] is False


def test_executed_action_fails():
    scenarios = [{"id": "PT-001", "expected_action": "monitor"}]
    guardian = {"decisions": [{
        "event_id": 101,
        "action": "monitor",
        "mode": "simulation",
        "executed": True,
    }]}

    result = compare_decisions(scenarios, {"PT-001": 101}, guardian)
    assert result[0]["passed"] is False
