# Manual do usuario — Icaro

Versao alinhada ao MVP local (FastAPI + SQLite + painel web). Publico: compras, comissoes de contratacao, pregoeiros, controle interno e consultorias.

---

## 1. O que e o Icaro

O **Icaro** apoia a **pesquisa de mercado por cesta de itens**, com:

- cadastro de **pesquisa** (objeto geral, local, responsavel);
- **itens** com descricao, unidade, quantidade e termo de busca no PNCP;
- **consulta ao PNCP** com ordenacao por **similaridade** em relacao ao texto do item;
- **fontes de preco** vinculadas ao item, com URL, orgao, valor e flag de uso no calculo;
- **atas** de registro de precos (registro manual para analise de carona);
- **checklist** e **comparabilidade** das fontes;
- **exportacao** em Markdown, HTML, DOCX e XLSX.

O software **nao substitui** o juizo do ordenador nem a analise juridica; documenta metodo, fontes e descartes para o processo administrativo.

---

## 2. Instalacao e acesso

### 2.1 Windows (recomendado)

Execute `INICIAR_ICARO.bat` na raiz do projeto, ou:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn api:app --host 127.0.0.1 --port 8100
```

### 2.2 Enderecos uteis

| Pagina | URL |
|--------|-----|
| Painel principal do Icaro | `http://127.0.0.1:8100/` |
| Hub AtlasNex (portal) | `http://127.0.0.1:8100/atlasnex` |
| Manual (Markdown) | `http://127.0.0.1:8100/icaro-docs/MANUAL_ICARO.md` |
| API (documentacao automatica) | `http://127.0.0.1:8100/docs` |

Dados gravados em SQLite em `data/icaro.sqlite3`. Exportacoes em `output/`.

---

## 3. Fluxo de trabalho sugerido

1. **Criar ou selecionar uma pesquisa** na lista "Base atual".
2. **Cadastrar itens** (formulario ou importacao em lote).
3. Para cada item relevante: **Busca PNCP** (botao "PNCP" ao lado do item preenche termo e texto de referencia).
4. **Lancar fontes** a partir dos resultados ("Rascunho fonte") ou digitacao manual; ajustar **valor unitario** quando o PNCP trouxer valor total da contratacao.
5. Opcional: **registrar atas** para estudo de carona.
6. Revisar **checklist** e **comparabilidade**.
7. **Exportar** relatorio e planilha.

---

## 4. Pesquisa de mercado (processo)

No bloco **Nova pesquisa de mercado**:

- **Titulo da pesquisa**: identificacao curta (ex.: "Cesta material escritorio 2026").
- **Objeto geral**: finalidade e familia de bens ou servicos.
- **Categoria, unidade, quantidade, local, responsavel**: campos auxiliares para contexto e comparabilidade.

Clique em **Criar pesquisa**. O sistema passa a usar essa pesquisa como ativa e sugere a secao **Itens**.

Na lista **Base atual**, clique numa pesquisa para ativa-la. Use **Atualizar** para recarregar a lista.

---

## 5. Itens da cesta

### 5.1 Inclusao manual

- **Codigo**: identificador interno (ex.: 001).
- **Descricao do item**: texto fiel ao objeto licitado; alimenta similaridade na busca PNCP.
- **Unidade / quantidade / categoria**: conforme TR ou ETP.
- **Termo de busca PNCP**: se vazio, o sistema pode usar trechos da descricao na busca.
- **Especificacao complementar**: marca, padrao, embalagem, etc.

**Adicionar item** grava o item na pesquisa ativa.

### 5.2 Selecao de item

Na **Cesta**, clique num item para seleciona-lo (destaque azul). O selo "Item #..." indica o item ativo para PNCP e para vinculo de fonte.

### 5.3 Importacao em lote

Uma linha por item, formato:

```text
codigo;descricao;unidade;quantidade;categoria
```

Exemplo:

```text
001;papel A4 sulfite 75g;resma;10;consumo
002;toner preto compativel HP;unidade;4;informatica
```

Cole no campo de importacao e clique em **Importar linhas**. O termo de busca inicial sera a descricao de cada linha.

---

## 6. Busca PNCP (contextual)

### 6.1 Campos principais

- **Item da cesta (opcional)**: preenche termo e texto de referencia a partir do cadastro.
- **Termo enviado ao PNCP**: texto da consulta `q` na API publica de contratacoes.
- **Texto de referencia**: descricao (e especificacao) usada para **ordenar** resultados por **similaridade lexical** (Jaccard em tokens) e para gerar **consultas auxiliares** opcionais.
- **Datas**: formato **AAAAMMDD** (ex.: 20251101). Vazio usa janela padrao do backend.
- **Resultados por consulta** / **Consultas combinadas**: limitam volume e numero de variantes de busca.
- **Incluir buscas auxiliares**: dispara consultas adicionais com palavras-chave derivadas da referencia; resultados sao **unificados** e deduplicados.

