"""Compara respostas simuladas com as ações esperadas do Guardian."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "latest-report.json"

# Permite importar o Guardian do projeto SOC sem copiar seu código.
import os
SOC_ROOT = Path(os.getenv("SOC_ROOT", str(Path.home() / "soc-blue-team-lab")))
sys.path.insert(0, str(SOC_ROOT))

from src.guardian.guardian import evaluate_event
from simulator import load_scenarios


def run_validation():
    results = []

    for scenario in load_scenarios():
        response = evaluate_event(scenario["event"])
        expected = scenario["expected_action"]
        actual = response.get("action")
        results.append({
            "id": scenario["id"],
            "name": scenario["name"],
            "expected_action": expected,
            "actual_action": actual,
            "reason": response.get("reason"),
            "passed": actual == expected,
            "mode": response.get("mode"),
            "executed": response.get("executed"),
        })

    report = {
        "project": "Purple Team Lab",
        "simulation_only": True,
        "total": len(results),
        "passed": sum(item["passed"] for item in results),
        "failed": sum(not item["passed"] for item in results),
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
        print(f'{status} {item["id"]}: {item["name"]}')
        if not item["passed"]:
            print(
                f'  Esperado: {item["expected_action"]}; '
                f'Recebido: {item["actual_action"]}'
            )
    print(f'Resultado: {report["passed"]}/{report["total"]} cenários')
    print(f'Relatório: {REPORT}')
    sys.exit(0 if report["failed"] == 0 else 1)
