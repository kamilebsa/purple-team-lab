"""Importação segura de evidências do Red Team Lab."""

import json
from pathlib import Path
from ipaddress import ip_address

DEFAULT_REPORT = (
    Path.home() / "red-team-lab" / "reports" / "port-check.json"
)


def load_red_team_report(report_path=DEFAULT_REPORT):
    path = Path(report_path)

    with path.open(encoding="utf-8") as file:
        report = json.load(file)

    if not isinstance(report, dict):
        raise ValueError("Relatório inválido.")

    if report.get("scope") != "loopback_only":
        raise ValueError("Escopo não permitido.")

    try:
        target = ip_address(report["target"])
    except (KeyError, ValueError, TypeError):
        raise ValueError("Alvo inválido.")

    if not target.is_loopback or target.version != 4:
        raise ValueError("Somente loopback IPv4 é permitido.")

    results = report.get("results")
    if not isinstance(results, list):
        raise ValueError("Resultados inválidos.")

    events = []

    for item in results:
        if not isinstance(item, dict):
            raise ValueError("Resultado de porta inválido.")

        port = item.get("port")
        status = item.get("status")

        if not isinstance(port, int) or isinstance(port, bool):
            raise ValueError("Porta inválida.")

        if not 1 <= port <= 65535:
            raise ValueError("Porta fora do intervalo permitido.")

        if status not in {"open", "closed_or_filtered", "error"}:
            raise ValueError("Status de porta inválido.")

        if status != "open":
            continue

        service = str(item.get("service_hint", "Desconhecido"))

        events.append({
            "event_type": "recon_observation",
            "source_ip": str(target),
            "severity": "INFO",
            "destination_port": port,
            "message": (
                f"Observação simulada do Red Team: "
                f"serviço {service} identificado na porta {port}. "
                "Porta aberta não comprova atividade maliciosa."
            ),
        })

    return {
        "source": "red-team-lab",
        "simulation_only": True,
        "target": str(target),
        "timestamp": report.get("timestamp"),
        "total_open_ports": len(events),
        "events": events,
    }
