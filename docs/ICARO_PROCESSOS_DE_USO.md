# Icaro GovLab AtlasNex

## Processos de uso passo a passo

Este documento detalha os processos operacionais de uso do Icaro, do acesso inicial até a exportação dos relatórios. O objetivo é servir como roteiro para equipe de compras, setor demandante, controle interno, consultorias e implantação do Icaro GovLab.

O Icaro apoia a instrução administrativa. Ele não substitui a análise técnica, jurídica, orçamentária ou de controle interno.

---

## 1. Visão geral do fluxo

```text
1. Acessar o sistema
2. Usar a aba Visão geral como painel de comando
3. Criar ou selecionar uma pesquisa
4. Cadastrar a cesta de itens
5. Buscar referências no PNCP
6. Salvar resultados como rascunhos
7. Converter rascunhos em fontes de preço
8. Inserir fontes manuais, se necessário
9. Revisar cálculos e comparabilidade
10. Registrar atas, quando aplicável
11. Conferir checklist e pendências
12. Exportar relatórios
13. Arquivar evidências no processo
```

---

## 2. Processo 1: acesso ao Icaro

### Objetivo

Abrir o ambiente local do Icaro e confirmar que o sistema está pronto para uso.

### Entrada necessária

- computador com o projeto instalado;
- servidor local iniciado;
- navegador web.

### Passo a passo

1. Abra a pasta do projeto.
2. Execute o arquivo `INICIAR_ICARO.bat`.
3. Aguarde o servidor iniciar.
4. Acesse o painel principal:

```text
http://127.0.0.1:8100/
```

5. Opcionalmente, acesse a landing institucional:

```text
http://127.0.0.1:8100/landing
```

6. Para acessar o portal da marca-mãe AtlasNex:

```text
http://127.0.0.1:8100/atlasnex
```

### Saída esperada

Painel do Icaro carregado no navegador.

### Organização da tela

O painel é dividido em abas:

| Aba | Uso principal |
| --- | --- |
| Visão geral | painel de comando, métricas e atalhos |
| Pesquisa | criação e seleção da pesquisa |
| Itens | cadastro, importação e seleção da cesta |
| PNCP | consulta ao PNCP e rascunhos salvos |
| Fontes | lançamento de fontes e memória de cálculo |
| Atas | registro de atas e análise de carona |
| Revisão | checklist, comparabilidade e revisão final |
| Relatórios | exportações MD, DOCX, HTML e XLSX |

### Cuidados

- Se a página não abrir, confirme se o servidor está rodando.
- Se a porta `8100` estiver ocupada, o servidor pode não iniciar corretamente.
- Os dados locais ficam no banco SQLite do projeto.

---

## 3. Processo 2: criar uma pesquisa de mercado

### Objetivo

Criar o processo principal que agrupará itens, fontes, rascunhos PNCP, atas, cálculos e relatórios.

### Quando usar

Sempre que houver uma nova contratação, cesta de itens, demanda administrativa ou estudo de preços.

### Entrada necessária

- título da pesquisa;
- objeto geral;
- responsável;
- local de entrega ou execução, se houver;
- categoria ou família de contratação, se houver.

### Passo a passo

1. No painel, localize a área **Nova pesquisa de mercado**.
2. Preencha o **título da pesquisa**.
3. Preencha o **objeto geral**.
4. Informe categoria, unidade, quantidade, local e responsável, quando aplicável.
5. Clique em **Criar pesquisa**.
6. Confirme se a pesquisa aparece como ativa na base atual.

### Exemplo

```text
Título: Pesquisa de preços para aquisição de equipamentos de informática
Objeto geral: Aquisição de processadores, memórias, SSDs e periféricos para modernização do parque tecnológico
Responsável: Setor de Compras
Local: Município/UF
```

### Saída esperada

Pesquisa criada e pronta para receber itens.

### Cuidados

- O objeto geral deve ser claro, mas não precisa repetir a descrição completa de todos os itens.
- Use um título que permita identificar o processo depois.

---

## 4. Processo 3: selecionar uma pesquisa existente

### Objetivo

Retomar uma pesquisa já criada.

### Passo a passo

1. Localize a área **Base atual**.
2. Clique na pesquisa desejada.
3. Confirme se os itens, fontes e métricas foram carregados.
4. Use **Atualizar** se a lista parecer desatualizada.

### Saída esperada

Pesquisa selecionada e contexto carregado para edição.

### Cuidados

- Antes de cadastrar item ou fonte, confirme se a pesquisa correta está ativa.
- Evite lançar fontes em pesquisa errada.

