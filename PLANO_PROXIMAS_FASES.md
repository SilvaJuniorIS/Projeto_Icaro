# Plano de Proximas Fases — Projeto Icaro

## Visao geral

Este documento descreve as proximas evolucoes planejadas apos a conclusao das melhorias prioritarias (v0.2.0). As fases estao organizadas por valor de entrega e complexidade crescente.

---

## Fase 5 — Robustez e Observabilidade

### 5.1 Migracoes de schema estruturadas
- Adotar sistema leve de migracoes (ex: `yoyo-migrations` ou versionamento manual com tabela `schema_version`).
- Eliminar `ALTER TABLE` ad-hoc dentro de `init_db()`.
- Garantir que upgrades de schema sejam idemponentes e reversiveis.

### 5.2 Logging estruturado
- Adicionar logging com `structlog` ou `logging` padrao em todos os modulos.
- Registrar chamadas ao PNCP (tempo de resposta, erros, termos buscados).
- Facilitar diagnostico em producao sem depender de print/debug.

### 5.3 Health check aprimorado
- Endpoint `/health` deve verificar conexao com SQLite e retornar versao do schema.
- Incluir uptime e contagem de processos ativos.

---

## Fase 6 — Experiencia do Usuario

### 6.1 Componentizacao do frontend
- Migrar `dashboard.html` (3500+ linhas) para modulos JS separados ou framework leve (Alpine.js / htmx).
- Separar CSS em arquivo dedicado.
- Melhorar carregamento com lazy loading das secoes.

### 6.2 Feedback visual em operacoes longas
- Indicadores de loading durante buscas PNCP.
- Notificacoes toast para sucesso/erro em acoes (criar fonte, importar, exportar).

### 6.3 Paginacao no frontend
- Adaptar listagem de processos para consumir o novo endpoint paginado.
- Adicionar controles de navegacao (anterior/proximo/total).

### 6.4 Filtros e busca
- Filtro por status, data e responsavel na lista de processos.
- Busca textual em itens e fontes dentro de um processo.

---

## Fase 7 — Inteligencia e Automacao

### 7.1 Sugestao automatica de termos de busca
- A partir da descricao e especificacao do item, sugerir variantes de busca para o PNCP.
- Usar sinonimos e abreviacoes comuns em compras publicas.

### 7.2 Deteccao automatica de duplicatas
- Ao importar itens ou converter rascunhos, alertar se ja existe fonte similar (por Jaccard > 0.8).
- Prevenir lancamento duplicado de mesma contratacao.

### 7.3 Enriquecimento de fontes
- Buscar dados complementares do PNCP (CNPJ fornecedor, vigencia do contrato).
- Preencher automaticamente campos como UF e municipio quando disponivel na API.

### 7.4 Score de confianca da pesquisa
- Indicador global de maturidade da pesquisa (quantidade de fontes, diversidade de UFs, cobertura de itens).
- Alertas visuais quando a pesquisa esta incompleta.

---

## Fase 8 — Multi-usuario e Colaboracao

### 8.1 Autenticacao multi-usuario
- Tabela de usuarios com hash bcrypt.
- Roles basicos: admin, analista, consulta.
- Sessoes independentes por usuario.

### 8.2 Auditoria de acoes
- Registrar quem criou/editou/excluiu cada recurso.
- Historico de alteracoes por processo.

### 8.3 Compartilhamento de processos
- Permitir que um processo seja acessado por mais de um usuario.
- Controle de permissao por processo (dono, colaborador, leitor).

---

## Fase 9 — Integracao e Ecossistema

### 9.1 API publica documentada
- Gerar documentacao OpenAPI/Swagger acessivel em `/docs`.
- Versionamento de API (`/v1/processos`).

### 9.2 Integracao com Hermes
- Sincronizar dados de pesquisa entre Icaro e Hermes via API.
- Unificar autenticacao no ecossistema AtlasNex.

### 9.3 Webhooks e notificacoes
- Notificar via webhook quando um processo atinge checklist completo.
- Integracao com email ou Teams/Slack para alertas.

### 9.4 Importacao de dados externos
- Importar tabelas de precos de referencia (painel de precos, bancos de precos estaduais).
- Suporte a fontes alem do PNCP (ComprasNet legado, portais estaduais).

---

## Fase 10 — Escalabilidade e Producao

### 10.1 Migrar para PostgreSQL
- Substituir SQLite por PostgreSQL para suportar concorrencia e volume.
- Manter SQLite como opcao para desenvolvimento local.

### 10.2 Cache de consultas PNCP
- Cachear resultados de busca por TTL (ex: 24h) para reduzir chamadas externas.
- Invalidar cache quando parametros mudam.

### 10.3 Containerizacao
- Adicionar `Dockerfile` e `docker-compose.yml`.
- Facilitar deploy em qualquer infraestrutura.

### 10.4 Monitoramento
- Integrar com Sentry ou similar para captura de erros.
- Metricas de uso (processos criados/dia, buscas PNCP/dia).

---

## Prioridade sugerida

| Fase | Impacto | Esforco | Recomendacao |
|------|---------|---------|-------------|
| 5 — Robustez | Alto | Baixo | Fazer primeiro |
| 6 — UX | Alto | Medio | Fazer em seguida |
| 7 — Inteligencia | Medio | Medio | Diferencial competitivo |
| 8 — Multi-usuario | Alto | Alto | Necessario para escalar |
| 9 — Integracao | Medio | Alto | Quando ecossistema crescer |
| 10 — Escalabilidade | Alto | Alto | Quando volume justificar |

---

## Criterios para avancar de fase

- Todos os testes da fase anterior passando.
- Lint limpo (`ruff check` sem erros).
- CI verde no GitHub Actions.
- README e CHANGELOG atualizados.
- Nenhum dado sensivel exposto no repositorio.
