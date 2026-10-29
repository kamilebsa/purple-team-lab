# Purple Team Lab

Laboratório educacional para validar decisões defensivas do Guardian do projeto SOC Blue Team Lab usando eventos fictícios e cenários controlados.

## Objetivos

- Simular cenários controlados com dados fictícios.
- Validar regras e decisões defensivas.
- Comparar ações esperadas e observadas.
- Gerar relatórios JSON reproduzíveis.
- Documentar evidências, resultados e limitações.

## Arquitetura

- `scenarios/scenarios.json`: cenários de teste.
- `src/simulator.py`: carregamento e validação dos cenários.
- `src/validator.py`: validação local das decisões do Guardian.
- `src/soc_integration.py`: integração opcional com a API SOC.
- `tests/`: testes automatizados.
- `reports/`: relatórios gerados localmente.

O Guardian é importado de `~/soc-blue-team-lab`; seu código não é duplicado neste repositório.

## Requisitos

- Python 3.10 ou superior.
- Projeto SOC disponível em `~/soc-blue-team-lab`.
- Dependências necessárias para os testes e a API SOC.

## Validação local

```bash
cd ~/purple-team-lab
python -m pytest -q
python src/validator.py
python -m json.tool reports/latest-report.json
```

A validação local compara as ações esperadas com as decisões retornadas pelo Guardian.

## Integração com o SOC

Por padrão, `src/soc_integration.py` apenas lista os cenários e não envia eventos.

O argumento `--send` envia eventos fictícios à API SOC, cria registros persistentes e consulta as decisões do Guardian. Use-o somente quando quiser registrar intencionalmente novos eventos de teste.

A integração autenticada exige a chave configurada localmente em `~/.config/soc-blue-team-lab/api_key`. Nunca publique nem compartilhe essa chave.

## Cenários

- `PT-001`: tentativas repetidas de login; ação esperada `investigate_and_monitor`.
- `PT-002`: malware simulado; ação esperada `isolate_candidate`.
- `PT-003`: atividade suspeita; ação esperada `monitor`.

## Segurança e limitações

- Os cenários usam dados fictícios em um laboratório educacional.
- O projeto não executa ataques reais.
- `mode=simulation` identifica uma decisão em modo de simulação.
- `executed=false` significa que a ação defensiva não foi executada.
- `isolate_candidate` é uma recomendação, não isolamento efetivo.
- O envio de eventos ao SOC não bloqueia conexões nem executa isolamento.

## Evidências de investigação

Para cada cenário, documente:

1. Identificador e objetivo.
2. Evento e severidade.
3. Ação esperada e ação observada.
4. Resultado do teste.
5. Evidências, limitações e melhorias recomendadas.

## Objetivo de aprendizagem

Praticar validação de detecções, integração com SOC, testes automatizados e documentação de evidências em um laboratório autorizado.
