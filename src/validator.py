"""Validação integrada Purple Team, Red Team e Guardian."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "latest-report.json"

SOC_ROOT = Path(
    os.getenv("SOC_ROOT", str(Path.home() / "soc-blue-team-lab"))
)
sys.path.insert(0, str(SOC_ROOT))

from src.guardian.guardian import evaluate_event
from simulator import load_scenarios
from red_team_integration import load_red_team_report


def run_validation():
    results = []

    # Cenários próprios do Purple Team.
    for scenario in load_scenarios():
        response = evaluate_event(scenario["event"])
        expected = scenario["expected_action"]
        actual = response.get("action")

        results.append({
            "id": scenario["id"],
            "name": scenario["name"],
            "source": "purple-team",
            "expected_action": expected,
            "actual_action": actual,
            "reason": response.get("reason"),
            "passed": (
                actual == expected
                and response.get("mode") == "simulation"
                and response.get("executed") is False
            ),
            "mode": response.get("mode"),
            "executed": response.get("executed"),
        })

    # Evidências importadas do Red Team.
    red_report = load_red_team_report()

    for index, event in enumerate(red_report["events"], start=1):
        response = evaluate_event(event)
        expected = "log_only"
        actual = response.get("action")

        results.append({
            "id": f"RT-{index:03d}",
            "name": (
                f"Observação da porta {event['destination_port']}"
            ),
            "source": "red-team-lab",
            "expected_action": expected,
            "actual_action": actual,
            "reason": response.get("reason"),
            "passed": (
                actual == expected
                and response.get("mode") == "simulation"
                and response.get("executed") is False
            ),
            "mode": response.get("mode"),
            "executed": response.get("executed"),
        })

    passed = sum(item["passed"] for item in results)

    report = {
        "project": "Purple Team Lab",
        "simulation_only": True,
        "integration": {
            "red_team_report": red_report["source"],
            "target": red_report["target"],
            "open_ports_observed": red_report["total_open_ports"],
        },
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return report


if __name__ == "__main__":
    report = run_validation()

    for item in report["results"]:
        status = "PASSOU" if item["passed"] else "FALHOU"
        print(
            f'{status} {item["id"]}: {item["name"]} '
            f'[{item["source"]}]'
        )
        if not item["passed"]:
            print(
                f'  Esperado: {item["expected_action"]}; '
                f'Recebido: {item["actual_action"]}'
            )

    print(
        f'\nResultado: {report["passed"]}/{report["total"]} '
        'validações aprovadas.'
    )
    print(f'Relatório: {REPORT}')

    sys.exit(0 if report["failed"] == 0 else 1)
