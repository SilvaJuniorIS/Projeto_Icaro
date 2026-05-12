# Plano de produto - Icaro

## Proposta

O Icaro sera uma ferramenta para apoiar a pesquisa de mercado por cesta de itens, com foco em buscar precos praticados no PNCP, parametrizar fontes por item e gerar relatorio administrativo de pesquisa de precos.

## Publico-alvo

- Setores de compras.
- Comissoes de contratacao.
- Pregoeiros e agentes de contratacao.
- Controle interno.
- Secretarias demandantes.
- Consultorias que apoiam municipios e entidades publicas.

## Problema

Processos preparatorios costumam sofrer com:

- pesquisa de precos pouco documentada por item;
- dificuldade para encontrar contratacoes comparaveis no PNCP;
- perda da origem dos valores coletados;
- uso fragil de fontes;
- ausencia de memoria de calculo clara;
- dificuldade de justificar descartes;
- risco de questionamento por tribunal de contas;
- retrabalho na montagem do processo administrativo.

## MVP

### 1. Cadastro da pesquisa e cesta de itens

Campos:

- titulo da pesquisa;
- descricao geral do objeto;
- lista de itens;
- codigo, descricao, unidade e quantidade por item;
- termo de busca PNCP por item;
- local de entrega/execucao;
- observacoes tecnicas.

### 2. Pesquisa PNCP

Funcionalidades:

- buscar licitacoes/contratacoes por termo de cada item;
- filtrar por periodo, UF, modalidade e situacao;
- vincular fontes encontradas ao item pesquisado;
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

- media por item;
- mediana por item;
- menor preco valido por item;
- intervalo de confianca simples;
- alerta de outlier;
- memoria de calculo.

### 5. Relatorio

Saidas:

- relatorio de pesquisa de mercado por item;
- quadro comparativo;
- justificativa metodologica;
- lista de fontes e origem dos valores;
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
