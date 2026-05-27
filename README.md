# Icaro

Ferramenta de apoio administrativo para pesquisa de mercado e formacao de cesta de precos a partir de itens informados pelo usuario.

O Icaro organiza uma pesquisa de precos por itens. O usuario informa uma lista de itens individualmente ou por importacao de linhas, e o sistema apoia a busca de valores praticados em contratacoes publicas, especialmente no PNCP, preservando origem, fonte, valor e memoria de calculo.

## Objetivo

Apoiar equipes de compras, planejamento e licitacoes na elaboracao de pesquisa de mercado com maior rastreabilidade por item, padronizacao das fontes e relatorio administrativo de precos praticados.

## Icaro GovLab AtlasNex

O Icaro tambem foi estruturado como uma oferta comercial vinculada ao ecossistema AtlasNex: software, metodo, capacitacao e governanca para orgaos publicos que querem amadurecer processos de licitacao.

Materiais estrategicos:

- `docs/ICARO_GOVLAB_PLANO_ESTRATEGICO.md` - viabilidade, linha do tempo, modelo comercial e caminho de execucao.
- `docs/ICARO_GOVLAB_KIT_PRODUTOS.md` - material detalhado de cada produto da familia Icaro GovLab.
- `docs/ICARO_GOVLAB_IDENTIDADE_VISUAL.md` - arquitetura de marca, paleta, tom de voz e diretrizes visuais.
- `docs/ICARO_PROCESSOS_DE_USO.md` - passo a passo operacional de uso do Icaro.

Paginas:

- Landing Icaro GovLab: `http://127.0.0.1:8100/`
- Login: `http://127.0.0.1:8100/login`
- Area de trabalho: `http://127.0.0.1:8100/app`
- Portal AtlasNex: `http://127.0.0.1:8100/atlasnex`
- Apresentacao Icaro: `http://127.0.0.1:8100/icaro`

## Stack tecnica

| Camada | Tecnologia |
|--------|-----------|
| Backend | FastAPI (Python 3.10+) |
| Servidor ASGI | Uvicorn |
| Banco de dados | SQLite |
| Frontend | HTML/CSS/JS vanilla (SPA em `dashboard.html`) |
| Exports | openpyxl (XLSX), python-docx (DOCX) |
| Lint | ruff |
| Testes | pytest + unittest + httpx |
| Deploy | Render.com (`render.yaml`) |
| CI | GitHub Actions |

## Modulos

1. **Cesta de itens**
   - Cadastro individual de itens.
   - Importacao por linhas, CSV ou XLSX com cabecalhos flexiveis.
   - Termo de busca por item para consulta no PNCP.

2. **Pesquisa de precos**
   - Busca de licitacoes e contratacoes similares no PNCP por termo, periodo, UF e modalidade.
   - Busca contextual com expansao de queries, similaridade Jaccard e ranqueamento.
   - Salvamento de resultados PNCP como rascunhos antes da conversao em amostra aproveitada.
   - Vinculo de fontes a cada item da cesta.
   - Memoria de calculo com media, mediana e tratamento de outliers (IQR).

3. **Atas e caronas**
   - Registro de atas de registro de precos.
   - Verificacao de aderencia, vigencia, fornecedor e quantitativos.

4. **Comparabilidade e revisao**
   - Score multi-fator por fonte (similaridade textual + desvio de preco + UF + aprovacao).
   - Revisao final por item com status (pronto/revisar/pendente).
   - Checklist administrativo de 12 itens.

5. **Relatorio administrativo**
   - Exportacao em Markdown, HTML, DOCX e XLSX.
   - Quadro comparativo, checklist e comparabilidade incluidos.

## Referencias normativas

- Lei n. 14.133/2021, especialmente art. 23.
- IN SEGES/ME n. 65/2021, sobre pesquisa de precos.
- Decreto n. 11.462/2023, sobre sistema de registro de precos.
- Orientacoes e jurisprudencia dos Tribunais de Contas aplicaveis ao ente contratante.

## Como executar

### Pre-requisitos

- Python 3.10+
- Variaveis de ambiente obrigatorias:

```bash
ICARO_AUTH_USER=seu_usuario
ICARO_AUTH_PASSWORD=sua_senha
ICARO_AUTH_SECRET=segredo-para-hmac
```

### Windows (automatico)

```powershell
INICIAR_ICARO.bat
```

O script cria o venv, instala dependencias, define defaults locais para as variaveis de auth e inicia o servidor.

### Manual

```bash
python -m venv venv
# Linux/Mac: source venv/bin/activate
# Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api:app --host 127.0.0.1 --port 8100
```

### Deploy em producao

Configure as variaveis de ambiente no seu provedor (Render, Railway, etc.):

