# Icaro

Ferramenta de apoio administrativo para pesquisa de mercado e formacao de cesta de precos a partir de itens informados pelo usuario.

O Icaro organiza uma pesquisa de precos por itens. O usuario informa uma lista de itens individualmente ou por importacao de linhas, e o sistema apoia a busca de valores praticados em contratacoes publicas, especialmente no PNCP, preservando origem, fonte, valor e memoria de calculo.

## Objetivo

Apoiar equipes de compras, planejamento e licitacoes na elaboracao de pesquisa de mercado com maior rastreabilidade por item, padronizacao das fontes e relatorio administrativo de precos praticados.

## Modulos previstos

1. **Cesta de itens**
   - Cadastro individual de itens.
   - Importacao por linhas, CSV ou XLSX com cabecalhos flexiveis.
   - Termo de busca por item para consulta no PNCP.

2. **Pesquisa de precos**
   - Busca de licitacoes e contratacoes similares no PNCP por termo, periodo, UF e modalidade.
   - Salvamento de resultados PNCP como rascunhos de fonte antes da conversao em amostra aproveitada.
   - Vinculo de fontes a cada item da cesta.
   - Agrupamento por item, unidade, quantidade e localidade.
   - Memoria de calculo com media, mediana e tratamento de valores extremos.
   - Registro das fontes consultadas e justificativas.

3. **Atas e caronas**
   - Busca de atas de registro de precos vigentes.
   - Verificacao inicial de aderencia do objeto.
   - Controle de vigencia, fornecedor, orgao gerenciador e quantitativos.
   - Checklist para adesao, conforme regras aplicaveis.

4. **Processo preparatorio**
   - Checklist de documentos.
   - Minutas e modelos de justificativa.
   - Organizacao do estudo tecnico preliminar, termo de referencia e pesquisa de mercado.

5. **Relatorio administrativo**
   - Relatorio de pesquisa de precos.
   - Quadro comparativo.
   - Revisao final por item antes da exportacao.
   - Justificativa da metodologia.
   - Registro de descartes de valores inconsistentes, inexequiveis ou excessivos.

## Referencias iniciais

- Lei nº 14.133/2021, especialmente art. 23.
- IN SEGES/ME nº 65/2021, sobre pesquisa de precos.
- Decreto nº 11.462/2023, sobre sistema de registro de precos.
- Orientacoes e jurisprudencia dos Tribunais de Contas aplicaveis ao ente contratante.

## Estado atual

MVP local com API FastAPI, banco SQLite, cadastro de pesquisas, cesta de itens, importacao CSV/XLSX, rascunhos PNCP, lancamento de fontes por item, calculo de media/mediana, comparabilidade, checklist, revisao final por item, consulta contextual ao PNCP e exportacoes MD/HTML/DOCX/XLSX. O **hub AtlasNex** (`/atlasnex`) agrega links ao Icaro e ao Hermes sem unificar backends.

## AtlasNex (portal do ecossistema)

- URL: `http://127.0.0.1:8100/atlasnex` (mesma estrutura visual do portal Hermes: holding + ecossistema). Apresentação do produto Ícaro: `http://127.0.0.1:8100/icaro`.
- Cartoes para **Icaro** (abrir em nova aba ou iframe na mesma origem) e **Hermes** (ativado ao salvar a URL em **Integracao**).
- Manual do usuario: `http://127.0.0.1:8100/icaro-docs/MANUAL_ICARO.md` ou ficheiro `docs/MANUAL_ICARO.md`.

## Como executar

No Windows, use:

```powershell
INICIAR_ICARO.bat
```

Ou manualmente:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn api:app --host 127.0.0.1 --port 8100
```

Depois acesse:

```text
http://127.0.0.1:8100
http://127.0.0.1:8100/icaro
http://127.0.0.1:8100/landing
http://127.0.0.1:8100/github-page
http://127.0.0.1:8100/atlasnex
```

## Estrutura

```text
Icaro/
  assets/
    atlasnex-mark.svg
    icaro-logo.svg
  config/
  data/
  docs/
    MANUAL_ICARO.md
    GITHUB_PAGE_MODELO.md
  output/
  src/
  api.py
  atlasnex.html
  github-page.html
  landing.html
  icaro-index.html
  dashboard.html
  requirements.txt
  INICIAR_ICARO.bat
  README.md
  PLANO_PRODUTO_ICARO.md
  REFERENCIAS_NORMATIVAS.md
```
