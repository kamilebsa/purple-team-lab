import importlib
import sys

import pytest


def test_soc_api_contract_uses_isolated_storage(tmp_path, monkeypatch):
    soc_root = __import__("os").environ.get("SOC_ROOT")
    if not soc_root:
        pytest.skip("SOC_ROOT não configurado")

    monkeypatch.setenv("SIEM_DB_FILE", str(tmp_path / "test-siem.db"))
    monkeypatch.setenv(
        "SIEM_EVENTS_FILE", str(tmp_path / "test-events.jsonl")
    )
    monkeypatch.setenv("SIEM_API_KEY", "test-only-key")

    sys.path.insert(0, soc_root)
    try:
        for name in ("src.siem.api",):
            sys.modules.pop(name, None)

        api_module = importlib.import_module("src.siem.api")
        from fastapi.testclient import TestClient

        client = TestClient(api_module.app)

        response = client.get(
            "/stats", headers={"X-API-Key": "test-only-key"}
        )
        assert response.status_code == 200
        assert response.json()["total_events"] == 0

        event = {
            "event_type": "malware_detected",
            "source_ip": "192.0.2.20",
            "severity": "CRITICAL",
            "message": "Teste fictício de contrato da API",
        }
        response = client.post(
            "/events",
            json=event,
            headers={"X-API-Key": "test-only-key"},
        )
        assert response.status_code == 200
        event_id = response.json()["event"]["id"]

        response = client.get(
            "/guardian", headers={"X-API-Key": "test-only-key"}
        )
        assert response.status_code == 200
        decisions = response.json()["decisions"]
        decision = next(
            item for item in decisions if item["event_id"] == event_id
        )
        assert decision["action"] == "isolate_candidate"
        assert decision["mode"] == "simulation"
        assert decision["executed"] is False

        unauthorized = client.get("/stats")
        assert unauthorized.status_code == 401
    finally:
        sys.modules.pop("src.siem.api", None)
        if soc_root in sys.path:
            sys.path.remove(soc_root)
