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


def test_red_team_event_is_imported(monkeypatch):
    import red_team_integration
    from soc_integration import load_red_team_events

    monkeypatch.setattr(
        red_team_integration,
        "load_red_team_report",
        lambda: {
            "simulation_only": True,
            "events": [{
                "event_type": "recon_observation",
                "source_ip": "127.0.0.1",
                "severity": "INFO",
                "destination_port": 8000,
                "message": "Observação simulada",
            }],
        },
    )

    events = load_red_team_events()

    assert len(events) == 1
    assert events[0]["id"] == "RT-8000"
    assert events[0]["event"]["severity"] == "INFO"
    assert events[0]["event"]["destination_port"] == 8000
    assert events[0]["expected_action"] == "log_only"


def test_red_team_rejects_non_simulation_report(monkeypatch):
    import pytest
    import red_team_integration
    from soc_integration import load_red_team_events

    monkeypatch.setattr(
        red_team_integration,
        "load_red_team_report",
        lambda: {
            "simulation_only": False,
            "events": [],
        },
    )

    with pytest.raises(ValueError, match="modo de simulação"):
        load_red_team_events()


def test_red_team_decision_requires_log_only():
    from soc_integration import compare_red_team_decisions

    events = [{
        "id": "RT-8000",
        "expected_action": "log_only",
    }]
    guardian = {"decisions": [{
        "event_id": 37,
        "action": "log_only",
        "mode": "simulation",
        "executed": False,
    }]}

    result = compare_red_team_decisions(
        events, {"RT-8000": 37}, guardian
    )

    assert result[0]["passed"] is True


def test_red_team_rejects_executed_action():
    from soc_integration import compare_red_team_decisions

    events = [{
        "id": "RT-8000",
        "expected_action": "log_only",
    }]
    guardian = {"decisions": [{
        "event_id": 37,
        "action": "log_only",
        "mode": "simulation",
        "executed": True,
    }]}

    result = compare_red_team_decisions(
        events, {"RT-8000": 37}, guardian
    )

    assert result[0]["passed"] is False