---

## 5. Processo 4: cadastrar itens manualmente

### Objetivo

Montar a cesta de itens da pesquisa.

### Entrada necessária

- código do item, se houver;
- descrição;
- unidade de medida;
- quantidade;
- categoria;
- termo de busca PNCP;
- especificação complementar.

### Passo a passo

1. Vá até a seção de **Itens**.
2. Preencha o **código**, se o órgão utilizar numeração interna.
3. Preencha a **descrição do item**.
4. Informe **unidade** e **quantidade**.
5. Preencha a **categoria**, se houver.
6. Informe o **termo de busca PNCP**.
7. Acrescente **especificação complementar**, se necessário.
8. Clique em **Adicionar item**.
9. Verifique se o item entrou na cesta.

### Exemplo

```text
Código: 001
Descrição: Processador para computador desktop, no mínimo 6 núcleos, compatível com placa-mãe padrão institucional
Unidade: unidade
Quantidade: 20
Categoria: informática
Termo de busca PNCP: processador
Especificação: informar geração, soquete, frequência mínima e compatibilidade quando houver
```

### Saída esperada

Item salvo na cesta da pesquisa.

### Cuidados

- A descrição do item influencia a comparação com resultados do PNCP.
- O termo de busca deve ser mais curto que a descrição, mas representativo.
- Evite termo genérico demais, como “material” ou “serviço”.

---

## 6. Processo 5: importar itens em lote

### Objetivo

Cadastrar vários itens de uma só vez.

### Entrada necessária

Lista de itens em linhas, com campos separados por ponto e vírgula.

### Formato recomendado

```text
codigo;descricao;unidade;quantidade;categoria
```

### Exemplo

```text
001;processador para computador desktop;unidade;20;informatica
002;memoria RAM DDR4 8GB;unidade;40;informatica
003;SSD 480GB SATA;unidade;30;informatica
```

### Passo a passo

1. Copie a lista de itens.
2. Cole no campo de importação em lote.
3. Revise se cada item está em uma linha.
4. Clique em **Importar linhas**.
5. Confira a cesta gerada.
6. Ajuste manualmente itens que ficaram incompletos.

### Saída esperada

Vários itens cadastrados na pesquisa.

### Cuidados

- Não use quebras de linha dentro da descrição.
- Revise quantidades após importar.
- Depois da importação, ajuste termos de busca PNCP quando necessário.

---

## 7. Processo 6: selecionar item de trabalho

### Objetivo

Definir qual item será usado como referência para busca PNCP e lançamento de fontes.

### Passo a passo

1. Na cesta, clique no item desejado.
2. Confirme se ele ficou destacado.
3. Verifique o identificador do item ativo.
4. Use o botão **PNCP** ao lado do item para iniciar a busca contextual.

### Saída esperada

Item selecionado para pesquisa, rascunhos e fontes.

### Cuidados

- Sempre confirme o item ativo antes de salvar rascunho ou fonte.
- Em cestas grandes, trabalhe item por item.

---

## 8. Processo 7: consultar o PNCP

### Objetivo

Buscar contratações publicadas no PNCP que possam servir como referência de preço ou contexto.

### Entrada necessária

- termo de busca;
- texto de referência;
- intervalo de datas;
- UF, se aplicável;
- modalidade, se aplicável;
- quantidade de resultados.

### Passo a passo

1. Clique no botão **PNCP** ao lado do item da cesta.
2. Revise o campo **Termo enviado ao PNCP**.
3. Revise o campo **Texto de referência**.
4. Informe **data inicial** e **data final** no formato `AAAAMMDD`, se quiser restringir o período.
5. Informe **UF**, se quiser limitar por estado.
6. Informe **modalidade PNCP**, se quiser filtrar.
7. Clique em **Buscar PNCP**.
8. Aguarde os resultados.
9. Analise objeto, órgão, modalidade, situação, valor estimado, publicação e similaridade.

### Modalidades aceitas

O campo pode receber o código ou o nome comum:

| Modalidade | Código PNCP usado |
| --- | --- |
| Concorrência | `1` |
| Concorrência Eletrônica | `2` |
| Concurso | `4` |
| Leilão | `5` |
| Pregão ou Pregão Eletrônico | `6` |
| Pregão Presencial | `7` |
| Dispensa | `8` |
| Inexigibilidade | `9` |
| Credenciamento | `12` |

### Exemplo de busca

```text
Termo: processador
Data inicial: 20250601
Data final: 20260401
Modalidade: Pregão
Resultados por consulta: 14
```

### Saída esperada

