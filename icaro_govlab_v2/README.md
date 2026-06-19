# Icaro GovLab v2

Plataforma de inteligencia para pesquisa de precos publicos baseada em:

`CESTA -> ITENS -> FONTES -> VALORES -> MEMORIA DE CALCULO`

## Objetivo

O Icaro GovLab v2 nao e um gerador de cestas fechadas ou formularios prontos. Ele organiza uma pesquisa de mercado defensavel, com composicao dinamica de cestas, busca por item, rastreabilidade das fontes, validacao de valores e memoria de calculo auditavel.

## MVP

O MVP permite:

- criar cesta dinamica;
- adicionar itens individualmente;
- registrar fontes com contexto obrigatorio;
- registrar valores vinculados a fontes;
- aceitar ou descartar valores com justificativa;
- gerar memoria de calculo por item e por cesta;
- exportar relatorio tecnico em Markdown;
- registrar logs de busca e validacoes de fonte.

## Entidades principais

- `baskets`
- `basket_items`
- `item_sources`
- `source_prices`
- `calculation_memories`
- `search_logs`
- `normalization_rules`
- `source_validations`

## Rodar localmente

```powershell
cd icaro_govlab_v2
python -m uvicorn app.main:app --reload --port 8200
```

Abra:

```text
http://127.0.0.1:8200
```

## Testes

```powershell
python -m unittest discover -s tests
```
