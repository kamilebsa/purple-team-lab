# Purple Team Lab

Laboratório educacional para testar a correspondência entre eventos de segurança fictícios e respostas defensivas esperadas pelo Guardian do projeto SOC Blue Team Lab.

## Objetivos

- Simular cenários controlados com dados fictícios.
- Validar regras e decisões defensivas.
- Comparar a ação esperada com a ação observada.
- Gerar um relatório JSON reproduzível.
- Documentar resultados e limitações para melhoria contínua da defesa.

## Arquitetura

- `scenarios/scenarios.json`: cenários de teste.
- `src/simulator.py`: suporte à simulação.
- `src/validator.py`: validação local das decisões do Guardian.
- `src/soc_integration.py`: integração opcional com a API SOC.
- `tests/`: testes de cenários, validação e integração.
- `reports/`: relatórios gerados localmente.

O Guardian é importado do projeto `~/soc-blue-team-lab`; seu código não é copiado para este repositório.

## Requisitos

- Python 3.10 ou superior.
- Projeto SOC disponível em `~/soc-blue-team-lab`.
- Dependências necessárias para executar os testes e a API SOC.

## Executar a validação local

```bash
cd ~/purple-team-lab
python -m pytest -q
python src/validator.py
python -m json.tool reports/latest-report.json
```

O relatório contém o total de cenários, os resultados, a ação esperada e a ação observada.

## Integração com o SOC

A integração com a API é separada da validação local. A execução padrão de `src/soc_integration.py` é destinada à conferência sem envio. O argumento `--send` registra eventos no SOC e pode criar registros persistentes.

Não execute novamente com `--send` apenas para repetir os testes: os eventos já enviados permanecem no banco do SOC. Use-o somente quando quiser intencionalmente registrar novos eventos de teste.

A integração autenticada precisa da chave configurada localmente. Nunca publique nem compartilhe a chave.

## Cenários atuais

- `PT-001`: tentativas repetidas de login; espera-se investigar e monitorar.
- `PT-002`: malware simulado; espera-se indicar um candidato a isolamento.
- `PT-003`: atividade suspeita de atenção; espera-se monitorar.

Os resultados anteriores foram 3 de 3 cenários aprovados. Execute a validação novamente para verificar o estado atual.

## Segurança e limites

- Os cenários são educacionais e usam dados fictícios.
- O projeto não executa ataques reais.
- `mode=simulation` indica execução em modo de simulação.
- `executed=false` indica que a ação defensiva não foi executada.
- `isolate_candidate` é uma recomendação, não isolamento efetivo.
- O envio de eventos à API cria registros no banco local do SOC, mas não realiza ataques nem bloqueia conexões.

## Como documentar uma investigação

Para cada cenário, registre:

1. Identificador e objetivo do teste.
2. Evento e severidade simulados.
3. Ação defensiva esperada.
4. Ação observada.
5. Resultado aprovado ou reprovado.
6. Evidências e limitações.
7. Ajuste recomendado para a regra de detecção, se necessário.

## Objetivo de aprendizagem

Praticar validação de detecções, colaboração Purple Team, integração com um SOC, testes automatizados e documentação de evidências em um laboratório autorizado.
