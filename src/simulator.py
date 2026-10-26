"""Carrega e valida cenários fictícios de testes defensivos locais."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_FILE = ROOT / "scenarios" / "scenarios.json"

REQUIRED_EVENT_FIELDS = {
    "event_type": str,
    "source_ip": str,
    "severity": str,
    "message": str,
}
ALLOWED_SEVERITIES = {"LOW", "MEDIUM", "WARNING", "HIGH", "CRITICAL"}
ALLOWED_ACTIONS = {
    "investigate_and_monitor",
    "isolate_candidate",
    "monitor",
    "log_only",
}


def load_scenarios():
    try:
        with SCENARIOS_FILE.open(encoding="utf-8") as file:
            scenarios = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON de cenários inválido: {exc}") from exc

    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("Os cenários devem estar em uma lista não vazia.")

    seen_ids = set()

    for index, scenario in enumerate(scenarios):
        label = f"Cenário na posição {index}"

        if not isinstance(scenario, dict):
            raise ValueError(f"{label}: deve ser um objeto.")

        for field in ("id", "name", "event", "expected_action"):
            if field not in scenario:
                raise ValueError(f"{label}: campo obrigatório ausente: {field}.")

        for field in ("id", "name", "expected_action"):
            if not isinstance(scenario[field], str) or not scenario[field].strip():
                raise ValueError(f"{label}: {field} deve ser texto não vazio.")

        scenario_id = scenario["id"]
        if scenario_id in seen_ids:
            raise ValueError(f"ID de cenário duplicado: {scenario_id}.")
        seen_ids.add(scenario_id)

        if scenario["expected_action"] not in ALLOWED_ACTIONS:
            raise ValueError(
                f"{label}: ação esperada não permitida: "
                f"{scenario['expected_action']}."
            )

        event = scenario["event"]
        if not isinstance(event, dict):
            raise ValueError(f"{label}: event deve ser um objeto.")

        for field, expected_type in REQUIRED_EVENT_FIELDS.items():
            value = event.get(field)
            if not isinstance(value, expected_type) or not value.strip():
                raise ValueError(
                    f"{label}: event.{field} deve ser texto não vazio."
                )

        if event["severity"] not in ALLOWED_SEVERITIES:
            raise ValueError(
                f"{label}: severidade inválida: {event['severity']}."
            )

    return scenarios