### 6.2 Botao PNCP na cesta

Ao lado de cada item, **PNCP** seleciona o item, preenche o formulario da busca e rola ate a secao. Revise termo e referencia e clique em **Buscar PNCP**.

### 6.3 Resultados

A coluna **Similaridade** indica proximidade do **objeto** da contratacao ao texto de referencia (referencia administrativa, nao juizo de idoneidade automatica).

**Rascunho fonte** copia dados para o formulario de fonte e leva ate **Fontes**. **Confira sempre** se o valor e **unitario** ou **total** da contratacao.

---

## 7. Fontes de preco

- **Item da cesta**: vincula a fonte ao item; pode ser "Fonte geral da pesquisa" se nao houver item.
- **Tipo da fonte**: PNCP, ata, painel, fornecedor, outro.
- **Valor unitario**: obrigatorio para calculo; deve refletir o preco unitario comparavel ao item.
- **Descricao do item encontrado**: texto da fonte (ex.: objeto PNCP).
- **Orgao, fornecedor, UF, municipio, URL, data referencia**: rastreabilidade.
- **Aproveitar no calculo?**: "Nao" exige justificativa em observacoes / descarte.

A tabela **Fontes e calculo** lista lancamentos; **Recalcular** atualiza mediana nas metricas do topo.

---

## 8. Atas de registro de precos

Registro **manual** para acompanhamento de **carona**: numero, orgao gerenciador, fornecedor, objeto, item, valores, vigencias, URL, aderencia e observacoes. A segunda tabela resume atas cadastradas.

---

## 9. Checklist e comparabilidade

- **Checklist**: itens do processo preparatorio com status OK / pendente.
- **Comparabilidade**: score por similaridade de texto, uso da fonte, desvio em relacao a mediana e coerencia com local informado na pesquisa.

Use como **apoio** a narrativa do relatorio, nao como decisao automatica.

---

## 10. Relatorios e exportacoes

Na secao **Relatorios**:

- **MD**: narrativa e dados em Markdown.
- **DOCX**: documento editavel.
- **HTML**: impressao / PDF pelo navegador.
- **XLSX**: planilha (tambem disponivel em **Fontes e calculo**).

Arquivos gerados em `output/` com nomes derivados do processo.

---

## 11. Integracao com o AtlasNex

O **AtlasNex** e o portal do ecossistema (`/atlasnex`). Por padrao os sistemas permanecem **separados** (URLs distintas ou mesma maquina em portas diferentes).

### 11.1 Abrir Icaro a partir do AtlasNex

1. Acesse `http://127.0.0.1:8100/atlasnex`.
2. Em **Integracao**, confira a **URL base do Icaro** (ex.: `http://127.0.0.1:8100`).
3. Clique em **Salvar** (gravado no `localStorage` do navegador).
4. Em **Visao geral**, use **Abrir Icaro (nova aba)**.

### 11.2 Iframe (mesma origem)

Se Icaro e AtlasNex forem publicados no **mesmo esquema, host e porta** (ex.: proxy com `/` para Icaro e `/atlasnex` para o hub), o botao **Ver aqui (iframe)** pode embutir o painel. Em origens diferentes, navegadores podem bloquear o iframe.

### 11.3 Hermes

Quando o Hermes estiver disponivel, informe a URL base em **Integracao** e use **Abrir Hermes** no cartao correspondente.

---

## 12. Boas praticas e limites

- Registrar **data de acesso** e **URL** de cada fonte sempre que possivel.
- Explicitar **descartes** e valores nao aproveitados.
- Tratar valores do PNCP como **referencia**; validar unidade de medida e quantidade.
- Consultar **IN 65/2021**, **Lei 14.133/2021** (art. 23) e normas do ente.
- Manter **backup** de `data/icaro.sqlite3` em rotinas de arquivo.

---

## 13. Resolucao de problemas

| Problema | Acao |
|----------|------|
| PNCP sem resultado | Ajuste termo, amplie datas, ative variantes ou simplifique palavras-chave. |
| Erro de rede PNCP | Verifique internet, firewall e disponibilidade da API `pncp.gov.br`. |
| Exportacao nao baixa | Confirme pesquisa selecionada e permissoes da pasta `output/`. |
| Manual nao abre no navegador | Acesse diretamente `/icaro-docs/MANUAL_ICARO.md` ou abra o arquivo em `docs/`. |

---

## 14. Contato e evolucao

Roadmap amplo em `PLANO_PRODUTO_ICARO.md`. Para integracao futura (login unico, API compartilhada, banco unico), defina arquitetura alvo com a equipe AtlasNex antes de migrar dados.