Lista de contratações PNCP relacionadas ao termo pesquisado.

### Cuidados

- A API do PNCP pode oscilar ou responder lentamente.
- Se ocorrer timeout, tente novamente depois ou reduza filtros.
- Se não houver resultado, simplifique o termo.
- O valor retornado pelo PNCP pode ser valor total da contratação, não necessariamente valor unitário.
- A similaridade é apoio textual, não decisão automática.

---

## 9. Processo 8: analisar resultados PNCP

### Objetivo

Selecionar resultados que possam ser úteis para a pesquisa.

### Critérios de análise

Verifique:

- se o objeto é comparável ao item;
- se a unidade de medida é compatível;
- se a quantidade faz sentido;
- se o valor parece unitário ou total;
- se o órgão e a localidade são relevantes;
- se a contratação está dentro do período desejado;
- se a modalidade é adequada ao contexto;
- se há link ou origem rastreável.

### Passo a passo

1. Leia o objeto do resultado.
2. Compare com a descrição do item da cesta.
3. Verifique a similaridade apresentada.
4. Abra a URL da fonte, se disponível.
5. Confirme a origem do valor.
6. Se o resultado for promissor, clique em **Rascunho fonte**.
7. Se o resultado não for útil, ignore ou busque outro termo.

### Saída esperada

Resultados promissores separados para tratamento como rascunho.

### Cuidados

- Não transforme automaticamente todo resultado PNCP em fonte aproveitada.
- Use rascunho como etapa intermediária de revisão.
- Justifique descartes quando um resultado foi analisado e recusado.

---

## 10. Processo 9: salvar rascunho PNCP

### Objetivo

Guardar um resultado PNCP antes de decidir se ele será fonte de preço.

### Quando usar

Use quando o resultado parece relevante, mas ainda precisa de conferência.

### Passo a passo

1. Na tabela de resultados PNCP, clique em **Rascunho fonte**.
2. Confirme se o resultado foi vinculado ao item correto.
3. Revise objeto, órgão, unidade, modalidade, valor e URL.
4. Mantenha o rascunho como pendente até a análise final.

### Saída esperada

Rascunho PNCP salvo e disponível para revisão.

### Cuidados

- Rascunho não é fonte definitiva.
- Rascunho precisa ser convertido ou descartado.
- Evite acumular rascunhos sem decisão.

---

## 11. Processo 10: converter rascunho em fonte de preço

### Objetivo

Transformar um rascunho PNCP validado em fonte de preço para cálculo.

### Entrada necessária

- rascunho PNCP;
- valor unitário validado;
- decisão sobre aproveitamento;
- observações ou justificativas.

### Passo a passo

1. Abra a área de rascunhos PNCP.
2. Localize o rascunho desejado.
3. Confira o objeto da contratação.
4. Verifique se o valor é unitário ou total.
5. Se necessário, calcule o valor unitário correto.
6. Informe o **valor unitário**.
7. Marque se a fonte será **aproveitada**.
8. Registre observações.
9. Converta o rascunho em fonte.
10. Confira se a fonte aparece na lista de fontes.

### Saída esperada

Fonte de preço criada e vinculada ao item.

### Cuidados

- Nunca use valor total como unitário sem verificar.
- Se a unidade de medida for incompatível, não aproveite sem justificativa técnica.
- Guarde observações sobre ajustes de valor.

---

## 12. Processo 11: lançar fonte manual

### Objetivo

Registrar fonte de preço que não veio diretamente do rascunho PNCP.

### Exemplos de fontes

- fornecedor;
- painel de preços;
- mídia especializada;
- ata de registro de preços;
- contratação similar;
- fonte oficial local;
- outro banco público.

### Passo a passo

1. Vá para a seção **Fontes de preço**.
2. Selecione o item da cesta.
3. Escolha o tipo da fonte.
4. Informe descrição do item encontrado.
5. Informe valor unitário.
6. Informe quantidade, se aplicável.
7. Preencha órgão, fornecedor, UF, município e URL.
8. Informe data de referência.
9. Marque se a fonte será aproveitada no cálculo.
10. Se não for aproveitada, registre justificativa.
11. Salve a fonte.

### Saída esperada

Fonte manual registrada no processo.

### Cuidados

- Fonte sem URL ou evidência precisa de justificativa documental.
- Sempre diferencie fonte aproveitada de fonte descartada.
- O valor unitário deve ser comparável ao item da cesta.

---

## 13. Processo 12: revisar cálculo de preço

### Objetivo

Conferir os valores coletados e a memória de cálculo.

### Passo a passo

