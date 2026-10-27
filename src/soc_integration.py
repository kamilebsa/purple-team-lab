"""Integração controlada entre Purple Team e SOC local."""
import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT = Path(__file__).resolve().parents[1]
KEY_FILE = Path.home() / ".config/soc-blue-team-lab/api_key"
SCENARIOS_FILE = PROJECT / "scenarios" / "scenarios.json"
BASE_URL = "http://127.0.0.1:8000"


def load_scenarios():
    with SCENARIOS_FILE.open(encoding="utf-8") as file:
        scenarios = json.load(file)

    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("Nenhum cenário válido encontrado.")

    return scenarios


def request_json(path, key):
    request = Request(
        BASE_URL + path,
        headers={"X-API-Key": key, "Accept": "application/json"},
    )
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def post_event(event, key):
    body = json.dumps(event).encode("utf-8")
    request = Request(
        BASE_URL + "/events",
        data=body,
        headers={
            "X-API-Key": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def compare_decisions(scenarios, sent_ids, guardian_data):
    """Compara somente decisões correspondentes aos eventos desta execução."""
    decisions = guardian_data.get("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("Resposta inválida: decisions não é uma lista.")

    by_id = {}
    for decision in decisions:
        event_id = decision.get("event_id")
        if event_id is not None:
            by_id[event_id] = decision

    results = []
    for scenario in scenarios:
        scenario_id = scenario["id"]
        event_id = sent_ids.get(scenario_id)
        decision = by_id.get(event_id) if event_id is not None else None
        expected = scenario["expected_action"]

        actual = decision.get("action") if decision else None
        mode = decision.get("mode") if decision else None
        executed = decision.get("executed") if decision else None

        passed = (
            decision is not None
            and actual == expected
            and mode == "simulation"
            and executed is False
        )

        results.append({
            "scenario_id": scenario_id,
            "event_id": event_id,
            "expected_action": expected,
            "actual_action": actual,
            "mode": mode,
            "executed": executed,
            "passed": passed,
        })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Integração controlada Purple Team -> SOC local."
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Envia eventos fictícios e grava registros no SOC.",
    )
    args = parser.parse_args()

    try:
        scenarios = load_scenarios()
        print(f"Cenários carregados: {len(scenarios)}")
        for scenario in scenarios:
            print(f"{scenario['id']}: {scenario['name']}")

        if not args.send:
            print("\nMODO DE SIMULAÇÃO: nenhum evento foi enviado.")
            print("A validação real exige autorização explícita com --send.")
            return 0

        if not KEY_FILE.is_file():
            print("ERRO: arquivo local da chave da API não encontrado.")
            return 1

        key = KEY_FILE.read_text(encoding="utf-8").strip()
        if not key:
            print("ERRO: arquivo da chave está vazio.")
            return 1

        # Confirma a autenticação antes de criar registros.
        request_json("/stats", key)

        sent_ids = {}
        for scenario in scenarios:
            response = post_event(scenario["event"], key)
            event = response.get("event", {})

            if (
                response.get("message") != "Evento registrado"
                or event.get("id") is None
            ):
                print(f"ERRO: resposta inesperada para {scenario['id']}.")
                return 1

            sent_ids[scenario["id"]] = event["id"]
            print(f"Registrado: {scenario['id']} (ID {event['id']})")

        guardian_data = request_json("/guardian", key)
        results = compare_decisions(scenarios, sent_ids, guardian_data)

        print("\n===== VALIDACAO DO GUARDIAN =====")
        for result in results:
            status = "PASSOU" if result["passed"] else "FALHOU"
            print(
                f"{status} {result['scenario_id']}: "
                f"esperado={result['expected_action']}, "
                f"recebido={result['actual_action']}, "
                f"modo={result['mode']}, "
                f"executed={result['executed']}"
            )

        passed = sum(item["passed"] for item in results)
        failed = len(results) - passed
        print(f"\nResultado: {passed}/{len(results)} cenários aprovados.")
        print("Os eventos enviados permanecem gravados no SOC.")
        return 0 if failed == 0 else 1

    except HTTPError as exc:
        print(f"ERRO HTTP: {exc.code}. Nenhuma chave foi exibida.")
        if exc.code == 401:
            print("Verifique a configuração da autenticação da API.")
        return 1
    except (URLError, TimeoutError) as exc:
        print(f"ERRO de conexão com o SOC: {exc}")
        return 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERRO: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
