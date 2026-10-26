# Purple Team Lab

Laboratório educacional para validar respostas defensivas usando eventos fictícios.

## Objetivos

- Simular cenários de segurança sem executar ataques reais.
- Comparar as respostas do Guardian com ações esperadas.
- Registrar resultados em JSON para análise e documentação.

## Requisitos

- Python 3.10 ou superior.
- Projeto `soc-blue-team-lab` presente em `~/soc-blue-team-lab`.

## Executar

```bash
cd ~/purple-team-lab
python src/validator.py
python -m unittest discover -s tests -v
```

O relatório é salvo em `reports/latest-report.json`.

## Segurança

Os endereços usados são exemplos reservados para documentação. Os cenários
não enviam tráfego de ataque, não bloqueiam conexões e não executam ações
defensivas reais. O Guardian é importado do projeto SOC; seu código não é copiado.
