# Purple Team Lab

Laboratório educacional para validar decisões defensivas do Guardian do projeto SOC Blue Team Lab usando eventos fictícios e cenários controlados.

## Objetivos

- Testar a integração HTTP com a API do SOC.
- Verificar autenticação e contratos da API.
- Gerar relatórios JSON reproduzíveis.
- Documentar resultados, limitações e melhorias.

## Arquitetura

| Componente | Responsabilidade |
|---|---|
| `scenarios/scenarios.json` | Define os cenários de teste |
| `src/simulator.py` | Carrega e valida os cenários |
| `src/validator.py` | Compara as ações esperadas com as decisões do Guardian |
| `src/soc_integration.py` | Permite testar a integração com a API SOC |
| `tests/` | Contém os testes automatizados |
| `reports/` | Recebe relatórios locais da validação |

O Guardian é utilizado a partir do repositório `soc-blue-team-lab`. Seu código não é duplicado neste projeto.

## Requisitos

- Python 3.10 ou superior.
- Repositório SOC Blue Team Lab disponível localmente.
- Dependências de desenvolvimento do Purple Team e dependências da API SOC para os testes de integração.

## Executar o laboratório

```bash
cd ~/purple-team-lab
SOC_ROOT="$HOME/soc-blue-team-lab" python -m pytest -q tests
SOC_ROOT="$HOME/soc-blue-team-lab" python src/validator.py
python -m json.tool reports/latest-report.json
```

## Integração com o SOC

Por padrão, `src/soc_integration.py` permite testar a integração sem enviar eventos persistentes.

O argumento `--send` envia eventos fictícios à API do SOC e pode criar registros persistentes. Use-o somente em ambiente controlado e quando quiser realizar esse envio intencionalmente.

A integração autenticada utiliza uma chave configurada localmente em `~/.config/soc-blue-team-lab/api_key`. Nunca publique nem compartilhe essa chave.

A validação local compara as ações esperadas com as decisões retornadas pelo Guardian.

## Limitações

- Os cenários são simulados e não representam ataques reais.
- O laboratório não executa isolamento real de máquinas.
- Os resultados dependem da implementação e configuração do SOC Blue Team Lab.

## Melhorias futuras

- Ampliar os cenários de teste.
- Melhorar a cobertura dos contratos da API.
- Expandir os relatórios e as evidências de validação.
- Documentar novas regras de detecção e resultados.

## Finalidade

Projeto de estudo e portfólio em cibersegurança, com foco em Blue Team, Purple Team, validação de detecção e integração com ferramentas defensivas.