1. Vá para **Fontes e cálculo**.
2. Confira as fontes aproveitadas.
3. Verifique valores unitários.
4. Clique em **Recalcular**, se necessário.
5. Analise média, mediana, menor preço e eventuais alertas.
6. Verifique se há valores extremos.
7. Decida se algum valor deve ser descartado.
8. Registre justificativa para descarte.

### Saída esperada

Preço estimado por item revisado.

### Cuidados

- A mediana costuma reduzir impacto de valores extremos, mas a metodologia deve ser justificada.
- Valores inexequíveis, excessivos ou incompatíveis devem ser tratados.
- O Icaro calcula; a equipe decide e justifica.

---

## 14. Processo 13: registrar ata de registro de preços

### Objetivo

Registrar ata para análise de aderência ou estudo de carona.

### Entrada necessária

- número da ata;
- órgão gerenciador;
- fornecedor;
- objeto;
- item;
- valor;
- vigência;
- URL;
- observações.

### Passo a passo

1. Vá para a seção **Atas de registro de preços**.
2. Informe número e órgão gerenciador.
3. Informe fornecedor.
4. Descreva objeto e item.
5. Informe valor, quantidade e vigência.
6. Registre URL ou fonte.
7. Classifique aderência, se aplicável.
8. Salve a ata.
9. Use as informações no relatório e na análise de viabilidade de adesão.

### Saída esperada

Ata registrada para análise administrativa.

### Cuidados

- Verifique vigência.
- Confira regras do ente sobre adesão.
- Avalie compatibilidade de objeto, quantidade, local e preço.

---

## 15. Processo 14: conferir checklist

### Objetivo

Identificar pendências administrativas antes da exportação.

### Passo a passo

1. Acesse a área **Checklist**.
2. Leia cada item apontado.
3. Verifique pendências de fontes, itens ou justificativas.
4. Corrija dados ausentes.
5. Reavalie fontes e rascunhos.
6. Atualize a pesquisa.

### Saída esperada

Lista de pendências reduzida ou resolvida.

### Cuidados

- Checklist é apoio, não parecer.
- Pendências podem exigir análise fora do sistema.

---

## 16. Processo 15: avaliar comparabilidade

### Objetivo

Verificar se as fontes são comparáveis ao item pesquisado.

### Critérios observados

- semelhança textual;
- aderência ao objeto;
- aproveitamento da fonte;
- desvio em relação à mediana;
- localidade;
- coerência geral.

### Passo a passo

1. Vá para a área **Comparabilidade**.
2. Analise o score por item ou fonte.
3. Identifique fontes com baixa aderência.
4. Revise descrição, unidade e valor.
5. Decida manter, corrigir ou descartar.
6. Registre justificativa.

### Saída esperada

Conjunto de fontes mais defensável.

### Cuidados

- Similaridade textual baixa não significa descarte automático.
- Similaridade alta não garante compatibilidade técnica.
- Use julgamento técnico e documentação.

---

## 17. Processo 16: revisão final por item

### Objetivo

Garantir que cada item da cesta esteja minimamente instruído.

### Passo a passo

1. Abra a revisão final.
2. Verifique item por item.
3. Confira número de fontes aproveitadas.
4. Veja se há rascunhos pendentes.
5. Verifique se há outliers.
6. Confira se o termo de busca PNCP está preenchido.
7. Corrija pendências.
8. Só avance para exportação quando os itens principais estiverem revisados.

### Saída esperada

Itens classificados como prontos, parciais ou pendentes.

### Cuidados

- Itens com menos fontes podem exigir justificativa.
- Rascunhos pendentes devem ser decididos.
- Documente limitações da pesquisa.

---

## 18. Processo 17: exportar relatório

### Objetivo

Gerar documentos para instrução, revisão e arquivamento.

### Formatos disponíveis

| Formato | Uso recomendado |
| --- | --- |
| Markdown | revisão técnica e edição simples |
| HTML | visualização e impressão pelo navegador |
| DOCX | documento editável para processo |
| XLSX | planilha de apoio e memória de dados |

### Passo a passo

1. Vá para a seção **Relatórios**.
2. Escolha o formato desejado.
3. Clique no botão de exportação.
4. Aguarde a geração.
5. Abra o arquivo exportado.
6. Revise conteúdo, fontes e valores.
7. Anexe ao processo administrativo, conforme rotina do órgão.

### Saída esperada

Arquivo gerado na pasta `output/`.

### Cuidados

- Revise o DOCX antes de protocolar.
- Confirme se todas as fontes aparecem corretamente.
- Verifique se valores e datas estão coerentes.

