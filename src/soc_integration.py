import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT = Path(__file__).resolve().parents[1]
SOC_HOME = Path.home() / "soc-blue-team-lab"
KEY_FILE = Path.home() / ".config/soc-blue-team-lab/api_key"
SCENARIOS_FILE = PROJECT / "scenarios" / "scenarios.json"
BASE_URL = "http://127.0.0.1:8000"


def load_scenarios():
    with SCENARIOS_FILE.open(encoding="utf-8") as f:
        scenarios = json.load(f)
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("Nenhum cenário válido encontrado.")
    return scenarios


def request_json(path, key):
    req = Request(
        BASE_URL + path,
        headers={"X-API-Key": key, "Accept": "application/json"},
    )
    with urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def post_event(event, key):
    body = json.dumps(event).encode("utf-8")
    req = Request(
        BASE_URL + "/events",
        data=body,
        headers={
            "X-API-Key": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(
        description="Integração controlada Purple Team -> SOC local."
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Envia os eventos fictícios e grava novos registros no SOC.",
    )
    args = parser.parse_args()

    try:
        scenarios = load_scenarios()
        print(f"Cenários carregados: {len(scenarios)}")

        for scenario in scenarios:
            print(f"{scenario['id']}: {scenario['name']}")

        if not args.send:
            print("\nMODO DE SIMULAÇÃO: nenhum evento foi enviado.")
            print("Para autorizar o envio, execute novamente com --send.")
            return 0

        if not KEY_FILE.is_file():
            print("ERRO: arquivo local da chave da API não encontrado.")
            return 1

        key = KEY_FILE.read_text(encoding="utf-8").strip()
        if not key:
            print("ERRO: arquivo da chave está vazio.")
            return 1

        # Verifica a autenticação antes de gravar qualquer evento.
        request_json("/stats", key)

        sent = 0
        for scenario in scenarios:
            result = post_event(scenario["event"], key)
            if result.get("message") != "Evento registrado":
                print(f"ERRO ao registrar {scenario['id']}.")
                return 1
            sent += 1
            print(f"Registrado: {scenario['id']}")

        events = request_json("/events", key)
        alerts = request_json("/alerts", key)
        print(f"\nEventos enviados nesta execução: {sent}")
        print(f"Eventos atualmente no SOC: {events.get('total', 'desconhecido')}")
        print(f"Alertas HIGH/CRITICAL atualmente no SOC: {alerts.get('total', 'desconhecido')}")
        print("Aviso: os registros enviados permanecem no banco do SOC.")
        return 0

    except HTTPError as exc:
        print(f"ERRO HTTP: {exc.code}. Nenhuma chave foi exibida.")
        return 1
    except (URLError, TimeoutError) as exc:
        print(f"ERRO de conexão com o SOC: {exc}")
        return 1
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERRO: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
