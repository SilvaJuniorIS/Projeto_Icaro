# Projeto Icaro

Ferramenta de apoio administrativo para a fase preparatoria de licitacoes.

O Icaro nasce como projeto paralelo ao Hermes. Enquanto o Hermes olha para oportunidades comerciais, o Icaro olha para o lado da Administracao: formacao do processo, pesquisa de precos, busca de atas ativas para possivel adesao e organizacao da evidencia documental.

## Objetivo

Apoiar equipes de compras, planejamento e licitacoes na elaboracao de processos preparatorios com maior rastreabilidade, padronizacao e seguranca tecnica.

## Modulos previstos

1. **Pesquisa de precos**
   - Busca de licitacoes e contratacoes similares no PNCP.
   - Agrupamento por item, unidade, quantidade e localidade.
   - Memoria de calculo com media, mediana e tratamento de valores extremos.
   - Registro das fontes consultadas e justificativas.

2. **Atas e caronas**
   - Busca de atas de registro de precos vigentes.
   - Verificacao inicial de aderencia do objeto.
   - Controle de vigencia, fornecedor, orgao gerenciador e quantitativos.
   - Checklist para adesao, conforme regras aplicaveis.

3. **Processo preparatorio**
   - Checklist de documentos.
   - Minutas e modelos de justificativa.
   - Organizacao do estudo tecnico preliminar, termo de referencia e pesquisa de mercado.

4. **Relatorio administrativo**
   - Relatorio de pesquisa de precos.
   - Quadro comparativo.
   - Justificativa da metodologia.
   - Registro de descartes de valores inconsistentes, inexequiveis ou excessivos.

## Referencias iniciais

- Lei nº 14.133/2021, especialmente art. 23.
- IN SEGES/ME nº 65/2021, sobre pesquisa de precos.
- Decreto nº 11.462/2023, sobre sistema de registro de precos.
- Orientacoes e jurisprudencia dos Tribunais de Contas aplicaveis ao ente contratante.

## Estado atual

MVP local inicial. Ja existem API FastAPI, banco SQLite, cadastro de processos, lancamento manual de fontes de preco, calculo de media/mediana e dashboard operacional.

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
```

## Estrutura

```text
Projeto_Icaro/
  config/
  data/
  docs/
  output/
  src/
  api.py
  dashboard.html
  requirements.txt
  INICIAR_ICARO.bat
  README.md
  PLANO_PRODUTO_ICARO.md
  REFERENCIAS_NORMATIVAS.md
```