---

## 19. Processo 18: tratar erros comuns

### Erro: Falha ao consultar PNCP 400

Possíveis causas:

- modalidade enviada em formato inválido;
- data em formato incorreto;
- tamanho de página fora do limite aceito pela API;
- parâmetro rejeitado pelo PNCP.

Como resolver:

1. Use datas no formato `AAAAMMDD`.
2. Use modalidade por nome comum ou código.
3. Mantenha resultados por consulta com valor mínimo `10`.
4. Tente sem filtro de modalidade.
5. Simplifique o termo.

### Erro: timeout no PNCP

Possíveis causas:

- instabilidade da API externa;
- consulta muito ampla;
- lentidão momentânea da rede.

Como resolver:

1. Tente novamente depois.
2. Reduza o período.
3. Use termo mais específico.
4. Remova filtros opcionais.
5. Registre a limitação, se necessário.

### Erro: nenhum resultado encontrado

Como resolver:

1. Simplifique o termo.
2. Remova marcas ou detalhes excessivos.
3. Amplie o período.
4. Pesquise por categoria do objeto.
5. Ative buscas auxiliares.
6. Faça busca manual complementar em outras fontes.

### Erro: fonte com valor estranho

Como resolver:

1. Verifique se o valor é total ou unitário.
2. Confira quantidade e unidade.
3. Abra a fonte original.
4. Ajuste o valor unitário.
5. Registre observação.
6. Descarte se a fonte não for comparável.

---

## 20. Processo 19: rotina recomendada para uma pesquisa real

### Dia 1: preparação

1. Criar pesquisa.
2. Cadastrar itens.
3. Revisar descrições.
4. Definir termos de busca.

### Dia 2: coleta

1. Buscar PNCP item por item.
2. Salvar rascunhos relevantes.
3. Registrar fontes manuais complementares.
4. Abrir links de evidência.

### Dia 3: saneamento

1. Converter rascunhos.
2. Corrigir valores unitários.
3. Descartar fontes inadequadas.
4. Registrar justificativas.

### Dia 4: análise

1. Recalcular preços.
2. Avaliar comparabilidade.
3. Verificar outliers.
4. Conferir checklist.

### Dia 5: fechamento

1. Revisar item por item.
2. Exportar DOCX e XLSX.
3. Revisar relatório.
4. Anexar evidências.
5. Encaminhar para validação interna.

---

## 21. Papéis sugeridos

| Papel | Responsabilidade no Icaro |
| --- | --- |
| Setor demandante | descrever necessidade e especificação |
| Compras | cadastrar pesquisa, buscar fontes e montar relatório |
| Agente de contratação | revisar coerência do processo |
| Controle interno | verificar pendências, riscos e rastreabilidade |
| Jurídico | analisar conformidade jurídica fora do sistema |
| Gestor | validar estratégia e decisão administrativa |

---

## 22. Boas práticas

1. Trabalhe por item, não apenas por objeto geral.
2. Salve rascunhos antes de criar fontes definitivas.
3. Confira valor unitário sempre.
4. Justifique descartes.
5. Use mais de uma fonte quando possível.
6. Não confie apenas na similaridade automática.
7. Preserve URLs e datas de referência.
8. Exporte relatório e planilha ao final.
9. Revise o documento antes de anexar ao processo.
10. Mantenha backup do banco local.

---

## 23. Entregáveis finais da pesquisa

Ao concluir uma pesquisa, recomenda-se manter:

- relatório DOCX;
- relatório HTML ou PDF gerado pelo navegador;
- planilha XLSX;
- memória de fontes;
- justificativas de descarte;
- evidências de URLs consultadas;
- atas analisadas, se houver;
- checklist final;
- observações da equipe.

---

## 24. Conexão com AtlasNex

O Icaro GovLab é uma solução AtlasNex.

Use o portal AtlasNex para apresentação institucional:

```text
http://127.0.0.1:8100/atlasnex
```

Use a landing Icaro GovLab para apresentação comercial:

```text
http://127.0.0.1:8100/landing
```

Use o painel Icaro para operação:

```text
http://127.0.0.1:8100/
```

---

## 25. Resumo executivo do processo

O uso ideal do Icaro segue uma lógica simples:

```text
Criar pesquisa
  -> cadastrar itens
  -> buscar PNCP
  -> salvar rascunhos
  -> validar fontes
  -> calcular preços
  -> revisar riscos
  -> exportar relatório
```

O valor do sistema está em tornar esse caminho rastreável, repetível e defensável.
