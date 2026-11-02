# Purple Team Lab

Laboratório educacional para validar decisões defensivas do Guardian do SOC Blue Team Lab e integrar evidências do Red Team Lab.

## Objetivos

- Validar decisões defensivas do Guardian.
- Testar cenários simulados de segurança.
- Importar relatórios de reconhecimento do Red Team.
- Verificar respostas esperadas e evitar falsos alertas.
- Gerar relatórios JSON reproduzíveis.

## Arquitetura

| Componente | Responsabilidade |
|---|---|
| `scenarios/scenarios.json` | Define os cenários Purple |
| `src/simulator.py` | Carrega e valida cenários |
| `src/red_team_integration.py` | Importa e valida relatórios do Red Team |
| `src/validator.py` | Executa a validação integrada com o Guardian |
| `src/soc_integration.py` | Integração autenticada com a API do SOC |
| `tests/` | Testes automatizados |
| `reports/` | Relatórios locais |

O Guardian é utilizado diretamente do repositório SOC Blue Team Lab. Seu código não é duplicado.

## Fluxo integrado

1. Red Team Lab realiza verificações controladas no loopback IPv4.
2. O Red Team gera `reports/port-check.json`.
3. Purple Team importa e valida o relatório.
4. Purple Team prepara eventos de observação para as portas abertas.
5. Guardian avalia os eventos em modo de simulação.
6. Purple Team registra os resultados em `reports/latest-report.json`.

Observações de portas abertas recebem severidade INFO e devem resultar em `log_only`. Uma porta aberta, isoladamente, não comprova atividade maliciosa.

## Requisitos

- Python 3.10 ou superior.
- Repositórios Red Team Lab e SOC Blue Team Lab disponíveis localmente.
- Dependências de desenvolvimento instaladas.

## Executar o laboratório

```bash
cd ~/purple-team-lab
SOC_ROOT="$HOME/soc-blue-team-lab" python -m pytest -q
SOC_ROOT="$HOME/soc-blue-team-lab" python src/validator.py
python -m json.tool reports/latest-report.json

Depois dessa conferência, vamos preparar o commit e a versão **v1.2.0** do Purple Team. Não publique ainda: primeiro quero ver a saída.