```
ICARO_AUTH_USER=<usuario>
ICARO_AUTH_PASSWORD=<senha_forte>
ICARO_AUTH_SECRET=<segredo_longo_aleatorio>
ICARO_COOKIE_SECURE=1
```

Guia detalhado: `DEPLOY_ONLINE.md`

## Testes

```bash
# Definir variaveis antes de rodar
export ICARO_AUTH_USER=admin
export ICARO_AUTH_PASSWORD=icaro123
export ICARO_AUTH_SECRET=test-secret

python -m pytest tests/ -v
```

Suite atual (20 testes):
- `test_core_flow.py` — Fluxo principal, auth, PNCP, pricing, similaridade.
- `test_reports.py` — Exportacao MD, HTML, DOCX, XLSX.
- `test_upload.py` — Importacao CSV e XLSX via endpoint.
- `test_atas.py` — CRUD de atas de registro de precos.

## Lint

```bash
ruff check src/ api.py tests/
```

Configuracao em `pyproject.toml`.

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) roda automaticamente em todo push e PR:
1. Instala dependencias
2. Roda `ruff check`
3. Roda `pytest`

## API — Endpoints principais

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/processos?limit=50&offset=0` | Lista processos (paginado) |
| POST | `/processos` | Criar processo |
| GET | `/processos/{id}` | Detalhe com itens, fontes, resumo |
| POST | `/itens` | Criar item |
| POST | `/itens/importar` | Importar itens via JSON |
| POST | `/itens/importar-arquivo` | Importar CSV/XLSX |
| POST | `/fontes` | Registrar fonte de preco |
| POST | `/atas` | Registrar ata |
| POST | `/pncp/buscar` | Busca direta no PNCP |
| POST | `/pncp/buscar-contexto` | Busca contextual com similaridade |
| POST | `/pncp/rascunhos` | Salvar rascunho PNCP |
| POST | `/pncp/rascunhos/{id}/fonte` | Converter rascunho em fonte |
| GET | `/processos/{id}/checklist` | Checklist administrativo |
| GET | `/processos/{id}/comparabilidade` | Avaliacao de comparabilidade |
| GET | `/processos/{id}/revisao` | Revisao final por item |
| GET | `/processos/{id}/export/xlsx` | Exportar XLSX |
| GET | `/processos/{id}/export/md` | Exportar Markdown |
| GET | `/processos/{id}/export/html` | Exportar HTML |
| GET | `/processos/{id}/export/docx` | Exportar DOCX |

## Estrutura do projeto

```text
Projeto_Icaro/
  .github/
    workflows/
      ci.yml                  # Pipeline CI
  assets/
    atlasnex-mark.svg
    icaro-logo.svg
  config/
    fontes_pesquisa.json      # Metadata das fontes suportadas
  data/                       # SQLite (gitignored)
  docs/
    MANUAL_ICARO.md
    ICARO_GOVLAB_PLANO_ESTRATEGICO.md
    ICARO_GOVLAB_KIT_PRODUTOS.md
    ICARO_GOVLAB_IDENTIDADE_VISUAL.md
    ICARO_PROCESSOS_DE_USO.md
    FONTES_PUBLICAS_PESQUISA_PRECOS.md
  output/                     # Exports gerados (gitignored)
  src/
    config.py                 # Paths (BASE_DIR, DATA_DIR, OUTPUT_DIR, DB_PATH)
    db.py                     # Persistencia SQLite
    pncp.py                   # Cliente API PNCP + busca contextual
    pricing.py                # Calculos estatisticos (IQR, mediana, media)
    checklist.py              # Geracao de checklist administrativo
    comparability.py          # Score de comparabilidade
    review.py                 # Revisao por item
    reports.py                # Exportacao MD, HTML, DOCX, XLSX
    text_utils.py             # Normalizacao Unicode + tokenizacao
  tests/
    test_core_flow.py
    test_reports.py
    test_upload.py
    test_atas.py
  api.py                      # Aplicacao FastAPI (entry point)
  dashboard.html              # SPA frontend
  landing.html                # Landing page publica
  atlasnex.html               # Hub AtlasNex
  icaro-index.html            # Apresentacao do produto
  github-page.html            # GitHub Pages
  requirements.txt            # Dependencias Python
  pyproject.toml              # Config ruff
  render.yaml                 # Deploy Render.com
  INICIAR_ICARO.bat           # Launcher Windows
  PLANO_PRODUTO_ICARO.md      # Visao de produto
  DEPLOY_ONLINE.md            # Guia de deploy
  REFERENCIAS_NORMATIVAS.md   # Base legal
```

## AtlasNex (portal do ecossistema)

- URL: `http://127.0.0.1:8100/atlasnex`
- Cartoes para **Icaro** e **Hermes** (ativado ao salvar a URL em Integracao).
- Manual do usuario: `http://127.0.0.1:8100/icaro-docs/MANUAL_ICARO.md`
