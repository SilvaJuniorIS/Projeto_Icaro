# Plano de produto - Icaro

## Proposta

O Icaro sera uma ferramenta para apoiar a elaboracao da fase preparatoria de licitacoes, com foco em pesquisa de precos, atas de registro de precos e organizacao documental do processo.

## Publico-alvo

- Setores de compras.
- Comissoes de contratacao.
- Pregoeiros e agentes de contratacao.
- Controle interno.
- Secretarias demandantes.
- Consultorias que apoiam municipios e entidades publicas.

## Problema

Processos preparatorios costumam sofrer com:

- pesquisa de precos pouco documentada;
- dificuldade para encontrar contratacoes comparaveis;
- uso fragil de fontes;
- ausencia de memoria de calculo clara;
- dificuldade de justificar descartes;
- risco de questionamento por tribunal de contas;
- retrabalho na montagem do processo administrativo.

## MVP

### 1. Cadastro do objeto

Campos:

- descricao do objeto;
- categoria;
- unidade de fornecimento;
- quantidade pretendida;
- local de entrega/execucao;
- prazo esperado;
- observacoes tecnicas.

### 2. Pesquisa PNCP

Funcionalidades:

- buscar licitacoes/contratacoes por palavra-chave;
- filtrar por periodo, UF, modalidade e situacao;
- marcar fontes como aproveitadas ou descartadas;
- registrar justificativa do descarte.

### 3. Pesquisa de atas

Funcionalidades:

- localizar atas possivelmente vigentes;
- extrair orgao gerenciador, fornecedor, item, preco, vigencia e quantidade;
- classificar aderencia ao objeto;
- gerar checklist de carona.

### 4. Calculo de preco estimado

Funcionalidades:

- media;
- mediana;
- menor preco valido;
- intervalo de confianca simples;
- alerta de outlier;
- memoria de calculo.

### 5. Relatorio

Saidas:

- relatorio de pesquisa de precos;
- quadro comparativo;
- justificativa metodologica;
- lista de fontes;
- lista de descartes;
- anexos.

## Roadmap

### Fase 1 - Fundacao

- Estrutura do projeto.
- Modelo de dados.
- Dashboard demo.
- Documento normativo inicial.
- Templates de relatorio.

### Fase 2 - Coleta

- Cliente PNCP.
- Busca por atas.
- Normalizacao de itens.
- Persistencia local.

### Fase 3 - Analise

- Motor de comparabilidade.
- Score de aderencia do objeto.
- Calculos de preco estimado.
- Tratamento de valores extremos.

### Fase 4 - Processo

- Geracao de relatorio em DOCX/PDF.
- Exportacao XLSX.
- Checklist administrativo.
- Fluxo por processo.

## Nome e identidade

Icaro sugere voo, planejamento e visao ampla. A identidade deve ser administrativa, clara e confiavel, menos comercial que o Hermes.
