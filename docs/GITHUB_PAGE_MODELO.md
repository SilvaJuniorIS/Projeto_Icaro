# Icaro

Pesquisa de precos no PNCP para cestas de itens, com rascunhos de fonte, revisao por item e relatorios exportaveis.

## Recursos

- Cadastro manual ou importacao CSV/XLSX de itens.
- Busca PNCP por termo, UF, modalidade e periodo.
- Persistencia de resultados PNCP como rascunhos antes de virar fonte de preco.
- Conversao de rascunho em fonte com valor unitario revisado.
- Revisao final por item com status e pendencias.
- Exportacao DOCX, HTML, Markdown e XLSX.

## Como rodar

```powershell
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\uvicorn api:app --host 127.0.0.1 --port 8100
```

Depois acesse:

- Dashboard: `http://127.0.0.1:8100`
- Landing page: `http://127.0.0.1:8100/landing`
- Pagina modelo GitHub: `http://127.0.0.1:8100/github-page`

## Fluxo de trabalho

1. Crie uma pesquisa de mercado.
2. Cadastre ou importe a cesta de itens.
3. Busque contratacoes no PNCP com filtros.
4. Salve resultados promissores como rascunhos.
5. Converta rascunhos em fontes depois de revisar o valor unitario.
6. Confira a revisao final por item.
7. Exporte o relatorio.

## Formato de importacao

Arquivos CSV e XLSX podem usar os cabecalhos:

| Campo | Obrigatorio | Exemplo |
| --- | --- | --- |
| codigo | Nao | 001 |
| descricao | Sim | Papel A4 sulfite 75g |
| unidade | Nao | resma |
| quantidade | Nao | 10 |
| categoria | Nao | material de consumo |
| termo_busca | Nao | papel A4 |
| especificacao | Nao | Formato A4, branco, 75g/m2 |

## Observacao

O Icaro apoia a instrucao administrativa e nao substitui a analise tecnica, juridica ou de controle interno.
