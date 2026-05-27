# Changelog

Todas as mudancas relevantes do projeto Icaro sao documentadas aqui.

## [0.2.0] - 2026-05-27

### Seguranca
- Removidas credenciais padrao hardcoded (`admin/icaro123`) do codigo-fonte.
- Variaveis de ambiente `ICARO_AUTH_USER`, `ICARO_AUTH_PASSWORD` e `ICARO_AUTH_SECRET` agora sao obrigatorias — a aplicacao falha no startup se nao estiverem definidas.
- `INICIAR_ICARO.bat` define defaults locais para desenvolvimento.

### Arquitetura
- Migrado `@app.on_event("startup")` (depreciado) para `lifespan` async context manager.
- Removido `src/models.py` (dataclasses orfaos nunca importados pelo sistema).
- `gerar_relatorio_html` nao grava mais arquivo `.md` intermediario no disco — markdown gerado em memoria via `_build_markdown_lines`.
- `GET /processos` agora aceita `?limit=50&offset=0` e retorna `{items, total, limit, offset}` (paginacao).

### CI/CD
- Adicionado GitHub Actions (`.github/workflows/ci.yml`) com lint e testes em todo push/PR.
- Adicionado linter `ruff` com configuracao em `pyproject.toml` (regras E, F, W).
- Corrigida variavel nao utilizada em `src/reports.py` detectada pelo ruff.

### Testes
- Adicionado `tests/test_reports.py` — 5 testes cobrindo exportacao MD, HTML, DOCX e XLSX.
- Adicionado `tests/test_upload.py` — 3 testes cobrindo importacao CSV, XLSX e rejeicao de formato invalido.
- Adicionado `tests/test_atas.py` — 2 testes cobrindo CRUD completo de atas e 404.
- Suite total: 20 testes (anteriormente 10).

### Documentacao
- README reescrito com stack tecnica, tabela de endpoints, instrucoes de testes/lint/CI, estrutura atualizada do projeto e requisitos de deploy.

---

## [0.1.0] - 2026-05-19

### MVP inicial
- API FastAPI com SQLite para persistencia.
- Cadastro de processos de pesquisa de mercado.
- Cesta de itens com importacao CSV/XLSX.
- Integracao com PNCP (busca direta e contextual com similaridade Jaccard).
- Fluxo de rascunhos PNCP com revisao e conversao em fonte.
- Calculo estatistico de precos (media, mediana, IQR, outliers).
- Score de comparabilidade multi-fator.
- Checklist administrativo (12 itens).
- Revisao final por item (pronto/revisar/pendente).
- Exportacao de relatorios em MD, HTML, DOCX e XLSX.
- Autenticacao por cookie com HMAC-SHA256.
- Hub AtlasNex e paginas de apresentacao.
- 10 testes unitarios/integracao cobrindo fluxo principal.
- Deploy configurado para Render.com (`render.yaml`).
